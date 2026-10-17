"""Throwaway spike: runs every nep26-se-civil regex over EVERY course in the family and writes docs/evidence/regex_runs/nep26-se-civil_*.txt
Command: PYTHONIOENCODING=utf-8 python spikes/nep26-se-civil_runs.py"""
import sys, re, glob, csv, importlib, os, json
sys.path.insert(0, "spikes")
M = importlib.import_module("nep26-se-civil_parse")
TV = importlib.import_module("topic_validity")
import fitz
OUT = "docs/evidence/regex_runs/"
CMD = "PYTHONIOENCODING=utf-8 python spikes/nep26-se-civil_runs.py"
FAMPDF = "2019-scheme/Civil-Engineeing/6.23-N-B.E.-Civil-Engineeing-Sem-III-IV.pdf"
P = M.pages()
C = M.courses(P)
for c in C:
    c["title"] = M.title(P, c)


def w(name, regexes, matched, total, failures, extra=()):
    with open(OUT + "nep26-se-civil_" + name + ".txt", "w", encoding="utf-8") as f:
        f.write("command: %s\n" % CMD)
        f.write("pdf: data/raw/%s\n" % FAMPDF)
        for k, v in regexes:
            f.write("regex %s: %s\n" % (k, v))
        f.write("matched/total: %d/%d\n" % (matched, total))
        f.write("failures: %d\n" % len(failures))
        for x in failures:
            f.write("FAIL %s\n" % x)
        for x in extra:
            f.write(x + "\n")
    print(name, "%d/%d" % (matched, total), "fail", len(failures))


# ---------- detect (PDF level, plus negative control over all PDFs in signatures.csv) ----------
DET = [r"(?m)^Second Year Civil Engineering\s*$", r"(?m)^Course Module / Contents\s*$"]
rows = list(csv.DictReader(open("docs/evidence/signatures.csv", encoding="utf-8")))
hit_other, hit_fam = [], 0
for r in rows:
    d = fitz.open("data/raw/" + r["path"])
    t = "\n".join(p.get_text() for p in d)
    ok = all(re.search(x, t) for x in DET)
    if r["path"] == FAMPDF:
        hit_fam += ok
    elif ok:
        hit_other.append(r["path"])
w("detect", [("D1", DET[0]), ("D2", DET[1]), ("rule", "family detected iff D1 and D2 both match somewhere in whole-PDF page text joined by newline")],
  hit_fam, 1, [], ["negative control: %d other PDFs in docs/evidence/signatures.csv checked (total rows %d); false positives = %d" % (len(rows) - 1, len(rows), len(hit_other))] + ["FALSEPOS " + x for x in hit_other])

# ---------- course code (compared with scheme-table codes on pdf pages 10 and 12) ----------
scheme = []
for pg in (10, 12):
    for l in P[pg - 1]:
        m = re.match(r"^(\d{7}) $", l)
        if m:
            scheme.append((m.group(1), pg))
found = {c["code"] for c in C}
miss = [(cd, pg) for cd, pg in scheme if cd not in found]
w("course_code", [("CODE", r"^(\d{7})\s*$  (whole line; course start = pdf page >=16, line index <25, preceded within 16 lines by a line matching ^(Course )?Code\s*$ or ^Course Code\s*$)")],
  len(scheme) - len(miss), len(scheme),
  ["%s | pdf page %d (scheme table first table) | code listed in scheme but no course-start page found, so no syllabus text" % (cd, pg) for cd, pg in miss],
  ["courses found (%d): " % len(C) + ", ".join("%s p%d-%d" % (c["code"], c["start"], c["end"]) for c in C),
   "found codes not in scheme tables: " + str(sorted(found - {s[0] for s in scheme}))] +
  ["pdf pages on which the missing code string occurs anywhere: %s=%s" % (cd, [i + 1 for i, L in enumerate(P) if any(cd in l for l in L)]) for cd, pg in miss])


