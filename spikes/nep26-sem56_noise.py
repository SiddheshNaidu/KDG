"""Throwaway: noise + numbering-style evidence for nep26-sem56.
Command: PYTHONIOENCODING=utf-8 python spikes/nep26-sem56_noise.py"""
import re, sys, collections
sys.path.insert(0, "spikes")
import importlib
M = importlib.import_module("nep26-sem56_modules")
P = M.P
PDF = "data/raw/_unclassified/SEM-V.pdf"
pages = P.load()
segs, first = P.segments(pages)
out = ["command: PYTHONIOENCODING=utf-8 python spikes/nep26-sem56_noise.py   (pdf=" + PDF + ")"]
# 1. QP template page
QP = re.compile(r"(?i)^\s*note for qp setters")
qp = [i + 1 for i, ls in enumerate(pages) if any(QP.match(l) for l in ls)]
out.append("regex (?i)^\\s*note for qp setters : question-paper template pages (noise, no syllabus content): %d pages: %s" % (len(qp), qp))
# 2. DRAFT / watermark / page-number / running header
dr = [(i + 1, n, l.strip()[:80]) for i, ls in enumerate(pages) for n, l in enumerate(ls) if re.search("(?i)draft", l)]
out.append("regex (?i)draft over all lines: %d hits: %s" % (len(dr), dr))
pn = [(i + 1, l.strip()) for i, ls in enumerate(pages) for l in ls[:3] + ls[-3:] if re.match(r"^\s*(page\s*)?\d{1,3}\s*(/\s*\d+)?\s*$", l, re.I) and False]
cnt = collections.Counter(l.strip() for ls in pages for l in ls if l.strip())
rep = [(t, n) for t, n in cnt.most_common(400) if n >= 60 and len(t) > 12]
out.append("non-trivial (len>12) lines repeated >=60 times across the 128 pages (running header/footer/watermark candidates): %s" % rep)
out.append("lines matching ^\\s*Total Hours?\\s*$ : %d" % sum(1 for ls in pages for l in ls if re.match(r"(?i)^\s*total\s+hours?\s*$", l)))
# 3. inserted scheme-table blocks inside module regions
tot = 0; per = {}
for c, s, e in segs:
    L = P.lines_of(pages, s, e)
    if not any(P.DS.match(l) for _, _, l in L): continue
    r = P.parse_modules(L)
    # recompute removed count
    ds = [i for i, (p, n, l) in enumerate(L) if P.DS.match(l)][0] + 1
    h = next(j for j in range(ds, len(L)) if P.HDREND.match(L[j][2])) + 1
    if h < len(L) and P.MAPPING.match(L[h][2]): h += 1
    stop = next((j for j in range(h, len(L)) if P.STOP.match(L[j][2])), len(L))
    kept, removed = P.strip_tables(L[h:stop])
    nblocks = sum(1 for p, n, l in removed if l.strip() == "Course")
    per[c] = (nblocks, len(removed))
out.append("inserted 'Course / Code / Course Name ...' scheme-table blocks found INSIDE module regions (strip_tables rule; block = line 'Course' + line 'Code' ... code line, title, run of numeric/dash cells): per course (blocks, lines): %s" % per)
# 4. numbering styles inside module rows
styles = {"arabic dotted 1.1 / 4.1": r"^\s*\d+\.\d+\s?\S", "roman dotted I.1": r"^\s*[IVX]+\.\d+\s", "arabic 1. / 2.": r"^\s*\d+\.\s?\S",
          "letter a) b)": r"^\s*[a-e]\)\s", "bullet only line": r"^\s*[•●]\s*$", "dash bullet": r"^\s*-\s+\S"}
res = {k: collections.Counter() for k in styles}
for c, s, e in segs:
    L = P.lines_of(pages, s, e)
    if not any(P.DS.match(l) for _, _, l in L): continue
    for r in M.parse(L)[0]:
        for p, n, x in r["lines"]:
            for k, rx in styles.items():
                if re.match(rx, x): res[k][c] += 1
for k in styles: out.append("numbering style '%s' (regex %s): %d lines in %d courses: %s" % (k, styles[k], sum(res[k].values()), len(res[k]), dict(res[k])))
open("docs/evidence/regex_runs/nep26-sem56_noise.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(o[:600] for o in out))
