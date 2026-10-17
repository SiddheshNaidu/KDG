"""Spike for family nep2425-fe: runs each regex against EVERY course unit, writes docs/evidence/regex_runs/nep2425-fe_<name>.txt.
Usage: PYTHONIOENCODING=utf-8 python spikes/nep2425-fe_regex.py"""
import fitz, re, os, sys
D = "data/raw/2024-25-scheme/FE/"
OUT = "docs/evidence/regex_runs/nep2425-fe_"
CMD = "PYTHONIOENCODING=utf-8 python spikes/nep2425-fe_regex.py"
PDF = {"ESC102": "02 Syllabus.pdf", "BSC103": "Applied Chemistry syllabus 2024-25.pdf", "ESC101": "NEW EM SYLLABUS 2024-25.pdf",
       "AEC101": "Professional_Comm._Ethics_Theory_Sem_I 2024-25.pdf", "VSEC102": "Syllabus-C Prog.pdf", "AEC101-stub": "02 Syllabus.pdf"}
LABS = {"ESL102": "02 Syllabus.pdf", "BSL102": "Applied Chemistry syllabus 2024-25.pdf", "ESL101": "NEW EM SYLLABUS 2024-25.pdf", "VSEC102": "Syllabus-C Prog.pdf"}
_cache = {}


def lines(pdf):
    if pdf not in _cache:
        L = []
        for pi, p in enumerate(fitz.open(D + pdf), 1):
            for i, l in enumerate(p.get_text().split("\n")):
                L.append((pi, i, l))
        _cache[pdf] = L
    return _cache[pdf]


HDR = re.compile(r"^\s*DETAILED SYLLABUS")
STOP = re.compile(r"^\s*(Text Books?|Recommended Books|References?)\s*:?\s*$")


def region(unit):
    L = lines(PDF[unit])
    s = None
    for k, (p, i, l) in enumerate(L):
        if s is None and HDR.match(l):
            s = k
        elif s is not None and STOP.match(l):
            return L[s:k + 1]
    return L[s:] if s is not None else []


def rtext(R):
    return "\n".join(l for _, _, l in R)


def loc(R, text, pos):
    k = text.count("\n", 0, pos)
    p, i, l = R[k]
    return f"page {p} line {i}"


results = {}


def write(name, regex, total, matched, failures, extra=""):
    s = f"command: {CMD}\nregex: {regex}\nmatched/total: {matched}/{total}\n{extra}"
    s += "failures:\n" + ("\n".join("  " + f for f in failures) if failures else "  (none)") + "\n"
    open(OUT + name + ".txt", "w", encoding="utf-8").write(s)
    results[name] = (matched, total, failures)


# ---- 1 course code alone on a line
CODE = r"^\s*([A-Z]{3,4})\s?(\d{3})\s*$"
units = [("ESC102", "02 Syllabus.pdf"), ("ESL102", "02 Syllabus.pdf"), ("AEC101-stub", "02 Syllabus.pdf"), ("BSC103", PDF["BSC103"]),
         ("BSL102", PDF["BSC103"]), ("ESC101", PDF["ESC101"]), ("ESL101", PDF["ESC101"]), ("AEC101", PDF["AEC101"]), ("VSEC102", PDF["VSEC102"])]
m = 0
f = []
for u, pdf in units:
    code = u.split("-")[0]
    hit = None
    for p, i, l in lines(pdf):
        mm = re.match(CODE, l)
        if mm and mm.group(1) + mm.group(2) == code:
            hit = (p, i, l)
            break
    if hit:
        m += 1
    else:
        f.append(f"{u} in {pdf}: no line matched")
write("course_code_line", CODE, len(units), m, f, "scope: every course code incl. labs; 'AEC 101' (with space) in the Professional_Comm pdf is matched by \\s?\n")

# ---- 2 detailed syllabus header, 3 stop marker
m = 0
f = []
for u in PDF:
    if u == "AEC101-stub":
        ok = any(HDR.match(l) for p, i, l in lines(PDF[u]) if p == 5)
    elif u == "ESC102":
        ok = any(HDR.match(l) for p, i, l in lines(PDF[u]) if p == 1)
    else:
        ok = bool(region(u))
    if ok:
        m += 1
    else:
        f.append(f"{u} in {PDF[u]}: no match" + (" (page 5 of the PDF holds only the AEC101 header/table rows and 'Rationale'; no module table)" if u == "AEC101-stub" else ""))