# ---------- title (first table vs second table agreement) ----------
def title2(c):
    L = P[c["start"] - 1]
    idx = [i for i, l in enumerate(L) if M.CODE_LINE.match(l)]
    if len(idx) < 2:
        return None
    j = idx[1]
    t = []
    for l in L[j + 1:j + 8]:
        if re.match(r"^(\d+[*#]?(\+\d+)?|[-–—]+|\(.*)\s*$", l.strip()):
            break
        t.append(l.strip())
    return " ".join(t)


norm = lambda s: re.sub(r"\s+", " ", s or "").strip().lower()
fails = []
ok = 0
for c in C:
    t1, t2 = c["title"], title2(c)
    if norm(t1) == norm(t2):
        ok += 1
    else:
        fails.append("%s | pdf page %d | table1 title=%r | table2 title=%r" % (c["code"], c["start"], t1, t2))
w("title", [("TITLE_STOP", r"^(\d+[*#]?(\+\d+)?|[-–—]+|\(.*)\s*$  (title = lines after code line joined by space until first line matching TITLE_STOP; checked by comparing table 1 (teaching scheme) vs table 2 (exam scheme) on the same page, case/whitespace-insensitive)")],
  ok, len(C), fails, ["titles (table1): " + " || ".join("%s=%s" % (c["code"], c["title"]) for c in C)])

# ---------- module courses ----------
modc = []
for c in C:
    L = M.body_lines(P, c)
    c["L"] = L
    c["has_modtable"] = M.module_section(L) is not None
    if c["has_modtable"]:
        modc.append(c)


OUT_HDR = r"^(?:(?:Course|Lab) )?Outcomes:"
OUT_END = r"^(?:Semester|Detailed|DETAILED|Prerequisite|Pre[- ]?[Rr]equisite|Module|Sr\. ?No)"
OUT_ITEM = r"^\d+(?:[.)]|[ ]*$)"


def n_outcomes(L):
    t = "\n".join(l.strip() for l in L)
    m = re.search(OUT_HDR, t, re.M)
    if not m:
        return None
    seg = t[m.end():]
    e = re.search(OUT_END, seg, re.M)
    seg = seg[:e.start()] if e else seg
    return len(re.findall(OUT_ITEM, seg, re.M))


fails = []
ok = 0
info = []
for c in modc:
    mods = M.parse_modules(c["L"])
    c["mods"] = mods
    exp = n_outcomes(c["L"])
    nums = [m["num"] for m in mods]
    good = exp is not None and len(mods) == exp and nums == list(range(1, len(mods) + 1))
    ok += good
    info.append("%s modules=%s hours=%s co=%s outcomes_count=%s" % (c["code"], nums, [m["hours"] for m in mods], [m["co"] for m in mods], exp))
    if not good:
        fails.append("%s | pdf pages %d-%d | modules found %s vs outcomes listed %s" % (c["code"], c["start"], c["end"], nums, exp))
w("module_row", [("COLHDR", M.RE_COLHDR.pattern), ("MODROW", M.RE_MODROW.pattern), ("STOP", M.RE_STOP.pattern + " (flags re.I|re.M)"), ("COURSEHDR", M.RE_COURSEHDR.pattern)],
  ok, len(modc), fails,
  ["courses with a 'Course Module / Contents' header: %d of %d courses; the other %d courses have no module table: %s" % (len(modc), len(C), len(C) - len(modc), [c["code"] for c in C if not c["has_modtable"]]),
   "denominator rule: course counts as matched if module count == numbered items under 'Course/Lab Outcomes:' and module numbers run 1..n"] + info)

# subitem
fails = []
okm = 0
totm = 0
rawdots = 0
acc = 0
for c in modc:
    c["subs"] = {}
    for m in c["mods"]:
        totm += 1
        subs, sl = M.split_body(m)
        seq = [s[0] for s in subs]
        c["subs"][m["num"]] = (subs, sl)
        raw = [l for l in m["body"] if re.match(r"^\s*\d{1,2}\.\d{1,2}(\s|$)", l)]
        rawdots += len(raw)
        acc += len(subs)
        if seq == list(range(1, len(seq) + 1)) and seq and len(raw) == len(subs):
            okm += 1
        else:
            fails.append("%s | module %d | pdf pages %d-%d | accepted sub-item numbers %s, raw dotted-start lines %d" % (c["code"], m["num"], c["start"], c["end"], seq, len(raw)))
