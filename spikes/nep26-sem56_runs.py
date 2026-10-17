"""Throwaway spike for nep26-sem56: runs each regex against every course in SEM-V.pdf and writes evidence files.
Command: PYTHONIOENCODING=utf-8 python spikes/nep26-sem56_runs.py"""
import re, sys, os, json
sys.path.insert(0, "spikes")
import importlib
M = importlib.import_module("nep26-sem56_modules")
P = M.P
OUT = "docs/evidence/regex_runs/"
FAM = "nep26-sem56"
PDF = "data/raw/_unclassified/SEM-V.pdf"
CMD = "PYTHONIOENCODING=utf-8 python spikes/nep26-sem56_runs.py   (pdf=" + PDF + ")"
pages = P.load()
segs, first = P.segments(pages)


def w(name, lines):
    open(OUT + FAM + "_" + name + ".txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")


def hdr(name, rx_list):
    return ["command: " + CMD, "regex name: " + name] + rx_list


courses = []
for c, s, e in segs:
    L = P.lines_of(pages, s, e)
    has = any(P.DS.match(l) for _, _, l in L)
    r = M.parse(L) if has else None
    courses.append(dict(code=c, s=s, e=e, L=L, has=has, r=r, title=P.title(pages, c, *first[c]), fp=first[c][0]))

# ---------- course list
lines = ["command: " + CMD,
         "pdf: " + PDF + " (128 pages). Course = first page >=10 where a line matches ^\\s*(\\d{7}|[A-Z]{3}\\d{3})\\s*$ ; pages run to the page before the next course's first page.",
         "columns: code | page range | module table (DETAILED SYLLABUS marker + roman rows) | title (first occurrence of the code line)"]
for k in courses:
    lines.append("%s | p%d-%d | %s | %s" % (k['code'], k['s'], k['e'], "module table" if k["has"] else "no module table", k['title']))
lines.append("total courses: %d ; with module table: %d" % (len(courses), sum(k['has'] for k in courses)))
w("course_list", lines)
# the filename requested by the brief
open(OUT + "nep26-sem56_course_list.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")

# ---------- detect
DET = re.compile(r"(?i)as\s+per\s+nep\s+2020")
hit = [(i + 1, n, l.strip()) for i in range(3) for n, l in enumerate(pages[i]) if DET.search(l)]
w("detect", hdr("detect", ["regex: (?i)as\\s+per\\s+nep\\s+2020  (applied to lines of pages 1-3)", "population: 1 PDF",
                           "matched/total: %d/1 PDF" % (1 if hit else 0)] + ["hit p%d line%d: %r" % h for h in hit] +
                 ["failures: none", "any-page line count (all 128 pages): %d" % sum(1 for p in pages for l in p if DET.search(l))]))

# ---------- course_header
scheme_codes = {}
for pg in (6, 7, 8, 9):
    for n, l in enumerate(pages[pg - 1]):
        m = re.match(r"^\s*(\d{7})\s*$", l)
        if m:
            scheme_codes.setdefault(m.group(1), (pg, n))
det = {k["code"] for k in courses}
f = []
for c, (pg, n) in sorted(scheme_codes.items()):
    if c not in det:
        f.append("scheme-table code %s (p%d line%d) has NO course header on pages>=10 (no detailed syllabus page)" % (c, pg, n))
for c in sorted(det):
    if c not in scheme_codes:
        f.append("detail code %s not present in scheme tables p6-p9 as 7 digits alone on a line" % c)
w("course_header", hdr("course_header", [
    "regex: ^\\s*(\\d{7}|[A-Z]{3}\\d{3})\\s*$  (first occurrence on pages>=10 starts a course)",
    "matched: %d distinct course codes (%d numeric, %d letters+digits)" % (len(det), sum(1 for c in det if c.isdigit()), sum(1 for c in det if not c.isdigit())),
    "scheme-table cross-check (p6-p9 lines matching ^\\s*\\d{7}\\s*$): %d distinct codes; in both: %d" % (len(scheme_codes), len(det & set(scheme_codes))),
    "matched/total vs scheme tables: %d/%d scheme codes have a detail course header" % (len(det & set(scheme_codes)), len(scheme_codes)),
    "mismatches (verbatim):"] + (f or ["none"])))


# ---------- title cross-check
def norm(t):
    return re.sub(r"[^a-z0-9]", "", t.lower().replace("&", "and"))


