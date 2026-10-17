"""Spike: decoding variants on VALIDATION courses only (nep2 scores). Not part of the product."""
import os, sys, json
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import numpy as np, networkx as nx
sys.path.insert(0, ".")
from app.ml.infer import Bundle, score_pairs
T = json.load(open("data/processed/topics_nep.json", encoding="utf-8")); b = Bundle.get("nep2")
courses = [c for c, v in T.items() if v["split"] == "val"]; data = {}
for c in courses:
    v = T[c]; ts = [dict(id=t["id"], name=t["name"], module=t["module_idx"]) for t in v["topics"]]; ids = {t["id"]: i for i, t in enumerate(ts)}
    gold = {(ids[e["a"]], ids[e["b"]]) for e in json.load(open(f"data/labelling/claude/{c}.json"))["edges"]}
    ctx = dict(title=v["course_title"], module_names={m["index"]: m["name"] for m in v["modules"]})
    data[c] = (ts, gold, score_pairs(ts, b, True, ctx=ctx))
def evaluate(decode):
    tp = pr = gd = 0
    for c, (ts, gold, S) in data.items():
        pred = decode(len(ts), S); tp += len(pred & gold); pr += len(pred); gd += len(gold)
    P = tp / max(1, pr); R = tp / max(1, gd); return round(P, 3), round(R, 3), round(2 * P * R / max(1e-9, P + R), 3)
def dec_global(thr, mg):
    def f(n, S):
        out = set()
        for (i, j), p in S.items():
            if p >= thr and p - S.get((j, i), 0) >= mg: out.add((i, j))
        return out
    return f
def dec_topk(k, thr, ratio, mg=0.0):
    def f(n, S):
        out = set()
        for j in range(n):
            cands = sorted(((S[(i, j)], i) for i in range(n) if i != j and S[(i, j)] - S.get((j, i), 0) >= mg), reverse=True)
            if not cands or cands[0][0] < thr: continue
            for p, i in cands[:k]:
                if p >= thr and p >= ratio * cands[0][0]: out.add((i, j))
        return out
    return f
print("global threshold:", {t: evaluate(dec_global(t, 0.0)) for t in (0.15, 0.25, 0.35)})
for k in (1, 2, 3):
    for thr in (0.1, 0.15, 0.2, 0.3):
        for ratio in (0.5, 0.8):
            print(f"top-{k} per child thr {thr} ratio {ratio}:", evaluate(dec_topk(k, thr, ratio)))

print("\n-- graph-rule ablation (validation, calibrated scores) --")
import app.ml.infer as I
def run(thr, mg, reduce, mi, mo):
    I.MAX_IN, I.MAX_OUT = mi, mo; tp = pr = gd = 0
    for c, (ts, gold, S) in data.items():
        ids = {t["id"]: i for i, t in enumerate(ts)}
        e = I.infer_course(ts, bundle=b, threshold=thr, margin=mg, reduce=reduce, scores=S)
        pred = {(ids[x.a], ids[x.b]) for x in e}; tp += len(pred & gold); pr += len(pred); gd += len(gold)
    P = tp / max(1, pr); R = tp / max(1, gd); return round(P, 3), round(R, 3), round(2 * P * R / max(1e-9, P + R), 3), pr
for thr in (0.25, 0.35):
    print(f"thr {thr}: full rules", run(thr, 0.0, True, 3, 6), "| no reduction", run(thr, 0.0, False, 3, 6), "| caps off", run(thr, 0.0, True, 99, 99), "| both off", run(thr, 0.0, False, 99, 99), "| in-cap 4 no-reduction", run(thr, 0.0, False, 4, 8))
