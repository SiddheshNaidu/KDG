"""Spike: per-PDF layout marker counts (lines matched, anchored to a whole stripped line unless noted)."""
import fitz, re, sys, glob, csv, pathlib
M = {
 "detailed_syllabus_hdr": r"^DETAIL(ED)? SYLLABUS\s*:?$",
 "module_detailed_content": r"^Detailed Contents?$",
 "total_hours": r"^Total Hours?$",
 "self_learning": r"^Self[- ]Learning Topics?\s*:?",
 "self_study": r"^Self[- ]Study\s*:",
 "prereq_line": r"^Prerequisite$",
 "code_7_8_digits_alone": r"^\d{7,8}$",
 "code_with_letters_alone": r"^[A-Z]{2,5}\d{3,5}$",
 "draft_watermark": r"DRAFT",
 "roman_module_alone": r"^(I|II|III|IV|V|VI)$",
 "dotted_subitem": r"^\d\.\d+\s",
 "course_outcomes": r"^Course Outcomes?\b",
}
rows=[]
for p in sorted(pathlib.Path("data/raw").rglob("*.pdf")):
    d=fitz.open(p); lines=[l.strip() for pg in d for l in pg.get_text().split("\n")]
    r={"path":str(p.relative_to("data/raw")).replace("\\","/"),"pages":len(d)}
    for k,rx in M.items(): r[k]=sum(1 for l in lines if re.search(rx,l,re.I if k in("detailed_syllabus_hdr","draft_watermark") else 0))
    rows.append(r)
w=csv.DictWriter(open("docs/evidence/signatures.csv","w",newline="",encoding="utf-8"),fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
for r in rows: print(r["path"].split("/")[-1][:34].ljust(34),*[f"{k[:6]}={v}" for k,v in r.items() if k not in("path",)])