w("subitem", [("SUB", M.RE_SUB.pattern + "  (applied to each stripped line of a module body; accepted only if group1 == current module number)")],
  okm, totm, fails, ["modules checked across %d courses; sub-items accepted=%d, raw lines starting with N.M = %d" % (len(modc), acc, rawdots)])

HIST_SELF = [
    "ATTEMPT HISTORY (failures of earlier attempts, kept verbatim):",
    "attempt 1 regex: Self[- ]?learning\s+[Tt]opics?\s*:  (re.I) -> 10/11; FAIL 2094111 | RE_SELF=2 captured=2 any-spelling=6; unmatched lines:",
    "  attempt1 FAIL 2094111 | pdf page 53 line 23 | 'Self- Learning Topics: '",
    "  attempt1 FAIL 2094111 | pdf page 53 line 66 | 'Self- learning Topics: Conditional probability, Total Probability '",
    "  attempt1 FAIL 2094111 | pdf page 54 line 16 | 'Self -learning Topics: Test of significance of large samples, '",
    "  attempt1 FAIL 2094111 | pdf page 54 line 28 | 'Self- learning Topics: ANOVA: One way classification, Two- '",
    "attempt 2 regex: Self[\s-]*learning\s+topics?\s*:  (re.I) -> see matched/total above",
]
HIST_OUT = [
    "ATTEMPT HISTORY (failures of earlier attempts, kept verbatim):",
    "attempt 1 regexes: header ^(Course|Lab) Outcomes:  item ^\d+\.  -> 15/17",
    "  attempt1 FAIL 2093611 | pdf pages 46-51 | header line is 'Outcomes: ' (pdf page 46 line 80), items are a bare number on its own line ('1', '2', ...)",
    "  attempt1 FAIL 2094411 | pdf pages 70-74 | header 'Lab Outcomes:' matched but items numbered '1) ...' (pdf page 70 line 82), item regex found 0",
    "attempt 2 regexes: OUT_HDR / OUT_ITEM / OUT_END above -> see matched/total above",
]
# self learning
fails = []
ok = 0
tot = 0
info = []
for c in modc:
    sec = M.module_section(c["L"])
    total_raw = len(M.RE_SELF.findall(sec))
    cap = sum(len([x for x in c["subs"][m["num"]][1] if M.RE_SELF.search(x)]) for m in c["mods"])
    anyspell = len(re.findall(r"self[\s-]*learning", sec, re.I))
    tot += 1
    info.append("%s RE_SELF occurrences in module section=%d, captured lines containing marker=%d, any 'self-learning' spelling=%d" % (c["code"], total_raw, cap, anyspell))
    if total_raw == cap == anyspell:
        ok += 1
    else:
        fails.append("%s | pdf pages %d-%d | RE_SELF=%d captured=%d any-spelling=%d" % (c["code"], c["start"], c["end"], total_raw, cap, anyspell))
w("self_learning", [("SELF", M.RE_SELF.pattern + "  (flags re.I)")], ok, tot, fails, info + HIST_SELF)

# outcomes header
fails = []
ok = 0
for c in C:
    n = n_outcomes(c["L"])
    if n:
        ok += 1
    else:
        fails.append("%s | pdf pages %d-%d | no 'Course Outcomes:'/'Lab Outcomes:' header with numbered items found (n=%s)" % (c["code"], c["start"], c["end"], n))
w("outcomes", [("OUT_HDR", OUT_HDR), ("OUT_ITEM", OUT_ITEM + " (counted after header until OUT_END)"), ("OUT_END", OUT_END)], ok, len(C), fails, HIST_OUT)


# ---------- topic validity census (naive candidate topics) ----------
def norm_ws(s):
    return re.sub(r"\s+", " ", s).strip()


