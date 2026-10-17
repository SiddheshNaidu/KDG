"""Evaluate the v5 edge model on courses it never saw, against provisional gold (labelled by Claude, not human-verified).
Usage: python scripts/eval_unknown.py [gold_json]    (default data/gold/unknown_chem_gold.json)
Reports: directed / undirected edge P-R-F1 at the served threshold and a sweep, PR-AUC over ALL ordered pairs (natural class balance),
reachability-closure F1 (tolerates a missing intermediate topic), reliability of confidence, and two trivial baselines."""
import sys, json, itertools, collections
import numpy as np
import networkx as nx
from sklearn.metrics import average_precision_score
sys.path.insert(0, ".")
from app.ml.infer import infer_course, score_pairs, V5Model

gold_path = sys.argv[1] if len(sys.argv) > 1 else "data/gold/unknown_chem_gold.json"
G = json.load(open(gold_path, encoding="utf-8"))["courses"]
T = json.load(open("data/processed/topics_nep.json", encoding="utf-8"))

def prf(pred, gold):
    tp = len(pred & gold); p = tp / len(pred) if pred else 0.0; r = tp / len(gold) if gold else 0.0
    return p, r, (2 * p * r / (p + r) if p + r else 0.0)

def closure(edges):
    g = nx.DiGraph(list(edges)); return {(a, b) for a in g for b in nx.descendants(g, a)}

def run(thr, aware):
    tot = collections.Counter(); per = {}
    allp, allg = [], []
    for c, ges in G.items():
        topics = [dict(id=t["id"], name=t["name"], module=t["module_idx"]) for t in T[c]["topics"]]
        gold = {(e["a"], e["b"]) for e in ges}
        pred_e = infer_course(topics, threshold=thr, direction_aware=aware)
        pred = {(e.a, e.b) for e in pred_e}
        und = lambda s: {frozenset(x) for x in s}
        d = prf(pred, gold); u = prf(und(pred), und(gold)); cl = prf(closure(pred), closure(gold))
        per[c] = (len(topics), len(gold), len(pred), d, u, cl)
        tot["tp"] += len(pred & gold); tot["pred"] += len(pred); tot["gold"] += len(gold)
        tot["utp"] += len(und(pred) & und(gold)); tot["upred"] += len(und(pred)); tot["ugold"] += len(und(gold))
    P = tot["tp"] / max(1, tot["pred"]); R = tot["tp"] / max(1, tot["gold"]); F = 2 * P * R / max(1e-9, P + R)
    uP = tot["utp"] / max(1, tot["upred"]); uR = tot["utp"] / max(1, tot["ugold"]); uF = 2 * uP * uR / max(1e-9, uP + uR)
    return per, (P, R, F), (uP, uR, uF), tot

def pr_auc_all():
    ys, ps, ys_und, ps_und = [], [], [], []
    for c, ges in G.items():
        topics = [dict(id=t["id"], name=t["name"], module=t["module_idx"]) for t in T[c]["topics"]]
        S = score_pairs(topics, True); gold = {(e["a"], e["b"]) for e in ges}
        for (i, j), p in S.items():
            ys.append(int((topics[i]["id"], topics[j]["id"]) in gold)); ps.append(p)
    return average_precision_score(ys, ps), sum(ys) / len(ys)

def baselines():
    out = {}
    for name in ("adjacent_in_module", "position_only_forward_window3"):
        tp = pr = gd = 0
        for c, ges in G.items():
            ts = T[c]["topics"]; gold = {(e["a"], e["b"]) for e in ges}; pred = set()
            for i in range(len(ts) - 1):
                if name == "adjacent_in_module" and ts[i]["module_idx"] == ts[i + 1]["module_idx"]:
                    pred.add((ts[i]["id"], ts[i + 1]["id"]))
                if name.startswith("position_only"):
                    for k in range(1, 4):
                        if i + k < len(ts) and ts[i]["module_idx"] == ts[i + k]["module_idx"]:
                            pred.add((ts[i]["id"], ts[i + k]["id"]))
            tp += len(pred & gold); pr += len(pred); gd += len(gold)
        P = tp / max(1, pr); R = tp / max(1, gd); out[name] = (round(P, 3), round(R, 3), round(2 * P * R / max(1e-9, P + R), 3))
    return out

if __name__ == "__main__":
    meta = V5Model.get().meta
    print("model v5, served threshold", meta["threshold"], "| its own held-out test (IT courses, 3:1 negatives):", meta["metrics"]["test_f1"], "F1,", meta["metrics"]["test_pr_auc"], "PR-AUC")
    print("courses:", {c: (T[c]["course_title"][:24], len(G[c])) for c in G})
    ap, base = pr_auc_all()
    print(f"\nPR-AUC over ALL ordered pairs (natural balance, base rate {base:.3f}): {ap:.3f}")
    print("baselines (directed P,R,F1):", baselines())
    for aware in (False, True):
        print(f"\n== {'direction-aware' if aware else 'production-like (forward pairs, direction by list order)'} ==")
        print("thr   directedP  R    F1   | undirectedP  R    F1")
        for thr in (0.2, 0.29, 0.4, 0.5, 0.6, 0.7):
            per, d, u, tot = run(thr, aware)
            print(f"{thr:.2f}   {d[0]:.3f}  {d[1]:.3f}  {d[2]:.3f}  |  {u[0]:.3f}  {u[1]:.3f}  {u[2]:.3f}   (pred {tot['pred']}, gold {tot['gold']})")
        per, d, u, tot = run(meta["threshold"], aware)
        print("per course @served threshold (topics, gold, pred, directed PRF, undirected PRF, closure PRF):")
        for c, (n, g, p, dd, uu, cl) in per.items():
            print(f"  {c} {T[c]['course_title'][:26]:26} {n:3} {g:3} {p:3}  D={dd[2]:.2f}  U={uu[2]:.2f}  closure={cl[2]:.2f}")
