"""Export graphs for the standalone demo: nep2 edges (accepted + uncertain band), Kahn levels, comparison with provisional gold.
Courses = the TEST split (two PDFs the model never saw). Output: demo/graph_data.json"""
import os, sys, json
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import networkx as nx
sys.path.insert(0, ".")
from app.ml.infer import Bundle, score_pairs, infer_course
T = json.load(open("data/processed/topics_nep.json", encoding="utf-8")); MODEL = os.environ.get("MODEL", "nep4"); b = Bundle.get(MODEL)
LOW = 0.10   # below the accepted threshold but worth showing as "uncertain"
out = dict(model=dict(name=MODEL, accepted_threshold=b.threshold, uncertain_threshold=LOW, calibrated=True,
                      note="confidence = calibrated probability (isotonic, fitted on validation courses). Gold = labels from two independent AI passes plus an independent adjudicator, not human verified."), courses=[])
def kahn(n, edges):
    indeg = [0] * n; adj = [[] for _ in range(n)]
    for a, c in edges: adj[a].append(c); indeg[c] += 1
    level = [0] * n; q = [i for i in range(n) if indeg[i] == 0]; order = []
    while q:
        u = q.pop(0); order.append(u)
        for v in adj[u]:
            level[v] = max(level[v], level[u] + 1); indeg[v] -= 1
            if indeg[v] == 0: q.append(v)
    assert len(order) == n, "cycle"
    return order, level
for c, v in T.items():
    if v["split"] != "test": continue
    ts = [dict(id=t["id"], name=t["name"], module=t["module_idx"]) for t in v["topics"]]; ids = {t["id"]: i for i, t in enumerate(ts)}; n = len(ts)
    ctx = dict(title=v["course_title"], module_names={m["index"]: m["name"] for m in v["modules"]})
    gold = {(ids[e["a"]], ids[e["b"]]) for e in json.load(open(os.environ.get("LABEL_DIR", "data/labelling/claude") + f"/{c}.json"))["edges"]}
    S = score_pairs(ts, b, True, ctx=ctx)
    low_edges = infer_course(ts, bundle=b, threshold=LOW, margin=b.margin, reduce=False, scores=S, ctx=ctx)
    E = [(ids[e.a], ids[e.b], e.confidence) for e in low_edges]
    acc = [(a, c2) for a, c2, p in E if p >= b.threshold]
    order, level = kahn(n, [(a, c2) for a, c2, _ in E])      # Kahn over ALL shown edges (uncertain ones included) for the full order
    order_acc, level_acc = kahn(n, acc)                       # Kahn over accepted edges only (what blocks a learner)
    red = {tuple(e) for e in nx.transitive_reduction(nx.DiGraph(acc)).edges()} if acc else set()
    edges = [dict(a=a, b=c2, p=round(p, 3), band="accepted" if p >= b.threshold else "uncertain",
                  gold=(a, c2) in gold, redundant=(a, c2) not in red and p >= b.threshold) for a, c2, p in E]
    missed = [dict(a=a, b=c2) for a, c2 in sorted(gold) if not any(e["a"] == a and e["b"] == c2 for e in edges if e["band"] == "accepted")]
    hit = sum(1 for e in edges if e["band"] == "accepted" and e["gold"]); na = sum(1 for e in edges if e["band"] == "accepted")
    out["courses"].append(dict(code=c, title=v["course_title"], source=v["source_pdfs"][0], n=n, nodes=ts, edges=edges, missed_gold=missed,
                               kahn_order=order_acc, kahn_level=level_acc, kahn_level_all=level,
                               stats=dict(accepted=na, hit=hit, gold=len(gold), precision=round(hit / max(1, na), 3), recall=round(hit / max(1, len(gold)), 3))))
    print(c, v["course_title"][:28].ljust(28), "topics", n, "accepted", na, "hit", hit, "gold", len(gold), "kahn levels", max(level_acc) + 1)
json.dump(out, open("demo/graph_data.json", "w", encoding="utf-8"), ensure_ascii=False)
print("wrote demo/graph_data.json", round(os.path.getsize("demo/graph_data.json") / 1024), "KB")
