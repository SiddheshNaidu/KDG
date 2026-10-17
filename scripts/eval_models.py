"""Frozen-model evaluation on the TEST courses (two PDFs never used for training, validation or any choice): Chemical Engineering
(6.40) and Mechanical Engineering (6.35). Gold = provisional edges labelled by Claude (NOT human verified).
Each model is decoded with ITS OWN validation-chosen settings (v5: its served threshold, forward pairs, transitive reduction).
Usage: python scripts/eval_models.py v5 nep2 [more bundle names]"""
import os, sys, json
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import numpy as np
from sklearn.metrics import average_precision_score
sys.path.insert(0, ".")
from app.ml.infer import Bundle, score_pairs, infer_course
T = json.load(open("data/processed/topics_nep.json", encoding="utf-8"))
test = [c for c, v in T.items() if v["split"] == "test"]
def course(c):
    v = T[c]; ts = [dict(id=t["id"], name=t["name"], module=t["module_idx"]) for t in v["topics"]]; ids = {t["id"]: i for i, t in enumerate(ts)}
    gold = {(ids[e["a"]], ids[e["b"]]) for e in json.load(open(os.environ.get("LABEL_DIR", "data/labelling/claude") + f"/{c}.json"))["edges"]}
    return ts, ids, gold, dict(title=v["course_title"], module_names={m["index"]: m["name"] for m in v["modules"]})
def prf(tp, pr, gd):
    P = tp / max(1, pr); R = tp / max(1, gd); return P, R, 2 * P * R / max(1e-9, P + R)
def run(name):
    b = Bundle.get(name); v5 = (name == "v5"); tp = pr = gd = utp = 0; dir_ok = linked = 0; ys = []; ps = []; per = {}; cal = []
    for c in test:
        ts, ids, gold, ctx = course(c)
        S = score_pairs(ts, b, direction_aware=not v5, ctx=ctx)
        e = infer_course(ts, bundle=b, direction_aware=not v5, scores=S, reduce=True if v5 else None, ctx=ctx)
        pred = {(ids[x.a], ids[x.b]) for x in e}; und = lambda s: {frozenset(p) for p in s}
        t = len(pred & gold); tp += t; pr += len(pred); gd += len(gold); ut = len(und(pred) & und(gold)); utp += ut
        linked += ut; dir_ok += t
        per[c] = prf(t, len(pred), len(gold))[2]
        for (i, j), p in S.items():
            ys.append(int((i, j) in gold)); ps.append(p)
            cal.append((p, int((i, j) in gold)))
    P, R, F = prf(tp, pr, gd); uP, uR, uF = prf(utp, pr, gd)
    # all-pairs scores exist only for direction-aware bundles (v5 scored forward pairs only: PR-AUC computed on those pairs, gold edges that point backwards count as misses)
    full = sum(1 for c in test for _ in [0])
    return dict(P=P, R=R, F=F, uF=uF, dir_acc=(dir_ok / max(1, linked)), ap=average_precision_score(ys, ps), per=per, edges=pr, gold=gd, cal=cal, n_pairs=len(ys), base=np.mean(ys))
def baselines():
    tp = pr = gd = 0; tp3 = pr3 = 0
    for c in test:
        ts, ids, gold, _ = course(c); a = {(i, i + 1) for i in range(len(ts) - 1) if ts[i]["module"] == ts[i + 1]["module"]}
        w = {(i, i + k) for i in range(len(ts)) for k in (1, 2, 3) if i + k < len(ts) and ts[i]["module"] == ts[i + k]["module"]}
        tp += len(a & gold); pr += len(a); gd += len(gold); tp3 += len(w & gold); pr3 += len(w)
    return prf(tp, pr, gd), prf(tp3, pr3, gd)
def reliability(cal, bins=(0, .1, .2, .3, .5, .7, 1.01)):
    cal = np.array(cal); out = []; ece = 0.0
    for lo, hi in zip(bins[:-1], bins[1:]):
        m = (cal[:, 0] >= lo) & (cal[:, 0] < hi)
        if m.sum(): out.append((f"{lo:.1f}-{min(hi,1):.1f}", int(m.sum()), round(float(cal[m, 0].mean()), 3), round(float(cal[m, 1].mean()), 3))); ece += m.sum() / len(cal) * abs(cal[m, 0].mean() - cal[m, 1].mean())
    return out, ece
if __name__ == "__main__":
    print("test courses:", {c: (T[c]["course_title"][:22], T[c]["n_topics"]) for c in test})
    (bp, br, bf), (wp, wr, wf) = baselines()
    print(f"\nbaseline adjacent-in-module: P {bp:.3f} R {br:.3f} F1 {bf:.3f} | window-3-in-module: P {wp:.3f} R {wr:.3f} F1 {wf:.3f}")
    print("\nmodel | directed P | R | F1 | undirected F1 | direction acc of linked pairs | PR-AUC (all pairs scored) | pred edges / gold")
    res = {}
    for name in sys.argv[1:]:
        r = res[name] = run(name)
        print(f"{name} | {r['P']:.3f} | {r['R']:.3f} | {r['F']:.3f} | {r['uF']:.3f} | {r['dir_acc']:.3f} | {r['ap']:.3f} (base rate {r['base']:.3f}) | {r['edges']}/{r['gold']}")
    for name, r in res.items():
        print(f"\n[{name}] per-course directed F1:", {c: round(f, 2) for c, f in r["per"].items()})
        rel, ece = reliability(r["cal"]); print(f"[{name}] reliability (bin, n pairs, mean predicted, observed rate):", rel, "ECE %.4f" % ece)
