"""Offline prerequisite-edge inference for ONE course (no network, no API key).

Scores topic pairs with the v5 XGBoost model (40 features, all-MiniLM-L6-v2 embeddings), then applies graph rules:
confidence threshold, in-degree <= 3, out-degree <= 6, no cycles, transitive reduction.
Two modes:
  direction_aware=False  production-like: forward pairs only (i<j); direction decided by syllabus order (what the old service did)
  direction_aware=True   every ordered pair is scored; per pair the direction with the higher probability wins if it beats the
                         other direction by `margin` (so the model, not list order, decides direction)."""
from __future__ import annotations
import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")        # offline inference doctrine: never reach the network
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
import json, pathlib
from dataclasses import dataclass
import numpy as np
import joblib
import networkx as nx

from .features_v5 import pair_features, set_pca

ML_DIR = pathlib.Path(__file__).resolve().parent
MAX_IN, MAX_OUT = 3, 6

@dataclass
class Edge:
    a: str
    b: str
    confidence: float
    reverse_confidence: float

class V5Model:
    _inst = None

    def __init__(self):
        self.model = joblib.load(ML_DIR / "model_artifact_v5.joblib")
        set_pca(joblib.load(ML_DIR / "pca_artifact_v5.joblib"))
        self.meta = json.load(open(ML_DIR / "model_artifact_v5_meta.json", encoding="utf-8"))
        self.threshold = float(self.meta["threshold"])
        from sentence_transformers import SentenceTransformer
        self.encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    @classmethod
    def get(cls):
        if cls._inst is None:
            cls._inst = cls()
        return cls._inst

    def embed(self, names):
        return self.encoder.encode([n.strip() or " " for n in names], convert_to_numpy=True, batch_size=32)

def score_pairs(topics, direction_aware=True):
    """topics: [{id,name,module}] in syllabus order. Returns dict {(i,j): p(i->j)} for the pairs that were scored."""
    m = V5Model.get(); n = len(topics)
    emb = m.embed([t["name"] for t in topics])
    pairs = [(i, j) for i in range(n) for j in range(n) if i != j and (direction_aware or i < j)]
    X = np.array([pair_features(topics[i]["name"], topics[j]["name"], n, topics[i]["module"], topics[j]["module"], i + 1, j + 1, emb[i], emb[j]) for i, j in pairs], dtype=np.float32)
    p = m.model.predict_proba(X)[:, 1]
    return dict(zip(pairs, map(float, p)))

def infer_course(topics, threshold=None, direction_aware=True, margin=0.10, reduce=True):
    m = V5Model.get(); thr = m.threshold if threshold is None else threshold
    n = len(topics); P = score_pairs(topics, direction_aware)
    cand = []
    for (i, j), p in P.items():
        if direction_aware:
            q = P.get((j, i), 0.0)
            if p < thr or p - q < margin:
                continue
        else:
            q = 0.0
            if p < thr:
                continue
            if topics[i]["module"] > topics[j]["module"]:
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
    if reduce:
        G = nx.transitive_reduction(G) if G.number_of_edges() else G
    return [Edge(topics[i]["id"], topics[j]["id"], round(kept[(i, j)][0], 4), round(kept[(i, j)][1], 4)) for i, j in G.edges() if (i, j) in kept]
