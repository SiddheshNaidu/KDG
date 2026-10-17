"""Train a within-course prerequisite-edge model on the NEP corpus (labels: data/labelling/claude, provisional, Claude-labelled).
Pipeline: embed topics (all-MiniLM-L6-v2, offline) -> ALL ordered pairs per course (natural class balance) -> features -> XGBoost
-> hyper-parameters, threshold and margin chosen on VALIDATION courses only -> isotonic calibration on VALIDATION pairs.
TEST courses are never touched here (evaluate with scripts/eval_models.py once the model is frozen).
Usage: python scripts/train_nep.py --name nep2 --features nep2 [--no-position]"""
import os, sys, json, argparse
os.environ.setdefault("HF_HUB_OFFLINE", "1"); os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
import numpy as np, joblib
from sklearn.decomposition import PCA
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import average_precision_score
import xgboost as xgb
sys.path.insert(0, ".")
from app.ml.infer import Bundle, SubModel, embed as _embed, infer_course
from app.ml import features_nep
from app.ml.features_batch import pair_matrix as v5_matrix
from app.ml.features_v5 import FEATURE_NAMES as V5_NAMES

ap = argparse.ArgumentParser()
ap.add_argument("--name", default="nep2"); ap.add_argument("--features", default="nep2", choices=["v5", "nep2"]); ap.add_argument("--no-position", action="store_true"); ap.add_argument("--encoder", default=None, help="fine-tuned encoder folder inside app/ml")
args = ap.parse_args()
T = json.load(open("data/processed/topics_nep.json", encoding="utf-8"))
LABEL_DIR = os.environ.get("LABEL_DIR", "data/labelling/claude")
embed = lambda names: _embed(names, args.encoder)
NAMES = features_nep.FEATURE_NAMES if args.features == "nep2" else V5_NAMES
POS = {"signed_norm_position_gap", "signed_unit_gap", "same_unit", "a_earlier_unit", "gap", "abs_gap", "adj_fwd", "adj_bwd", "same_mod_gap",
       "i_pos_in_mod", "j_pos_in_mod", "i_mod_first", "j_mod_first", "i_mod_last", "col_rank", "row_rank"}
use = [i for i, f in enumerate(NAMES) if not (args.no_position and f in POS)]

def load(c):
    v = T[c]; ts = v["topics"]; ids = {t["id"]: i for i, t in enumerate(ts)}
    lab = json.load(open(f"{LABEL_DIR}/{c}.json"))["edges"]
    mods = {m["index"]: m["name"] for m in v["modules"]}
    names = [t["name"] for t in ts]; units = [t["module_idx"] for t in ts]; n = len(ts)
    pairs = [(i, j) for i in range(n) for j in range(n) if i != j]; gold = {(ids[e["a"]], ids[e["b"]]) for e in lab}
    return dict(ts=[dict(id=t["id"], name=t["name"], module=t["module_idx"]) for t in ts], names=names, units=units, n=n, pairs=pairs, gold=gold,
                y=np.array([int(p in gold) for p in pairs]), emb=embed(names), mods=mods, title=v["course_title"])

def matrix(d, pca):
    if args.features == "nep2":
        me = {m: e for m, e in zip(d["mods"].keys(), embed(list(d["mods"].values())))}
        return features_nep.pair_matrix(d["names"], d["units"], d["emb"], d["pairs"], pca, me, embed([d["title"]])[0])
    return v5_matrix(d["names"], d["units"], d["emb"], d["pairs"], pca)

split = {s: [c for c, v in T.items() if v["split"] == s] for s in ("train", "val")}
tr = {c: load(c) for c in split["train"]}; va = {c: load(c) for c in split["val"]}
rng = np.random.RandomState(0); dp = []
for d in tr.values():
    take = [k for k, p in enumerate(d["pairs"]) if p in d["gold"]] + list(rng.choice(len(d["pairs"]), min(400, len(d["pairs"])), replace=False))
    for k in take:
        i, j = d["pairs"][k]; dp.append(np.concatenate([d["emb"][j] - d["emb"][i], d["emb"][i] * d["emb"][j]]))
