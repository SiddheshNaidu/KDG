"""Directed-edge P/R/F1 of a model per department on the held-out test courses, next to the adjacent-topic baseline.
Also lists which departments the training split comes from. Usage:
  LABEL_DIR=data/labelling/final python scripts/eval_by_department.py nep6  > data/gold/eval_by_department_nep6.txt"""
import os, sys, json, collections
sys.path.insert(0, ".")
from app.ml.infer import Bundle, score_pairs, infer_course

LABEL_DIR = os.environ.get("LABEL_DIR", "data/labelling/final")
T = json.load(open("data/processed/topics_nep.json", encoding="utf-8"))
DEPTS = [("EXTC", "E&TC"), ("Chemical", "Chemical"), ("Mechanical", "Mechanical"), ("6.35", "Mechanical"), ("6.40", "Chemical"),
         ("Information-Technology", "IT"), ("6.22-NIT", "IT"), ("nep_sem5_6", "IT"), ("6.34", "IT"), ("Computer-Engineering", "Computer"),
         ("6.24", "Computer"), ("CSE-AIML", "CSE (AI&ML)"), ("6.14N", "CSE (AI&ML)"), ("AI-DS", "AI&DS"), ("AI-ML", "AI&ML"), ("AIML", "AI&ML"),
         ("Data-Science", "Data Science"), ("DS_sem", "Data Science"), ("Civil", "Civil"), ("Electrical-Computer", "Electrical & Computer"),
         ("Electrical", "Electrical"), ("Automation", "Mech. Automation"), ("Computer-Science", "CSE"), ("6.54", "CSE"), ("6.19", "E&TC"),
         ("6.20", "AI&DS"), ("6.21", "AI&ML"), ("6.23", "Civil/Mech"), ("6.28", "Data Science"), ("6.29", "Electrical"), ("6.39", "Data Science"),
         ("6.44", "Mech. Automation"), ("6.51", "Electrical & Computer"), ("6.9N", "AI&ML")]

def dept(c):
    f = " ".join(T[c]["source_pdfs"])
    d = next((name for key, name in DEPTS if key in f), "other")
    sem = "Sem 5/6" if "Sem5_6" in f or "sem5_6" in f.lower() else "Sem 3/4" if "III-IV" in f else "Sem 1/2"
    return f"{d} {sem}"

def prf(tp, pr, gd):
    P = tp / max(1, pr); R = tp / max(1, gd); return P, R, 2 * P * R / max(1e-9, P + R)

b = Bundle.get(sys.argv[1] if len(sys.argv) > 1 else "nep6")
have = lambda c: os.path.exists(f"{LABEL_DIR}/{c}.json")
print("training departments:", dict(collections.Counter(dept(c) for c, v in T.items() if v["split"] == "train" and have(c))))
print("validation departments:", dict(collections.Counter(dept(c) for c, v in T.items() if v["split"] == "val" and have(c))))
agg = collections.defaultdict(collections.Counter); rows = []
for c, v in T.items():
    if v["split"] != "test" or not have(c): continue
    ts = [dict(id=t["id"], name=t["name"], module=t["module_idx"]) for t in v["topics"]]
    ctx = dict(title=v["course_title"], module_names={m["index"]: m["name"] for m in v["modules"]})
    gold = {(e["a"], e["b"]) for e in json.load(open(f"{LABEL_DIR}/{c}.json"))["edges"]}
    pred = {(e.a, e.b) for e in infer_course(ts, bundle=b, ctx=ctx)}
    base = {(ts[i]["id"], ts[i + 1]["id"]) for i in range(len(ts) - 1) if ts[i]["module"] == ts[i + 1]["module"]}
    g = dept(c); a = agg[g]
    a["tp"] += len(pred & gold); a["pr"] += len(pred); a["gd"] += len(gold); a["btp"] += len(base & gold); a["bpr"] += len(base); a["n"] += 1
    rows.append((g, c, v["course_title"][:38], len(ts), len(gold), round(prf(len(pred & gold), len(pred), len(gold))[2], 3),
                 round(prf(len(base & gold), len(base), len(gold))[2], 3)))
print(f"\nmodel {b.name} (threshold {b.threshold})\ndepartment | courses | gold edges | P | R | F1 | baseline F1 | model - baseline")
tot = collections.Counter()
for g, a in sorted(agg.items()):
    P, R, F = prf(a["tp"], a["pr"], a["gd"]); bF = prf(a["btp"], a["bpr"], a["gd"])[2]; tot.update(a)
    print(f"{g} | {a['n']} | {a['gd']} | {P:.3f} | {R:.3f} | {F:.3f} | {bF:.3f} | {F - bF:+.3f}")
P, R, F = prf(tot["tp"], tot["pr"], tot["gd"]); bF = prf(tot["btp"], tot["bpr"], tot["gd"])[2]
print(f"ALL | {tot['n']} | {tot['gd']} | {P:.3f} | {R:.3f} | {F:.3f} | {bF:.3f} | {F - bF:+.3f}")
print("\nper course: department | code | title | topics | gold | F1 | baseline F1")
for r in sorted(rows): print(*r, sep=" | ")
