"""Spike: measure family regexes over EVERY course of nep26-se-electrical (26 courses = 13 x 2 PDFs).
Writes docs/evidence/regex_runs/nep26-se-electrical_<name>.txt
Usage: PYTHONIOENCODING=utf-8 python spikes/nep26-se-electrical_regex_runs.py <name>
names: detect code objectives syllabus_hdr module_start tail prereq stop title selflearn"""
import re, sys, importlib, fitz, os

x = importlib.import_module("nep26-se-electrical_extract")
seg = x.seg
FAM = "nep26-se-electrical"
PDFN = {"ece": seg.PDFS["ece"], "ee": seg.PDFS["ee"]}


def allcourses():
    out = []
    for k, p in PDFN.items():
        for c in x.extract(p):
            c["pdf"] = p
            c["pk"] = k
            out.append(c)
    return out


def ln(c):
    return [(pg, t) for pg, _, t in c["lines"]]


def write(name, cmd, header, attempts):
    os.makedirs("docs/evidence/regex_runs", exist_ok=True)
    with open(f"docs/evidence/regex_runs/{FAM}_{name}.txt", "w", encoding="utf-8") as f:
        f.write(f"command: {cmd}\nscript: spikes/{FAM}_regex_runs.py\n{header}\n")
        for a in attempts:
            f.write(f"\n--- attempt {a['n']} ---\nregex: {a['regex']}\n{a.get('note','')}\n"
                    f"matched/total: {a['m']}/{a['t']}  ({a['unit']})\nfailures ({len(a['fails'])}):\n")
            for s in a["fails"]:
                f.write("  " + s + "\n")
    for a in attempts:
        print(name, "attempt", a["n"], f"{a['m']}/{a['t']}", len(a["fails"]), "fails")


def cid(c):
    return f"{os.path.basename(c['pdf'])} | {c['code']} | p{c['start_page']}"


def module_seq(c, attempt):
    lines = c["lines"]
    res = []
    started = False
    prev = ""
    for pg, xx, t in lines:
        if t.startswith("Detailed Syllabus"):
            started = True
        if started:
            if attempt == 1 and re.fullmatch(r"(I|II|III|IV|V|VI)", t):
                res.append(t)
            if attempt == 2 and re.fullmatch(r"(I|II|III|IV|V|VI)", t) and prev != "IAT-":
                res.append(t)
            if attempt == 3 and re.fullmatch(r"(I|II|III|IV|V|VI)|[1-6]", t) and prev != "IAT-" and xx < 95:
                res.append(t)
        prev = t
    return res


def titles(c, ctx=False):
    L = [(pg, t) for pg, _, t in (c["ctx"] if ctx else c["lines"])]
    T = []
    for i, (pg, tt) in enumerate(L):
        if tt == c["code"]:
            j = i + 1
            parts = []
            while j < len(L) and not re.fullmatch(r"--?|\d+|\d\*\+\d|Theory", L[j][1]):
                parts.append(L[j][1])
                j += 1
            T.append(" ".join(parts))
    return T


