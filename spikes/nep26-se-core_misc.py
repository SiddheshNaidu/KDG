"""Misc census for family nep26-se-core: prerequisite spellings, column-header variants, hours header, dotted numbering, last-course trailing pages."""
import sys, re, importlib, collections
sys.path.insert(0, "spikes")
E = importlib.import_module("nep26-se-core_extract"); L = E.L
DET = re.compile(r"^\s*(Detailed Content|Topics|Topic Description|Mapping)\s*$")
out = ["command: PYTHONIOENCODING=utf-8 python spikes/nep26-se-core_misc.py"]
pre = collections.Counter(); col = collections.Counter(); hrs = collections.Counter(); dotted = []
kinds = collections.Counter(); nm = 0; tot = 0
for p in L.PDFS:
    for c in E.courses(p):
        tot += 1
        mt = any(DET.match(x[2]) for x in c["lines"])
        nm += mt
        if not mt: kinds["no module table: " + c["title"]] += 1
        for pg, j, l in c["lines"]:
            if re.search(r"(?i)re-?\s?quisite|perquis", l) and pg >= 16:
                pre[re.sub(r"\s+", " ", l.strip())[:18]] += 1
            if re.match(r"^\s*\d+\.\d+\b", l) and not re.match(r"^\s*\d+\.\d+\s*[-–<]", l): dotted.append(f"{p.split('/')[0]} p{pg} l{j}: {l.strip()[:40]!r}")
        if mt:
            r = E.region(c)
            labs = {x[2].strip() for x in r[:40]}
            key = []
            for k in ("Name of Module", "Name of the Module", "Module", "Unit", "Detailed Content", "Topics", "Topic Description", "Hours", "Hrs", "CO", "LO"):
                if k in labs: key.append(k)
            col[" | ".join(key)] += 1
print_lines = []
out.append(f"courses: {tot}; with module table (Detailed Content|Topics|Topic Description|Mapping column line): {nm}; without: {tot-nm}")
out.append("courses without module table (title: count over 6 PDFs): " + "; ".join(f"{k[17:]}={v}" for k, v in sorted(kinds.items())))
out.append("prerequisite-like lines (page>=16), normalised first 18 chars: " + str(dict(pre)))
out.append("column-header words among first 40 region lines, per module-table course: ")
for k, v in col.most_common(): out.append(f"  {v}: {k}")
out.append(f"dotted numbering lines like '1.1' (excluding grade-point ranges): {len(dotted)}")
out += ["  " + d for d in dotted[:10]]
# last course trailing pages
for p in L.PDFS:
    cs = E.courses(p); c = cs[-1]
    tail = [x for x in c["lines"] if re.search(r"Letter Grades and Grade Points", x[2])]
    out.append(f"{p.split('/')[0]}: last course {c['code']} pages {c['pages'][0]}-{c['pages'][-1]}; 'Letter Grades and Grade Points' at " + str([(x[0], x[1]) for x in tail]))
open("docs/evidence/regex_runs/nep26-se-core_misc_census.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out)[:3500])

# program-structure codes (pages < 16) vs detailed-syllabus codes (course starts)
rows = ["command: PYTHONIOENCODING=utf-8 python spikes/nep26-se-core_misc.py (structure vs detail codes)"]
for p in L.PDFS:
    ls = L.lines(p)
    struct = sorted({l.strip() for pg, j, l in ls if pg < 16 and re.fullmatch(r"\d{7}\s*", l)})
    det = sorted(c["code"] for c in E.courses(p))
    rows.append(f"{p.split('/')[0]}: in structure pages(<16) only: {sorted(set(struct)-set(det))}; in detail starts only: {sorted(set(det)-set(struct))}; structure={len(struct)} detail={len(det)}")
open("docs/evidence/regex_runs/nep26-se-core_structure_vs_detail_codes.txt", "w", encoding="utf-8").write("\n".join(rows) + "\n")
print("\n".join(rows))

# raw titles with runs of >=2 spaces; Hours/Hrs header counts; first non-blank line per page
rows = ["command: PYTHONIOENCODING=utf-8 python spikes/nep26-se-core_misc.py (titles, hours header words, page first lines)"]
for p in L.PDFS:
    ls = L.lines(p)
    raw = []
    for k, e in L.segment(ls):
        t = []
        m = k + 1
        while m < len(ls) and not L.TITLE_END.fullmatch(ls[m][2]):
            t.append(ls[m][2]); m += 1
        joined = " ".join(x.rstrip() if False else x for x in t)
        if re.search(r"\S {2,}\S", "".join(t)) or re.search(r"\S {2,}\S", joined): raw.append(ls[k][2].strip() + ":" + repr(joined))
    hh = collections.Counter(l.strip() for pg, j, l in ls if re.fullmatch(r"\s*(Hours|Hrs)\s*", l))
    rows.append(f"{p.split('/')[0]}: titles with 2+ consecutive spaces inside raw joined title: {raw}; hours header words: {dict(hh)}")
open("docs/evidence/regex_runs/nep26-se-core_titles_hours_words.txt", "w", encoding="utf-8").write("\n".join(rows) + "\n")
fl = ["command: PYTHONIOENCODING=utf-8 python spikes/nep26-se-core_misc.py (first non-blank line, first 40 chars, per page: pdf page: text)"]
for p in L.PDFS:
    ls = L.lines(p); first = {}
    for pg, j, l in ls:
        if pg not in first and l.strip(): first[pg] = l.strip()[:40]
    fl.append(p.split("/")[0] + " | " + " | ".join(f"{a}:{b}" for a, b in sorted(first.items())))
open("docs/evidence/regex_runs/nep26-se-core_page_first_lines.txt", "w", encoding="utf-8").write("\n".join(fl) + "\n")
# raw 60-line sample of Computational Theory (no header line) page 33, lines 104-163 (unedited)
import fitz
d = fitz.open(L.R + L.PDFS[3]); ls33 = d[32].get_text().split("\n")
open("docs/evidence/regex_runs/nep26-se-core_tcs_sample_p33_lines104-163.txt", "w", encoding="utf-8", newline="\n").write("\n".join(ls33[104:164]) + "\n")
print("\n".join(rows)[:900])
