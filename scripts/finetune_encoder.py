"""Fine-tune the MiniLM sentence encoder on TRAIN-course prerequisite pairs (anchor = prerequisite topic, positive = dependent topic)
with in-batch negatives, so embeddings reflect syllabus relatedness. Validation courses/TEST courses are never used.
Usage: python scripts/finetune_encoder.py [--epochs 2] [--out app/ml/encoder_nep3]"""
import os, sys, json, argparse, random
os.environ.setdefault("HF_HUB_OFFLINE", "1"); os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
from sentence_transformers import SentenceTransformer, InputExample
ap = argparse.ArgumentParser(); ap.add_argument("--epochs", type=int, default=2); ap.add_argument("--out", default="app/ml/encoder_nep3"); args = ap.parse_args()
T = json.load(open("data/processed/topics_nep.json", encoding="utf-8")); ex = []
for c, v in T.items():
    if v["split"] != "train": continue
    nm = {t["id"]: t["name"] for t in v["topics"]}
    for e in json.load(open(f"data/labelling/claude/{c}.json"))["edges"]:
        ex.append(InputExample(texts=[nm[e["a"]], nm[e["b"]]]))
random.Random(0).shuffle(ex); print("training pairs", len(ex))
import torch, torch.nn.functional as F
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2"); model.train()
opt = torch.optim.AdamW(model.parameters(), lr=2e-5)
def emb(texts):
    feats = model.tokenize(texts); return model(feats)["sentence_embedding"]
steps = 0
for ep in range(args.epochs):
    random.Random(ep).shuffle(ex); tot = 0.0; nb = 0
    for k in range(0, len(ex), 32):
        batch = ex[k:k + 32]
        if len(batch) < 4: continue
        a = F.normalize(emb([b.texts[0] for b in batch]), dim=-1); b = F.normalize(emb([b.texts[1] for b in batch]), dim=-1)
        sim = a @ b.T * 20.0; lab = torch.arange(len(batch))
        loss = (F.cross_entropy(sim, lab) + F.cross_entropy(sim.T, lab)) / 2     # symmetric in-batch contrastive loss
        opt.zero_grad(); loss.backward(); opt.step(); tot += float(loss); nb += 1
    print(f"epoch {ep + 1}: mean loss {tot / max(1, nb):.4f}")
model.eval(); model.save(args.out); print("saved", args.out)