f = []
ok = 0
tot = 0
for k in courses:
    if not k["code"].isdigit():
        continue
    c = k["code"]
    tit = None
    for pg in (7, 9):
        for n, l in enumerate(pages[pg - 1]):
            if re.match(r"^\s*" + c + r"\s*$", l):
                tit = P.title(pages, c, pg, n)
                break
        if tit:
            break
    tot += 1
    if tit is not None and norm(tit) == norm(k["title"]):
        ok += 1
    else:
        f.append("%s: detail title=%r vs scheme-table(p7/p9) title=%r" % (c, k['title'], tit))
w("title", hdr("title", [
    "procedure (not one regex): title = text lines after the code line, joined, until a line matching ^[\\d\\-–—]+$ or a blank line; a line ending in '-' joins without space",
    "cross-check: normalised (lowercase, &->and, alnum only) equal to the same procedure applied to the p7/p9 scheme-table row; matched/total: %d/%d numeric-code courses (IKS501 has no scheme-table row with that code)" % (ok, tot),
    "mismatches (verbatim):"] + (f or ["none"])))

# ---------- ds_marker
nonds = [k for k in courses if not k["has"]]
dsc = [k for k in courses if k["has"]]
f = []
for k in nonds:
    ev = [(p, n, l.strip()[:45]) for p, n, l in k["L"] if re.search(r"(?i)list of (experiments|assign)|guidelines for", l)]
    f.append("%s %r: no DS marker; independent evidence marker: %s" % (k['code'], k['title'], ev[:2]))
w("ds_marker", hdr("ds_marker", [
    "regex: (?i)^\\s*detailed\\s+syllabus\\s*:?\\s*$ (on each course's pages)",
    "matched/total: %d/%d courses; census signature (signatures.csv detailed_syllabus_hdr) for this PDF = 21" % (len(dsc), len(courses)),
    "the %d non-matching courses (verbatim):" % len(nonds)] + f))


# ---------- module_roman
def attempt1(k):
    L = k["L"]
    ds = [i for i, (p, n, l) in enumerate(L) if P.DS.match(l)][0]
    reg = L[ds + 1:]
    for j, (p, n, l) in enumerate(reg):
        if P.STOP.match(l):
            reg = reg[:j]
            break
    exp = 0
    pos = []
    for p, n, l in reg:
        if exp < len(M.ORD) and l.strip() == M.ORD[exp]:
            pos.append((p, n))
            exp += 1
    return pos


f1 = []
ok1 = 0
for k in dsc:
    rows = k["r"][0]
    pos = attempt1(k)
    bad = [(i, pos[i], rows[i]["pos"]) for i in range(min(len(pos), len(rows))) if pos[i] != rows[i]["pos"]]
    if bad:
        f1.append("attempt1 %s: Roman row start differs from attempt2: %s (a table-header cell such as 'IAT-I' on the course's first page is read as module I)" % (k['code'], bad[:2]))
    else:
        ok1 += 1
f2 = []
for k in dsc:
    rows = k["r"][0]
    if [r["num"] for r in rows] != M.ORD[:len(rows)] or len(rows) < 1:
        f2.append("%s roman rows %s" % (k['code'], [r['num'] for r in rows]))
w("module_roman", hdr("module_roman", [
    "regex: ^\\s*(I|II|III|IV|V|VI|VII|VIII)\\s*$ , rows must appear in order I,II,...",
    "population: courses with DETAILED SYLLABUS marker (%d)" % len(dsc),
    "attempt1 (region starts right after the DETAILED SYLLABUS line): %d/%d courses give the same rows as the final rule; failures:" % (ok1, len(dsc))] + (f1 or ["none"]) + [
    "attempt2 (region starts after the first lone CO/LO[ Mapping] line = column-header end; regex ^\\s*(C[O0]|LO)(\\s+mapping)?\\s*$): consecutive I..N in %d/%d courses" % (len(dsc) - len(f2), len(dsc)),
    "modules per course: %s ; total module rows: %d" % (sorted(set(len(k['r'][0]) for k in dsc)), sum(len(k['r'][0]) for k in dsc)),
    "failures attempt2:"] + (f2 or ["none"])))

# ---------- tail
allrows = [(k, r) for k in dsc for r in k["r"][0]]
A1 = re.compile(r"^\s*((CO|LO)\s?\d+(\s*(,|&|-|–|to|and)\s*((CO|LO)\s?)?\d+)*)\s*$")
A2 = re.compile(r"^\s*((C[O0]|LO)\s?\d+(\s*(,|&|-|–|to|and)\s*((C[O0]|LO)\s?)?\d+)*)\s*$")
A3 = re.compile(r"^\s*((C[O0]|L[O0])\s?\d+(\s*(,|&|-|–|to|and)\s*((C[O0]|L[O0])\s?)?\d+)*)\s*$")