pca = PCA(n_components=32, random_state=42).fit(np.array(dp, dtype=np.float32))
Xtr = {c: matrix(d, pca) for c, d in tr.items()}; Xva = {c: matrix(d, pca) for c, d in va.items()}
X = np.vstack(list(Xtr.values()))[:, use]; y = np.concatenate([d["y"] for d in tr.values()])
Xv = np.vstack(list(Xva.values()))[:, use]; yv = np.concatenate([d["y"] for d in va.values()])
print(f"features {len(use)} | train pairs {len(y)} (pos {y.sum()}) | val pairs {len(yv)} (pos {yv.sum()})")
spw = float((len(y) - y.sum()) / max(1, y.sum())) ** 0.5
best = (-1, None, None)
for depth in (3, 4, 6):
    for mcw in (3, 10):
        m = xgb.XGBClassifier(n_estimators=800, max_depth=depth, learning_rate=0.04, subsample=0.8, colsample_bytree=0.7, min_child_weight=mcw,
                              scale_pos_weight=spw, eval_metric="aucpr", early_stopping_rounds=50, random_state=42, n_jobs=4)
        m.fit(X, y, eval_set=[(Xv, yv)], verbose=False)
        ap_v = average_precision_score(yv, m.predict_proba(Xv)[:, 1]); print(f"  depth {depth} mcw {mcw}: val PR-AUC {ap_v:.4f} (iters {m.best_iteration})")
        if ap_v > best[0]: best = (ap_v, m, (depth, mcw))
ap_v, clf, hp = best; print("chosen hyper-parameters (validation):", hp, "val PR-AUC %.4f (base rate %.4f)" % (ap_v, yv.mean()))
cal = IsotonicRegression(out_of_bounds="clip", y_min=0, y_max=1).fit(clf.predict_proba(Xv)[:, 1], yv)
bundle = Bundle.__new__(Bundle); bundle.name = args.name; bundle.model = SubModel(clf, use); bundle.pca = pca
bundle.meta = dict(threshold=0.5, margin=0.1, feature_set=args.features, reduce=False, encoder=args.encoder); bundle.enc = args.encoder; bundle.threshold = 0.5; bundle.margin = 0.1; bundle.calibrator = cal

def pair_scores(d, Xfull):
    return dict(zip(d["pairs"], map(float, bundle.proba(Xfull))))
Sva = {c: pair_scores(va[c], Xva[c]) for c in va}
def graph_f1(thr, mg):
    tp = pr = gd = 0
    for c, d in va.items():
        e = infer_course(d["ts"], bundle=bundle, threshold=thr, margin=mg, reduce=False, scores=Sva[c])
        ids = {t["id"]: i for i, t in enumerate(d["ts"])}; pred = {(ids[x.a], ids[x.b]) for x in e}
        tp += len(pred & d["gold"]); pr += len(pred); gd += len(d["gold"])
    P = tp / max(1, pr); R = tp / max(1, gd); return 2 * P * R / max(1e-9, P + R), P, R
sel = (-1, None)
for thr in (0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6):
    for mg in (0.0, 0.05, 0.1, 0.2):
        f, P, R = graph_f1(thr, mg)
        if f > sel[0]: sel = (f, (thr, mg, P, R))
thr, mg, P, R = sel[1]
print("validation-chosen calibrated threshold %.2f margin %.2f -> val graph F1 %.3f (P %.3f R %.3f)" % (thr, mg, sel[0], P, R))
joblib.dump(bundle.model, f"app/ml/model_artifact_{args.name}.joblib"); joblib.dump(pca, f"app/ml/pca_artifact_{args.name}.joblib"); joblib.dump(cal, f"app/ml/calibrator_{args.name}.joblib")
json.dump(dict(model_version=args.name, feature_set=args.features, features=[NAMES[i] for i in use], no_position=args.no_position, threshold=thr, margin=mg, reduce=False, encoder=args.encoder,
               hyper_parameters=dict(max_depth=hp[0], min_child_weight=hp[1]), val_pr_auc=round(ap_v, 4), val_graph_f1=round(sel[0], 4),
               train_courses=split["train"], val_courses=split["val"], labels="claude-provisional (not human verified)"),
          open(f"app/ml/model_artifact_{args.name}_meta.json", "w"), indent=1)
print("saved bundle", args.name)