cens = {"S1_subitem_whole": {}, "S2_split_on_colon_semicolon_comma_period": {}}
tot = {k: 0 for k in cens}
ex = []
for c in modc:
    for m in c["mods"]:
        subs, sl = c["subs"][m["num"]]
        for n, parts in subs:
            txt = norm_ws(" ".join(parts))
            cands1 = [txt]
            depth = 0
            cur = ""
            cands2 = []
            for ch in txt:
                if ch == "(":
                    depth += 1
                if ch == ")":
                    depth = max(0, depth - 1)
                if ch in ":;,." and depth == 0:
                    cands2.append(cur)
                    cur = ""
                else:
                    cur += ch
            cands2.append(cur)
            cands2 = [x.strip() for x in cands2 if x.strip()]
            for k, cs in (("S1_subitem_whole", cands1), ("S2_split_on_colon_semicolon_comma_period", cands2)):
                for t in cs:
                    tot[k] += 1
                    v = TV.validate(t)
                    for r in v:
                        cens[k][r] = cens[k].get(r, 0) + 1
                    if v:
                        cens[k]["_topics_with_any_violation"] = cens[k].get("_topics_with_any_violation", 0) + 1
                    if k.startswith("S1") and v and len(ex) < 3:
                        ex.append("example violating topic (S1): %r -> %s" % (t[:80], v))
lines = []
for k in cens:
    lines.append("%s: total_candidates=%d violations_by_rule=%s" % (k, tot[k], json.dumps(cens[k], sort_keys=True)))
for fn in sorted(glob.glob("tests/golden/nep26-se-civil/*.json")):
    j = json.load(open(fn, encoding="utf-8"))
    gt = 0
    gv = {}
    bad = []
    for m in j["modules"]:
        for t in m["topics"]:
            gt += 1
            v = TV.validate(t)
            for r in v:
                gv[r] = gv.get(r, 0) + 1
            if v:
                bad.append("%r->%s" % (t, v))
    lines.append("golden %s: topics=%d violations_by_rule=%s %s" % (os.path.basename(fn), gt, json.dumps(gv, sort_keys=True), bad))
w("topic_validity", [("validate", "spikes/topic_validity.py validate() rules R1-R8 (docs/formats/topic_validity.md)"),
                     ("candidates", "S1 = whole sub-item text of the module courses; S2 = sub-item text split at : ; , . outside parentheses (naive baseline; a human decision per case is still needed)")],
  0, 0, [], lines + ex)

# ---------- prerequisite line (informational coverage: courses having it / courses) ----------
PRE = r"(?im)^Pre[- ]?requisites?\s*:"
fails = []
ok = 0
info = []
for c in C:
    t = "\n".join(l.strip() for l in c["L"])
    ms = list(re.finditer(PRE, t))
    if ms:
        ok += 1
    else:
        fails.append("%s | pdf pages %d-%d | no prerequisite line (not an error by itself: absence of a prerequisite is UNKNOWN vs 'none')" % (c["code"], c["start"], c["end"]))
    for m in ms:
        info.append("%s prerequisite line: %r" % (c["code"], t[m.start():m.start() + 90].replace("\n", " / ")))
w("prereq", [("PRE", PRE)], ok, len(C), fails, info)

# ---------- page-header noise and other noise lines ----------
HDR = [r"^Page \| \d+ $", r"^University of Mumbai $", r"^Second Year Civil Engineering $"]
fails = []
ok = 0
tot = 0
for i, L in enumerate(P):
    pg = i + 1
    if pg < 6:
        continue
    tot += 1
    if all(re.match(HDR[k], L[k]) for k in range(3)):
        ok += 1
    else:
        fails.append("pdf page %d | first 3 lines %r" % (pg, L[:3]))
fl = []
for i, L in enumerate(P):
    for j, l in enumerate(L):
        if re.match(r"^(Semester (III|IV)|Vertical . \d+)\s*$", l):
            fl.append("NOISE2 pdf page %d line %d %r" % (i + 1, j, l))