write("detailed_syllabus_header", HDR.pattern, len(PDF), m, f, "ESC102 checked on page 1 (its table), the stub on page 5\n")
m = 0
f = []
for u in PDF:
    if u == "AEC101-stub":
        ok = any(STOP.match(l) for p, i, l in lines(PDF[u]) if p == 5)
    elif u == "ESC102":
        ok = any(STOP.match(l) for p, i, l in lines(PDF[u]) if p == 2)
    else:
        R = region(u)
        ok = bool(R) and bool(STOP.match(R[-1][2]))
    if ok:
        m += 1
    else:
        f.append(f"{u} in {PDF[u]}: no match")
write("stop_marker", STOP.pattern, len(PDF), m, f)

# ---- 4 Roman module rows (sub-families a,b)
ROM = r"^[ \t]*(I|II|III|IV|V|VI)[ \t]*$"
m = 0
f = []
ex = ""
for u in ["ESC102", "BSC103", "ESC101"]:
    R = region(u)
    t = rtext(R)
    found = [(mm.group(1), loc(R, t, mm.start())) for mm in re.finditer(ROM, t, re.M)]
    seq = [x for x, _ in found]
    ex += f"{u}: {found}\n"
    if seq == ["I", "II", "III", "IV", "V", "VI"]:
        m += 1
    else:
        f.append(f"{u} in {PDF[u]}: got {seq}")
write("module_roman", ROM + "  (flags re.M, applied to region DETAILED SYLLABUS..stop marker)", 3, m, f, ex)

# ---- 5 arabic zero-padded module rows for AEC101
R = region("AEC101")
t = rtext(R)
a1 = r"^[ \t]*0([1-6])[ \t]*$"
a2 = r"^[ \t]*0([1-6])[ \t]*\n(?![ \t]*(?:\d|CO|LO|\uf0b7|\n))"
n1 = [(mm.group(1), loc(R, t, mm.start())) for mm in re.finditer(a1, t, re.M)]
n2 = [(mm.group(1), loc(R, t, mm.start())) for mm in re.finditer(a2, t, re.M)]
exp = [str(i) for i in range(1, 7)]
ok2 = [x for x, _ in n2] == exp
fl = [f"attempt 1 regex {a1}: {len(n1)} matches {n1} (expected 6 modules; hours values 02,02,02 collide with module numbers) -> FAIL",
      f"attempt 2 regex {a2} (flags re.M): {len(n2)} matches {n2}" + (" -> ok (this is the accepted regex)" if ok2 else " -> FAIL")]
write("module_arabic_padded", f"attempt2: {a2} (attempt1 naive: {a1})", 1, 1 if ok2 else 0, fl,
      "unit: AEC101 only (zero-padded Sr numbers, no Roman numerals). matched/total reports attempt 2; attempt 1 failure kept verbatim.\n")

# ---- 6 arabic unpadded module rows for VSEC102
R = region("VSEC102")
t = rtext(R)
a1 = r"^[ \t]*([1-6])[ \t]*$"
n1 = [(mm.group(1), loc(R, t, mm.start())) for mm in re.finditer(a1, t, re.M)]
ok = [x for x, _ in n1] == exp
write("module_arabic_unpadded", a1 + " (flags re.M, region scope)", 1, 1 if ok else 0, [] if ok else [f"VSEC102: {n1}"], f"matches: {n1}\n")

# ---- 7 hours + CO/LO tail
TAIL = r"^[ \t]*(\d{2})[ \t]*\n(?:[ \t]*\n)*[ \t]*((?:CO|LO)[ ]?\d(?:[ \t]*,[ \t]*\n?[ \t]*LO\d)*)[ \t]*$"
expect = {"ESC102": 6, "BSC103": 6, "ESC101": 7, "AEC101": 6, "VSEC102": 6}
m = 0
f = []
ex = ""
for u, e in expect.items():
    R = region(u)
    t = rtext(R)
    n = [(mm.group(1), mm.group(2), loc(R, t, mm.start())) for mm in re.finditer(TAIL, t, re.M)]
    ex += f"{u}: expected {e} got {len(n)} {[(a, b) for a, b, _ in n]}\n"
    if len(n) == e:
        m += 1
    else:
        f.append(f"{u} in {PDF[u]}: expected {e} got {len(n)}: {n}")