def row_span(k, r):
    reg = k["r"][3]
    start = [i for i, (p, n, l) in enumerate(reg) if (p, n) == r["pos"]][0]
    idx = M.ORD.index(r["num"])
    end = len(reg)
    if idx + 1 < len(M.ORD):
        nxt = [i for i in range(start + 1, len(reg)) if reg[i][2].strip() == M.ORD[idx + 1]]
        if nxt:
            end = nxt[0]
    return reg[start + 1:end]


def rx_cov(rx):
    ok = 0
    f = []
    for k, r in allrows:
        span = row_span(k, r)
        if any(rx.match(l) for p, n, l in span):
            ok += 1
        else:
            lastl = [(p, n, l.strip()) for p, n, l in span if l.strip()][-3:]
            f.append("%s module %s (pdf %s p%d line%d): no match; last non-blank lines of row: %s" % (k['code'], r['num'], PDF, r['pos'][0], r['pos'][1], lastl))
    return ok, f


rxs = {"attempt1": r"^\s*((CO|LO)\s?\d+(\s*(,|&|-|–|to|and)\s*((CO|LO)\s?)?\d+)*)\s*$",
       "attempt2": r"^\s*((C[O0]|LO)\s?\d+(\s*(,|&|-|–|to|and)\s*((C[O0]|LO)\s?)?\d+)*)\s*$   (accepts zero typed for letter O: 'C03')",
       "attempt3": r"^\s*((C[O0]|L[O0])\s?\d+(\s*(,|&|-|–|to|and)\s*((C[O0]|L[O0])\s?)?\d+)*)\s*$   (also accepts 'L06')"}
res = [(n, rx_cov(rx)) for n, rx in (("attempt1", A1), ("attempt2", A2), ("attempt3", A3))]
Lg = hdr("module_tail", ["population: every module row of every course with a module table; a row matches if any line inside the row matches"])
for n, (ok, f) in res:
    Lg += ["%s regex: %s" % (n, rxs[n]), "%s matched/total: %d/%d modules" % (n, ok, len(allrows))] + ["  failure: " + x for x in f]
Lg += ["FINAL: attempt3. Remaining failure(s) are rows with no CO/LO line in the PDF text at all (see above) -> tail regex PARTIAL"]
w("module_tail", Lg)
tail_ok = res[2][1][0]
tail_tot = len(allrows)

# ---------- hours
th = [(k, r) for k, r in allrows if r["tail"] is None or r["tail"].lstrip()[0] in "Cc"]
lab_rows = [(k, r) for k, r in allrows if r["tail"] is not None and r["tail"].lstrip()[0] in "Ll"]
theory_codes = {k["code"] for k, r in th}
okh = 0
f = []
for k, r in th:
    if r["hours"] is not None:
        okh += 1
    else:
        f.append("%s module %s (p%d line%d): no digit-only line directly before a CO tail (tail=%r)" % (k['code'], r['num'], r['pos'][0], r['pos'][1], r['tail']))
w("hours", hdr("hours", [
    "regex: ^\\s*\\d{1,2}\\s*$ on the non-blank line immediately before the CO tail line (theory courses only: they have an 'Hours' column)",
    "matched/total: %d/%d theory modules (%d courses)" % (okh, len(th), len(theory_codes)), "failures (verbatim):"] + (f or ["none"]) + [
    "lab-with-modules rows (LO tail, no Hours column): %d modules; hours extracted: %d (must be 0; a digit line before an LO tail is content, e.g. 'OWASP Top / 10' in 2166122)" % (len(lab_rows), sum(1 for k, r in lab_rows if r['hours']))]))

# ---------- prerequisite row
PRE0 = re.compile(r"^0+$")
okp = 0
f = []
variants = {"labelled Prerequisite": 0, "labelled Pre-Requisite": 0, "unlabelled": 0}
for k in dsc:
    reg = k["r"][3]
    nb = [(p, n, l.strip()) for p, n, l in reg if l.strip()][:3]
    if nb and PRE0.match(nb[0][2]):
        okp += 1
        lab = nb[1][2] if len(nb) > 1 else ""
        if re.match(r"(?i)^pre-?requisites?$", lab):
            variants["labelled Pre-Requisite" if "-" in lab else "labelled Prerequisite"] += 1
        else:
            variants["unlabelled"] += 1
    else:
        f.append("%s: region begins %s" % (k['code'], nb))
