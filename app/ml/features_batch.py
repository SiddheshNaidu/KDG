"""Vectorised version of features_v5.pair_features (identical 40 features, same order). Parity is tested in tests/test_features_batch.py."""
from __future__ import annotations
import re
import numpy as np
from .features_v5 import FOUNDATIONAL_KEYWORDS

def _tokens(s: str) -> frozenset:
    return frozenset(re.findall(r"\w+", str(s).lower()))

def pair_matrix(names, units, emb, pairs, pca):
    """names: topic names in syllabus order; units: module index per topic; emb: (n,384); pairs: [(i,j)] meaning i -> j; positions are 1-based like training."""
    n = len(names); I = np.array([p[0] for p in pairs]); J = np.array([p[1] for p in pairs])
    e = np.asarray(emb, dtype=np.float32); norms = np.linalg.norm(e, axis=1)
    safe = np.where(norms > 1e-9, norms, 1.0)
    cos = np.where((norms[I] > 1e-9) & (norms[J] > 1e-9), (e[I] * e[J]).sum(1) / (safe[I] * safe[J]), 0.0)
    pos_gap = ((J + 1) - (I + 1)).astype(np.float32) / max(1.0, float(n))
    u = np.asarray(units, dtype=np.float32); unit_gap = u[J] - u[I]
    same_unit = (u[I].astype(int) == u[J].astype(int)).astype(np.float32)
    a_earlier = (u[I] < u[J]).astype(np.float32)
    toks = [_tokens(x) for x in names]; low = [str(x).strip().lower() for x in names]
    found = np.array([1.0 if any(t in FOUNDATIONAL_KEYWORDS for t in tk) else 0.0 for tk in toks], dtype=np.float32)
    kw = np.empty(len(pairs), dtype=np.float32); nin = np.empty(len(pairs), dtype=np.float32)
    for k, (i, j) in enumerate(pairs):
        a, b = toks[i], toks[j]
        kw[k] = len(a & b) / len(a | b) if a and b else 0.0
        nin[k] = 1.0 if (low[i] and low[i] in low[j]) else 0.0
    base = np.stack([cos, pos_gap, unit_gap, same_unit, a_earlier, kw, nin, found[I]], axis=1).astype(np.float32)
    dp = np.concatenate([e[J] - e[I], e[I] * e[J]], axis=1).astype(np.float32)
    return np.concatenate([base, pca.transform(dp).astype(np.float32)], axis=1)
