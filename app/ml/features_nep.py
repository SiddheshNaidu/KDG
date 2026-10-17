"""NEP feature set 'nep2' = the 40 v5 features + syllabus-structure and course-context extras (all computable offline from one parsed course).
Extras (names in EXTRA_NAMES) encode what makes prerequisite pairs in syllabi: neighbourhood in the list, position inside the module,
relation to module / course titles, name containment, and per-course relative similarity ranks."""
from __future__ import annotations
import re
import numpy as np
from .features_batch import pair_matrix as v5_matrix, _tokens
from .features_v5 import FEATURE_NAMES as V5_NAMES

EXTRA_NAMES = ["gap", "abs_gap", "adj_fwd", "adj_bwd", "same_mod_gap", "i_pos_in_mod", "j_pos_in_mod", "i_mod_first", "j_mod_first", "i_mod_last",
               "cos_i_module", "cos_j_module", "cos_i_title", "cos_j_title", "words_a", "words_b", "a_subset_b", "b_subset_a", "shared_tokens",
               "col_rank", "row_rank", "n_topics", "n_modules"]
FEATURE_NAMES = V5_NAMES + EXTRA_NAMES

def _unit(m):
    n = np.linalg.norm(m, axis=-1, keepdims=True); n[n == 0] = 1.0
    return m / n

def pair_matrix(names, units, emb, pairs, pca, mod_emb_by_unit=None, title_emb=None):
    """mod_emb_by_unit: {module_idx: embedding of module name} (optional); title_emb: embedding of course title (optional)."""
    n = len(names); I = np.array([p[0] for p in pairs]); J = np.array([p[1] for p in pairs])
    base = v5_matrix(names, units, emb, pairs, pca)
    e = _unit(np.asarray(emb, dtype=np.float32)); C = e @ e.T
    units = list(units); mods = sorted(set(units)); u = np.asarray(units)
    first = {m: min(k for k in range(n) if units[k] == m) for m in mods}; last = {m: max(k for k in range(n) if units[k] == m) for m in mods}
    size = {m: last[m] - first[m] + 1 for m in mods}
    pos_in = np.array([(k - first[units[k]]) / max(1, size[units[k]] - 1) for k in range(n)], dtype=np.float32)
    mfirst = np.array([1.0 if k == first[units[k]] else 0.0 for k in range(n)], dtype=np.float32)
    mlast = np.array([1.0 if k == last[units[k]] else 0.0 for k in range(n)], dtype=np.float32)
    if mod_emb_by_unit:
        cm = np.array([float(e[k] @ _unit(mod_emb_by_unit[units[k]])) if units[k] in mod_emb_by_unit else 0.0 for k in range(n)], dtype=np.float32)
    else:
        cm = np.zeros(n, dtype=np.float32)
    ct = (e @ _unit(np.asarray(title_emb, dtype=np.float32))).astype(np.float32) if title_emb is not None else np.zeros(n, dtype=np.float32)
    toks = [_tokens(x) for x in names]; words = np.array([len(str(x).split()) for x in names], dtype=np.float32)
    # relative ranks of cosine inside the course (excluding self)
    Cn = C.copy(); np.fill_diagonal(Cn, np.nan)
    col_rank = np.zeros((n, n), dtype=np.float32); row_rank = np.zeros((n, n), dtype=np.float32)
    for k in range(n):
        col = Cn[:, k]; ok = ~np.isnan(col); r = col[ok].argsort().argsort() / max(1, ok.sum() - 1); col_rank[ok, k] = r
        row = Cn[k, :]; ok = ~np.isnan(row); r = row[ok].argsort().argsort() / max(1, ok.sum() - 1); row_rank[k, ok] = r
    gap = (J - I).astype(np.float32); same = (u[I] == u[J])
    ex = np.stack([gap, np.abs(gap), (gap == 1).astype(np.float32), (gap == -1).astype(np.float32), np.where(same, gap, 0.0),
                   pos_in[I], pos_in[J], mfirst[I], mfirst[J], mlast[I], cm[I], cm[J], ct[I], ct[J], words[I], words[J],
                   np.array([1.0 if toks[i] and toks[i] <= toks[j] else 0.0 for i, j in pairs], dtype=np.float32),
                   np.array([1.0 if toks[j] and toks[j] <= toks[i] else 0.0 for i, j in pairs], dtype=np.float32),
                   np.array([len(toks[i] & toks[j]) for i, j in pairs], dtype=np.float32),
                   col_rank[I, J], row_rank[I, J], np.full(len(pairs), n, dtype=np.float32), np.full(len(pairs), len(mods), dtype=np.float32)], axis=1)
    return np.concatenate([base, ex.astype(np.float32)], axis=1)