def run(name):
    C = allcourses()
    cmd = f"PYTHONIOENCODING=utf-8 python spikes/{FAM}_regex_runs.py {name}"
    A = []
    theory = [c for c in C if c["kind"] == "theory"]
    work = [c for c in C if c["code"].endswith("4411")]
    if name == "detect":
        for n, r in enumerate([r"As [Pp]er NEP 2020", r"^\(?As [Pp]er NEP 2020\)?$"], 1):
            m = 0
            fails = []
            for k, p in PDFN.items():
                d = fitz.open(p)
                hit = None
                for i in range(0, 8):
                    for l in d[i].get_text().split("\n"):
                        if re.search(r, l.strip()):
                            hit = (i + 1, l)
                            break
                    if hit:
                        break
                if hit:
                    m += 1
                else:
                    fails.append(f"{p} pages 1-8: no line matched")
            A.append(dict(n=n, regex=r, m=m, t=2, unit="PDFs, first 8 pages, per line .strip()", fails=fails))
        write(name, cmd, "Detect NEP 2020 text on early pages.", A)
    elif name == "code":
        for n, win in enumerate([0, 1], 1):
            r = r"^\d{7}$"
            m = 0
            fails = []
            for pk, p in PDFN.items():
                L, objs, codes, segs = seg.courses(p)
                for (s, e), code in zip(segs, codes):
                    lo = s
                    if win:
                        pg = L[s][0]
                        while lo > 0 and L[lo - 1][0] >= pg - 1:
                            lo -= 1
                    hit = any(re.match(r, t) and t == code for _, t in L[lo:e])
                    if hit:
                        m += 1
                    else:
                        fails.append(f"{p} | assigned code {code} | objective marker p{L[s][0]} line {L[s][1][:30]!r}: code line not in window")
            A.append(dict(n=n, regex=r, m=m, t=26,
                          unit="courses (13 per PDF); code = k-th distinct bare 7-digit line on pages>=16 assigned to k-th objectives marker; window=" + ("segment only" if not win else "segment + previous page"),
                          fails=fails))
        write(name, cmd, "Course code line.", A)
    elif name == "objectives":
        r = r"^(Course|Lab) [Oo]bjectives?:"
        m = 0
        fails = []
        t = 0
        for pk, p in PDFN.items():
            L, objs, codes, segs = seg.courses(p)
            t += len(codes)
            m += min(len(objs), len(codes))
            if len(objs) != len(codes):
                fails.append(f"{p}: {len(objs)} objective markers vs {len(codes)} codes")
        A = [dict(n=1, regex=r, m=m, t=t, unit="courses (total = distinct codes on pages>=16)", fails=fails)]
        write(name, cmd, "Objectives marker starts each course body.", A)
    elif name == "syllabus_hdr":
        r = r"^Detailed Syllabus:"
        m = 0
        fails = []
        for c in C:
            if any(re.match(r, t) for _, t in ln(c)):
                m += 1
            else:
                fails.append(f"{cid(c)} kind={c['kind']}: no line matched in course segment")
        A = [dict(n=1, regex=r, m=m, t=len(C), unit="courses", fails=fails,
                  note="Unmatched courses are those whose body has no 'Detailed Syllabus:' line (see doc).")]
        write(name, cmd, "", A)
    elif name == "module_start":
        T = theory + work
        regs = {1: r"^(I|II|III|IV|V|VI)$",
                2: r"^(I|II|III|IV|V|VI)$ with condition: previous line != 'IAT-'",
                3: r"^((I|II|III|IV|V|VI)|[1-6])$ with conditions: previous line != 'IAT-' AND line x0 < 95 (bbox, not line order only)"}
        for n in (1, 2, 3):
            m = 0
            fails = []
            for c in T:
                s = module_seq(c, n)
                if s in (["I", "II", "III", "IV", "V", "VI"], ["1", "2", "3", "4", "5", "6"]):
                    m += 1
                else:
                    fails.append(f"{cid(c)}: extracted {s}")
            A.append(dict(n=n, regex=regs[n], m=m, t=len(T),
                          unit="courses with a module table (14 theory + 2 Electrical Workshop); success = exactly 6 modules numbered 1..6 in order",
                          fails=fails))
        write(name, cmd, "", A)
    elif name == "tail":
        T = theory + work
        for n, r in enumerate([r"^\d{1,2}$ then next line ^CO\d$", r"^\d{1,2}$ then next line ^(CO|LO)\d$"], 1):
            pat = r"(CO)" if n == 1 else r"(CO|LO)"
            m = 0
            fails = []
            for c in T:
                L = [t for _, t in ln(c)]
                tails = [(L[i], L[i + 1]) for i in range(len(L) - 1)
                         if re.fullmatch(r"\d{1,2}", L[i]) and re.fullmatch(pat + r"\d", L[i + 1])]
                if len(tails) == 6:
                    m += 1
                else:
                    fails.append(f"{cid(c)}: {len(tails)} tails {tails}")
            A.append(dict(n=n, regex=r, m=m, t=len(T), unit="courses with a module table; success = exactly 6 hours/CO tails", fails=fails))
        write(name, cmd, "", A)
    elif name == "prereq":
        r = r"^Prerequisite$"
        m = 0
        fails = []
        for c in theory:
            if any(re.match(r, t) for _, t in ln(c)):
                m += 1
            else:
                anyword = any(re.search("(?i)prerequisite|pre-requisite", t) for _, t in ln(c))
                fails.append(f"{cid(c)}: no '^Prerequisite$' line; any case-insensitive prerequisite substring in segment: {anyword}")
        A = [dict(n=1, regex=r, m=m, t=len(theory), unit="theory courses", fails=fails,
                  note="Failures here = courses with NO prerequisite row (not a parser miss), shown verbatim.")]
        write(name, cmd, "", A)
    elif name == "stop":
        for n, r in enumerate([r"^(Text Books:|Reference Books:)", r"^(Text ?[Bb]ooks?:|Reference Books:|References:)"], 1):
            m = 0
            fails = []
            for c in theory:
                if [t for _, t in ln(c) if re.match(r, t)]:
                    m += 1
                else:
                    fails.append(f"{cid(c)}: none")
            A.append(dict(n=n, regex=r, m=m, t=len(theory), unit="theory courses", fails=fails))
        write(name, cmd, "", A)
    elif name == "title":
        r = r"after bare ^\d{7}$ line: join following lines until a line matching ^(--?|\d+|\d\*\+\d|Theory)$"
        for n, ctx in enumerate([False, True, True], 1):
            m = 0
            fails = []
            for c in C:
                T = titles(c, ctx)
                Tn = [re.sub(r"\s+", " ", a).strip() for a in T]
                if n == 3:
                    ok = len(Tn) >= 2 and Tn[0] != "" and all(Tn[0].startswith(a) for a in Tn)
                else:
                    ok = len(T) >= 2 and len(set(Tn)) == 1 and T[0]
                if ok:
                    m += 1
                else:
                    fails.append(f"{cid(c)}: titles from code occurrences = {T}")
            A.append(dict(n=n, regex=r, m=m, t=len(C),
                          unit="courses; window=" + ("segment only" if not ctx else "segment + previous page") + "; success = >=2 code occurrences in window, non-empty, all joined titles identical" + (" (attempt 3: identical OR every later title is a prefix of the first)" if n == 3 else "") + "",
                          fails=fails))
        write(name, cmd, "", A)
    elif name == "selflearn":
        A = []
        for n, r in enumerate([r"(?i)self[\s\-]*(learning|study)|\bSL\b", r"(?i)self[\s\-]*(learning|study)"], 1):
            hits = []
            for k, p in PDFN.items():
                d = fitz.open(p)
                for i, pg in enumerate(d):
                    for l in pg.get_text().split(chr(10)):
                        if re.search(r, l):
                            hits.append(f"{p} p{i+1}: {l!r}")
            A.append(dict(n=n, regex=r, m=len(hits), t=0, unit="hits over all 60 pages of both PDFs (not a coverage measure; 0 hits = marker absent)", fails=hits))
        write(name, cmd, "Self-learning/self-study marker search.", A)


if __name__ == "__main__":
    run(sys.argv[1])
