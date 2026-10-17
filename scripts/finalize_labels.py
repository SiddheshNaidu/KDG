"""Final labels per course = edges both passes agree on + disputed edges kept by the independent adjudicator.
Writes data/labelling/final/<course>.json and prints counts. Usage: python scripts/finalize_labels.py"""
import json, pathlib, collections
M = pathlib.Path("data/labelling/merged"); AD = pathlib.Path("data/labelling/adjudicated"); IN = pathlib.Path("data/labelling/adjudicate"); OUT = pathlib.Path("data/labelling/final"); OUT.mkdir(exist_ok=True)
T = json.load(open("data/processed/topics_nep.json", encoding="utf-8")); tot = collections.Counter(); rows = []
for f in sorted(M.glob("*.json")):
    c = f.stem
    if not (IN / f.name).exists(): continue      # excluded course (no adjudication input)
    m = json.load(open(f)); agree = {tuple(e) for e in m["agree"]}
    cand = {x["i"]: (x["a"], x["b"]) for x in json.load(open(IN / f.name, encoding="utf-8"))["candidates"]}
    keep = set(json.load(open(AD / f.name))["keep"]) if (AD / f.name).exists() else None
    if keep is None: print("MISSING adjudication for", c); continue
    kept = {cand[i] for i in keep}; edges = sorted(agree | kept)
    json.dump(dict(label_source="2 independent passes + independent adjudication (AI labellers; not human verified)", split=T[c]["split"], edges=[dict(a=a, b=b) for a, b in edges]), open(OUT / f.name, "w"))
    rows.append((c, T[c]["split"], len(agree), len(kept), len(cand))); tot["agree"] += len(agree); tot["kept"] += len(kept); tot["cand"] += len(cand)
print("courses", len(rows), "| agreed", tot["agree"], "| disputed candidates", tot["cand"], "| kept by adjudicator", tot["kept"], "(%.0f%%)" % (100 * tot["kept"] / max(1, tot["cand"])), "| final edges", tot["agree"] + tot["kept"])
