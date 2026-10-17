import sys, glob, json, collections
sys.path.insert(0, ".")
from app.parser.nep_tables import extract_course_tables
from app.parser.nep_topics import parse_course
from app.parser.nep_gate import gate_course
rows = []
for pdf in sorted(glob.glob("data/raw/**/*.pdf", recursive=True)):
    p = pdf.replace("\\", "/")
    for ct in extract_course_tables(p):
        if not ct.has_module_table and not ct.is_lab: continue
        c = parse_course(ct, p); g = gate_course(c)
        rows.append(dict(pdf=p.split("/")[-1], code=c["course_code"], title=c["title"][:40], **g))
json.dump(rows, open("docs/evidence/baseline/gate_stats.json", "w"), indent=1)
acc = [r for r in rows if r["accepted"]]
print("evaluated", len(rows), "accepted", len(acc))
rc = collections.Counter(x.split(":")[0].split("_")[0] + "_" + x.split(":")[0].split("_")[1] if "_" in x else x for r in rows for x in r["reasons"])
print("reject reasons:", dict(collections.Counter(re_.split(":")[0] for r in rows for re_ in r["reasons"])))
print("hours sum distribution (accepted):", dict(collections.Counter(r["total_hours"] for r in acc).most_common(8)))
print("hours sum distribution (all non-lab):", dict(collections.Counter(r["total_hours"] for r in rows if "lab_course" not in "".join(r["reasons"])).most_common(8)))