w("noise", [("HDR1", HDR[0]), ("HDR2", HDR[1]), ("HDR3", HDR[2]), ("rule", "lines 0..2 of every pdf page 6..82 (pages 1-5 are cover/front matter, see extras)"),
            ("NOISE2", r"^(Semester (III|IV)|Vertical . \d+)\s*$ (stray single lines, listed below)")], ok, tot, fails,
  ["pdf page 1 line count=%d, page 5 first lines=%r" % (len(P[0]), P[4][:3])] + fl)

# ---------- repeated column header noise inside module section ----------
LEAK = r"(?m)^(?:Module|Course Module / Contents|Hours|Hrs|CO|LO|Mapping|Mappi|ng)\s*$"
fails = []
ok = 0
info = []
for c in modc:
    sec = M.module_section(c["L"])
    n_hdr_before = len(re.findall(r"(?m)^Course Module / Contents\s*$", sec))
    cleaned = M.RE_COLHDR.sub("", sec)
    leaks = re.findall(LEAK, cleaned)
    info.append("%s column-header blocks in module section=%d (1 real + continuation-page repeats), leftover header tokens after removal=%d" % (c["code"], n_hdr_before, len(leaks)))
    if leaks:
        fails.append("%s | pdf pages %d-%d | leftover tokens %r" % (c["code"], c["start"], c["end"], leaks))
    else:
        ok += 1
w("colhdr", [("COLHDR", M.RE_COLHDR.pattern), ("LEAK", LEAK)], ok, len(modc), fails,
  info + ["ATTEMPT HISTORY (earlier attempt failures, kept verbatim):",
          "attempt 1 regex: ^Module[ ]*\nCourse Module / Contents[ ]*\nHours[ ]*\n(?:CO|LO)[ ]*\n(?:Mapping[ ]*\n)?  (module_section cut after the first 'Course Module / Contents' line)",
          "  attempt1 FAIL 2094111 | pdf page 54 lines 4-7 | 'Module', 'Course Module / Contents ', 'Hrs ', 'CO ' (header spells 'Hrs'; leaked into body of sub-item 5.2 as text 'Module Course Module / Contents Hrs CO')",
          "  attempt1 FAIL 2094111 | pdf page 53 lines 4-7 | first header also spells 'Hrs ' / 'CO ' (left in section lead)",
          "  attempt1 FAIL 2994512 | pdf page 78 lines 80-85 | header 'Module','Course Module / Contents','Hours','CO','Mappi','ng' (word 'Mapping' split over two lines)",
          "attempt 2 regex = COLHDR above -> see matched/total"])

# ---------- non-module courses: experiment / stages tables ----------
EXP = r"^\s*(?:Sr\.? ?No\.?\s*$|List of (?:Experiments|Assignments)[^\n]*$|Stages of Project|Concepts & Discussions|Practical\s*$)"
fails = []
ok = 0
info = []
nonmod = [c for c in C if not c["has_modtable"]]
for c in nonmod:
    hits = []
    for pg in range(c["start"], c["end"] + 1):
        for j, l in enumerate(P[pg - 1]):
            if re.match(EXP, l):
                hits.append("p%d:l%d:%r" % (pg, j, l.strip()))
    if hits:
        ok += 1
    else:
        fails.append("%s | pdf pages %d-%d | no experiment/stages table header found" % (c["code"], c["start"], c["end"]))
    info.append("%s title=%r first_hits=%s total_hits=%d" % (c["code"], c["title"], hits[:6], len(hits)))
w("experiment_tables", [("EXP", EXP)], ok, len(nonmod), fails, info)

# ---------- extra observations on sub-items ----------
cnt = []
lsp = []
for c in modc:
    cnt.append("%s sub-items per module=%s" % (c["code"], [len(c["subs"][m["num"]][0]) for m in c["mods"]]))
    sec = M.module_section(c["L"])
    for mm in re.finditer(r"(?:\b\w ){5,}\w\b", sec):
        lsp.append("%s letter-spaced text %r" % (c["code"], mm.group(0)))
with open(OUT + "nep26-se-civil_subitem.txt", "a", encoding="utf-8") as f:
    f.write("EXTRA (letter-spaced regex (?:\b\w ){5,}\w\b over module sections):\n")
    for x in cnt + lsp:
        f.write(x + "\n")
