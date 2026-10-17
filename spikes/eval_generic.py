"""Spike: run generic table extractor over every PDF; compare with goldens by (pdf, code)."""
import sys, json, glob, re, collections, statistics as st, pathlib
sys.path.insert(0, "."); sys.path.insert(0, "spikes")
from app.parser.nep_tables import extract_course_tables
from app.parser.nep_topics import parse_course
from topic_validity import validate
def norm(s): return re.findall(r"[a-z0-9]+", s.lower())
def jac(a, b):
    A, B = set(a), set(b); return len(A & B) / len(A | B) if A | B else 0
def prf(pred, gold):
    P = [norm(x) for x in pred]; G = [norm(x) for x in gold]; used = set(); tp = 0
    for p in P:
        best = max(((jac(p, g), i) for i, g in enumerate(G) if i not in used), default=(0, None))
        if best[0] >= 0.6: used.add(best[1]); tp += 1
    # recall counted by gold covered
    pr = tp / len(P) if P else 0; rc = tp / len(G) if G else 0
    return pr, rc, (2 * pr * rc / (pr + rc) if pr + rc else 0)
gold = {}
for f in glob.glob("tests/golden/*/*.json"):
    g = json.load(open(f, encoding="utf-8")); gold[(g["source_pdf"], str(g["course_code"]))] = g
res = []; seen_pdf = set()
for pdf in sorted(glob.glob("data/raw/**/*.pdf", recursive=True)):
    p = pdf.replace("\\", "/")
    for ct in extract_course_tables(p):
        if not ct.has_module_table or ct.is_lab: continue
        c = parse_course(ct, p)
        topics = [t for m in c["modules"] for t in m["topics"]]
        viol = sum(1 for t in topics if validate(t))
        row = dict(pdf=p.split("/")[-1][:30], code=ct.code, mods=len(c["modules"]), topics=len(topics), viol=viol,
                   hours=sum(m["hours"] for m in c["modules"]), empty_mods=sum(1 for m in c["modules"] if not m["topics"]))
        g = gold.get((p, ct.code))
        if g:
            gt = [t for m in g["modules"] for t in m["topics"]]
            pr, rc, f = prf(topics, gt); row.update(g_mods=len(g["modules"]), g_topics=len(gt), P=round(pr, 2), R=round(rc, 2), F=round(f, 2))
        res.append(row)
json.dump(res, open("docs/evidence/baseline/generic_eval.json", "w"), indent=1)
print("courses with module table:", len(res), " mean topics", round(st.mean(r["topics"] for r in res), 1))
gr = [r for r in res if "F" in r]
print("golden-matched:", len(gr), "of", len(gold), " mean P/R/F:", [round(st.mean(r[k] for r in gr), 2) for k in "PRF"])
print("module count equals golden:", sum(1 for r in gr if r["mods"] == r["g_mods"]), "/", len(gr))
for r in gr: print(r["pdf"][:22].ljust(22), r["code"].ljust(8), "mods", r["mods"], "/", r["g_mods"], "topics", r["topics"], "/", r["g_topics"], "P", r["P"], "R", r["R"], "F", r["F"], "viol", r["viol"], "empty", r["empty_mods"])
print("golden not found:", [k[1] for k in gold if not any(r["code"] == k[1] for r in res)])
