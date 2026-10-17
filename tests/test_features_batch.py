import sys, random
import numpy as np, joblib
sys.path.insert(0, ".")
from app.ml.features_v5 import pair_features
from app.ml.features_batch import pair_matrix

def test_parity_with_pair_features():
    pca = joblib.load("app/ml/pca_artifact_v5.joblib"); rng = np.random.RandomState(0)
    names = ["Basic Concepts of Stack", "Stack Operations", "Linear Algebra Introduction", "Binary Tree Traversal", "Tree", "Probability of events"]
    units = [1, 1, 2, 3, 3, 4]; emb = rng.randn(len(names), 384).astype(np.float32)
    pairs = [(i, j) for i in range(len(names)) for j in range(len(names)) if i != j]
    X = pair_matrix(names, units, emb, pairs, pca)
    for k, (i, j) in enumerate(pairs):
        ref = pair_features(names[i], names[j], len(names), units[i], units[j], i + 1, j + 1, emb[i], emb[j], pca=pca)
        assert np.allclose(X[k], ref, atol=1e-4), (i, j)