write("hours_co_tail", TAIL + " (flags re.M, region scope; ESC101 expected 7 = 6 modules + prerequisite row 'Hours 01 CO1')", len(expect), m, f, ex)

# ---- 8 prerequisite
PQ = r"^\s*Prerequisite\b"
m = 0
f = []
ex = ""
for u in ["ESC102", "BSC103", "ESC101", "AEC101", "VSEC102"]:
    n = [(p, i, l.strip()) for p, i, l in lines(PDF[u]) if re.match(PQ, l)]
    ex += f"{u}: {n}\n"
    if n:
        m += 1
    else:
        f.append(f"{u} in {PDF[u]}: no line matched (label absent from text)")
write("prerequisite_label", PQ, 5, m, f, ex)
ZP = r"^\s*0\s*\n\s*Prerequisite"
m = 0
f = []
for u in ["ESC102", "ESC101"]:
    t = "\n".join(l for _, _, l in lines(PDF[u]))
    if re.search(ZP, t, re.M):
        m += 1
    else:
        f.append(f"{u}: no match")
write("prerequisite_row_zero", ZP + " (flags re.M)", 2, m, f, "units: the two courses whose module table has the 'Sr No 0 / Prerequisite' row (ESC102, ESC101)\n")

# ---- 9 self-learning
SL = r"(?i)self[\s-]*(learning|study)"
n = []
for pdf in sorted(set(PDF.values())):
    for p, i, l in lines(pdf):
        if re.search(SL, l):
            n.append(f"{pdf} page {p} line {i}: {l!r}")
write("self_learning_marker", SL, 5, len(n), n, "matched = number of hits over all lines of the 5 PDFs (0 = marker never appears)\n")

# ---- 10 page-number first line
PN = r"^\d{1,2}\s*$"
m = 0
tot = 0
f = []
for pdf in sorted(set(PDF.values())):
    for p, i, l in lines(pdf):
        if i == 0:
            tot += 1
            if re.match(PN, l):
                m += 1
            else:
                f.append(f"{pdf} page {p} line 0: {l!r}")
write("page_number_first_line", PN, tot, m, f, "scope: first raw line of every page of the 5 PDFs\n")

# ---- 11 lab experiment list label and rows
LB = r"^\s*(List of\s+Experiments|Suggested List of)\b"
m = 0
f = []
for u, pdf in LABS.items():
    if any(re.match(LB, l) for _, _, l in lines(pdf)):
        m += 1
    else:
        f.append(f"{u} in {pdf}: no match")
write("lab_list_label", LB, len(LABS), m, f)
ROW = r"(?m)^(\d{2})[ \t]*\n((?:(?![ \t]*\d{2}[ \t]*\n).*\n){1,6}?)[ \t]*(\d{2})[ \t]*\n[ \t]*LO\d"
expl = {"ESL102": 13, "BSL102": 11}
m = 0
f = []
ex = ""
cut = re.compile(r"List of\s+Assignments")
for u, e in expl.items():
    t = "\n".join(l for _, _, l in lines(LABS[u]))
    n1 = [mm.group(1) for mm in re.finditer(ROW, t)]
    ex += f"{u} attempt 1 (whole pdf text): expected {e} got {len(n1)} {n1}\n"
    if len(n1) != e:
        f.append(f"attempt 1 {u} in {LABS[u]}: expected {e} got {len(n1)}: {n1} (extra match comes from the 'List of Assignments / Tutorials' table, whose first row '01 / Assignment on Basic electrical safety practices / 02 / LO1' has the same shape)")
    mc = cut.search(t)
    t2 = t[:mc.start()] if mc else t
    n2 = [mm.group(1) for mm in re.finditer(ROW, t2)]
    ex += f"{u} attempt 2 (text truncated at first 'List of Assignments'): expected {e} got {len(n2)} {n2}\n"
    if len(n2) == e:
        m += 1
    else:
        f.append(f"attempt 2 {u} in {LABS[u]}: expected {e} got {len(n2)}: {n2}")
write("lab_row_hours_lo", "attempt2 = ROW applied to text before first 'List of\s+Assignments'; ROW=" + ROW, len(expl), m, f, ex)
for k, (m, t, fl) in results.items():
    print(f"{k}: {m}/{t} failures={len(fl)}")