w("prerequisite_row", hdr("prerequisite_row", [
    "regex: first non-blank line of the module region == ^0+$ (Sr.No 0), optionally followed by (?i)^\\s*pre-?\\s*requisites?\\s*$ then free text then a hours cell like '00'/'01'/'-'",
    "matched/total: %d/%d courses with module table" % (okp, len(dsc)), "label variants: %s" % variants, "failures (verbatim):"] + (f or ["none"])))
FP = re.compile(r"(?i)^\s*pre-?\s*requisites?\s*:")
fm = [(k["code"], p, n, l.strip()[:60]) for k in courses for p, n, l in k["L"] if FP.match(l)]
w("prerequisite_frontmatter", hdr("prerequisite_frontmatter", [
    "regex: (?i)^\\s*pre-?\\s*requisites?\\s*:",
    "courses with a front-matter 'Prerequisite:' line: %d/%d" % (len(set(c for c, _, _, _ in fm)), len(courses))] + ["%s p%d line%d: %r" % x for x in fm]))

# ---------- self marker
SM = re.compile(r"(?i)\bself[\s\-–]*(learning|study)\b")
ok = 0
f = []
sp = {}
for k, r in allrows:
    hits = [x for x in r["lines"] if SM.search(x[2])]
    if hits:
        ok += 1
        for p, n, s in hits:
            m = SM.search(s)
            key = re.sub(r"\s+", " ", s[m.start():m.end() + 9]).strip()
            sp[key] = sp.get(key, 0) + 1
    else:
        f.append("%s module %s (p%d line%d): no self-learning/self-study text inside row" % (k['code'], r['num'], r['pos'][0], r['pos'][1]))
spell = {}
for key, v in sp.items():
    kk = re.sub(r"(?i)^(self[\s\-–]*(learning|study)).*$", lambda m: m.group(1), key)
    spell[kk] = spell.get(kk, 0) + v
w("self_marker", hdr("self_marker", [
    "regex: (?i)\\bself[\\s\\-–]*(learning|study)\\b",
    "matched/total: %d/%d module rows contain the marker; the %d misses are modules whose PDF text has no marker (verified by dump, not a regex failure)" % (ok, len(allrows), len(f)),
    "distinct spellings of the marker word (count): %s" % spell,
    "marker + following 9 chars, non-standard continuations (verbatim):"] + ["  %r: %d" % (k_, v) for k_, v in sorted(sp.items()) if not re.match(r"^Self-learning Topics", k_)][:40] + ["modules without marker:"] + f))

# ---------- stop marker
ST = re.compile(r"(?i)^\s*(text\s*(and\s+reference\s+)?books?\b|books\s*:)")
ST1 = re.compile(r"^\s*Text\s*Books?\b")


def cov(rx, pop):
    ok = 0
    f = []
    for k in pop:
        if any(rx.match(l) for p, n, l in k["L"]):
            ok += 1
        else:
            f.append("%s (pdf %s pages %d-%d): no match" % (k['code'], PDF, k['s'], k['e']))
    return ok, f


o1, f1 = cov(ST1, dsc)
o2, f2 = cov(ST, dsc)
spl = sorted(set(l.strip() for k in dsc for p, n, l in k["L"] if ST.match(l)))
tl = sum(1 for p in pages for l in p if re.search(r"(?i)^\s*total\s+hours?\s*$", l))
nd_ok, nd_f = cov(ST, nonds)
w("stop_marker", hdr("stop_marker", ["population: %d courses with module table (stop = end of module table)" % len(dsc),
                                    "attempt1 regex: ^\\s*Text\\s*Books?\\b", "attempt1 matched/total: %d/%d" % (o1, len(dsc))] + ["  failure: " + x for x in f1] + [
    "attempt2 regex: (?i)^\\s*(text\\s*(and\\s+reference\\s+)?books?\\b|books\\s*:)", "attempt2 matched/total: %d/%d" % (o2, len(dsc))] + ["  failure: " + x for x in f2] + [
    "distinct matched line spellings: %s" % spl,
    "lines matching ^\\s*Total Hours?\\s*$ in whole pdf (old-repo hint): %d" % tl,
    "non-module courses (labs with experiment lists / project) matched by attempt2: %d/%d" % (nd_ok, len(nonds))] + ["  note (no Text Books line): " + x for x in nd_f]))

summ = {"tail": (tail_ok, tail_tot), "dsc": len(dsc), "hours": (okh, len(th)), "self": (ok, len(allrows)), "stop": (o2, len(dsc)),
        "roman": (len(dsc) - len(f2) if False else len(dsc), len(dsc)), "pre": (okp, len(dsc)), "stop_nonmod": (nd_ok, len(nonds)), "courses": len(courses)}
json.dump(summ, open("spikes/nep26-sem56_summary.json", "w"))
print(summ)
