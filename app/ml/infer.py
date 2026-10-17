"""Offline prerequisite-edge inference for ONE course (no network, no API key).

A `Bundle` is a trained edge model: XGBoost classifier + PCA (+ optional isotonic calibrator) + meta (threshold, margin).
Pair scores are turned into a graph with rules: confidence threshold, direction margin, in-degree <= 3, out-degree <= 6,
no cycles, transitive reduction.
  direction_aware=True   every ordered pair is scored; per pair the direction with the higher probability wins if it beats
                         the other direction by `margin` (the model, not list order, decides direction)
  direction_aware=False  v5 production behaviour: forward pairs only (i<j); direction fixed by syllabus order."""
from __future__ import annotations
import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")        # offline inference doctrine: never reach the network
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
import json, pathlib
from dataclasses import dataclass
import numpy as np
import joblib
import networkx as nx

from .features_batch import pair_matrix
from . import features_nep

ML_DIR = pathlib.Path(__file__).resolve().parent
MAX_IN, MAX_OUT = 3, 6
_ENCODERS = {}

def encoder(path=None):
    """path: folder name inside app/ml of a fine-tuned encoder, or None for the base all-MiniLM-L6-v2 (cached locally, offline)."""
    key = path or "base"
    if key not in _ENCODERS:
        from sentence_transformers import SentenceTransformer
        _ENCODERS[key] = SentenceTransformer(str(ML_DIR / path) if path else "sentence-transformers/all-MiniLM-L6-v2")
    return _ENCODERS[key]

def embed(names, enc=None):
    return encoder(enc).encode([n.strip() or " " for n in names], convert_to_numpy=True, batch_size=32)

class SubModel:
    """XGBoost model trained on a column subset of the feature matrix; accepts the full matrix and slices."""
    def __init__(self, model, use):
        self.m = model; self.use = list(use)
    def predict_proba(self, Z):
        return self.m.predict_proba(Z[:, self.use])

@dataclass
class Edge:
    a: str
    b: str
    confidence: float          # calibrated when the bundle has a calibrator, else the raw model probability
    reverse_confidence: float  # same quantity for the opposite direction (direction margin evidence)

class Bundle:
    _cache: dict = {}

    def __init__(self, name: str = "v5"):
        self.name = name
        self.model = joblib.load(ML_DIR / f"model_artifact_{name}.joblib")
        self.pca = joblib.load(ML_DIR / f"pca_artifact_{name}.joblib")
        self.meta = json.load(open(ML_DIR / f"model_artifact_{name}_meta.json", encoding="utf-8"))
        self.threshold = float(self.meta["threshold"])
        self.margin = float(self.meta.get("margin", 0.10))
        self.enc = self.meta.get("encoder")
        cal = ML_DIR / f"calibrator_{name}.joblib"
        self.calibrator = joblib.load(cal) if cal.exists() else None

    @classmethod
    def get(cls, name: str = "v5"):
        if name not in cls._cache:
            cls._cache[name] = cls(name)
        return cls._cache[name]

    def embed(self, names):
        return embed(names, getattr(self, "enc", None))

    def proba(self, X):
        p = self.model.predict_proba(X)[:, 1]
        return self.calibrator.predict(p) if self.calibrator is not None else p

def feature_matrix(topics, bundle, emb, pairs, ctx=None):
    names = [t["name"] for t in topics]; units = [t["module"] for t in topics]
    if bundle.meta.get("feature_set") == "nep2":
        ctx = ctx or {}
        mods = ctx.get("module_names") or {}
        mod_emb = {m: v for m, v in zip(mods.keys(), bundle.embed(list(mods.values())))} if mods else None
        title_emb = bundle.embed([ctx["title"]])[0] if ctx.get("title") else None
        return features_nep.pair_matrix(names, units, emb, pairs, bundle.pca, mod_emb, title_emb)
    return pair_matrix(names, units, emb, pairs, bundle.pca)

def score_pairs(topics, bundle: Bundle, direction_aware=True, raw=False, ctx=None):
    """topics: [{id,name,module}] in syllabus order. ctx (nep2 only): {'title': str, 'module_names': {idx: name}}.
    Returns {(i,j): p(i->j)} (calibrated unless raw=True)."""
    n = len(topics); emb = bundle.embed([t["name"] for t in topics])
    pairs = [(i, j) for i in range(n) for j in range(n) if i != j and (direction_aware or i < j)]
    X = feature_matrix(topics, bundle, emb, pairs, ctx)
    p = bundle.model.predict_proba(X)[:, 1] if raw else bundle.proba(X)
    return dict(zip(pairs, map(float, p)))

def infer_course(topics, bundle: Bundle | None = None, threshold=None, direction_aware=True, margin=None, reduce=None, scores=None, ctx=None):
    bundle = bundle or Bundle.get("v5")
    thr = bundle.threshold if threshold is None else threshold
    mg = bundle.margin if margin is None else margin
    reduce = bundle.meta.get("reduce", True) if reduce is None else reduce
    n = len(topics); P = scores if scores is not None else score_pairs(topics, bundle, direction_aware, ctx=ctx)
    cand = []
    for (i, j), p in P.items():
        if direction_aware:
            q = P.get((j, i), 0.0)
            if p < thr or p - q < mg:
                continue
        else:
            q = 0.0
            if p < thr or topics[i]["module"] > topics[j]["module"]:
                continue
        cand.append((p, i, j, q))
    cand.sort(reverse=True)
    G = nx.DiGraph(); G.add_nodes_from(range(n)); kept = {}
    for p, i, j, q in cand:
        if G.in_degree(j) >= MAX_IN or G.out_degree(i) >= MAX_OUT:
            continue
        G.add_edge(i, j)
        if not nx.is_directed_acyclic_graph(G):
            G.remove_edge(i, j); continue
        kept[(i, j)] = (p, q)
    if reduce and G.number_of_edges():
        G = nx.transitive_reduction(G)
    return [Edge(topics[i]["id"], topics[j]["id"], round(kept[(i, j)][0], 4), round(kept[(i, j)][1], 4)) for i, j in G.edges() if (i, j) in kept]
