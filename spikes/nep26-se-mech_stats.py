"""Spike: descriptive counts backing claims in docs/formats/nep26-se-mech.md. Command: PYTHONIOENCODING=utf-8 python spikes/nep26-se-mech_stats.py"""
import re, sys, io, contextlib, collections, fitz
sys.path.insert(0, "spikes")
from importlib import util
def _imp(n, p):
    s = util.spec_from_file_location(n, p); m = util.module_from_spec(s); s.loader.exec_module(m); return m
with contextlib.redirect_stdout(io.StringIO()): rg = _imp("rg", "spikes/nep26-se-mech_regex.py")
out = open("docs/evidence/regex_runs/nep26-se-mech_stats.txt", "w", encoding="utf-8")
def w(*a): print(*a, file=out)
w("command: PYTHONIOENCODING=utf-8 python spikes/nep26-se-mech_stats.py\n")
# prerequisite spellings
cnt = collections.Counter(); who = collections.defaultdict(set)
for c in rg.courses:
    for p, l in c["lines"]:
        if re.match(r"(?i)^pre-?requisites?\b", l): cnt[l[:40]] += 1; who[l[:40]].add(rg.tag(c))
w("== lines starting (?i)^pre-?requisites?\b  (text[:40], count, #courses)")
for k, v in cnt.most_common(): w(f"  {k!r} {v} {len(who[k])}")
w("\n== Sr.No '0' row: course has a line '0' immediately followed by a line matching ^Prerequisite")
zr = [rg.tag(c) for c in rg.courses if any(re.match(r"^0$", c['lines'][i][1]) and re.match(r"^Prerequisite", c['lines'][i+1][1]) for i in range(len(c['lines'])-1))]
w(f"  {len(zr)} courses: {zr}")
# stop markers actually hit
w("\n== first STOP line per course (region end)")
sc = collections.Counter()
for c in rg.courses:
    r = rg.region(c)
    if r and r[1] < len(c['lines']): sc[c['lines'][r[1]][1][:30]] += 1
    else: sc['<none>'] += 1
for k, v in sc.most_common(): w(f"  {k!r} {v}")
# tails spellings (all lines in all course pages)
w("\n== CO/LO tail line spellings (whole-line, all courses)")
tc = collections.Counter()
for c in rg.courses:
    for p, l in c["lines"]:
        m = re.match(r"^(C[O0]|LO|L)\s?(\d)(.*)$", l)
        if m and len(l) < 14: tc[re.sub(r"\d", "N", l)] += 1
for k, v in tc.most_common(): w(f"  {k!r} {v}")
# header spellings of table header
w("\n== table header lines (hours/CO column) spellings")
hc = collections.Counter()
for c in rg.courses:
    for p, l in c["lines"]:
        if re.match(r"^(Hrs?\.?|Hours?|Hour|Mapp|Mapping|CO|LO|s|Hour s)\s*$", l): hc[l] += 1
for k, v in hc.most_common(): w(f"  {k!r} {v}")
# blank/noise lines
w("\n== noise: lines per all courses")
nl = collections.Counter(); ntot = 0
for sub, path in rg.lib.PDFS.items():
    d = fitz.open(path)
    for pg in d:
        for l in pg.get_text().split("\n"):
            ntot += 1
            if l.strip() == "": nl["blank-or-space-only"] += 1
            if "" in l: nl["U+F0B7 bullet"] += 1
            if "●" in l: nl["U+25CF bullet"] += 1
            if re.match(r"^\s*(Page\s*)?\d+\s*(/\s*\d+)?\s*$", l) and len(l.strip()) > 2: nl["page-number-like (3+ digits)"] += 1
w(f"  total raw lines {ntot}: {dict(nl)}")
# repeated lines across pages in a PDF (header/footer candidates)
for sub, path in rg.lib.PDFS.items():
    d = fitz.open(path); pc = collections.Counter()
    for pg in d:
        for l in set(x.strip() for x in pg.get_text().split("\n") if x.strip()): pc[l] += 1
    w(f"\n== lines present on >=25 pages ({sub}, {len(d)} pages)")
    for k, v in pc.most_common(8):
        if v >= 25: w(f"  {k[:60]!r} {v}")
# sub-family header evidence
w("\n== credits block (line '^Credits\s*$') per course start page  a vs b")
for sub in "ab":
    w(f"  {sub}: " + str(sum(1 for c in rg.courses if c['sub'] == sub and any(re.match(r'^Credits\s*$', l) for p, l in c['lines']))) + "/17")
# page-count of 'Credits Assigned' lines in front matter (pages 1-14) to justify page>=15 gate
for sub, path in rg.lib.PDFS.items():
    d = fitz.open(path); n = [i + 1 for i in range(14) if any(re.match(rg.lib.START_RX, l.strip()) for l in d[i].get_text().split("\n"))]
    w(f"  {sub}: pages<=14 matching course-start regex: {n}")
# lab / odd-course tag: Credits column pattern, titles with Lab
w("\n== titles containing 'Lab'")
for c in rg.courses:
    t, n = rg.title_of(c)
    if t and 'Lab' in t: w("  " + rg.tag(c) + " " + t)
# page-order oddity: course header ('Credits Assigned') after region start
w("\n== raw-order oddity: first line index of region start < first line index of 'Course Code' header (table before header block)")
for c in rg.courses:
    r = rg.region(c); hi = [i for i, (p, l) in enumerate(c['lines']) if l.strip() == 'Course Code']
    if r and hi and r[0] < hi[0]: w(f"  {rg.tag(c)} region_start_idx={r[0]} first 'Course Code' idx={hi[0]}")
out.close()
