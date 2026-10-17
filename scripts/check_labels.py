"""Validate a labelling file against its input. Usage: python scripts/check_labels.py <pass_dir> [course ...]
Rules: ids exist; a != b; no duplicate edge; no 2-cycles (a->b and b->a); graph is acyclic; reports edges/topic and share of edges
pointing backwards in syllabus order (allowed but reported)."""
import sys, json, pathlib
import networkx as nx
d = pathlib.Path(sys.argv[1]); inp = pathlib.Path("data/labelling/inputs")
names = sys.argv[2:] or [p.stem for p in sorted(d.glob("*.json"))]
bad = 0
for c in names:
    f = d / f"{c}.json"
    if not f.exists(): print(c, "MISSING"); bad += 1; continue
    ins = json.load(open(inp / f"{c}.json", encoding="utf-8")); ids = {t["id"]: i for i, t in enumerate(ins["topics"])}
    ed = json.load(open(f, encoding="utf-8"))["edges"]; errs = []; seen = set(); G = nx.DiGraph()
    for e in ed:
        a, b = e["a"], e["b"]
        if a not in ids or b not in ids: errs.append(f"unknown id {a}->{b}"); continue
        if a == b: errs.append(f"self loop {a}"); continue
        if (a, b) in seen: errs.append(f"duplicate {a}->{b}"); continue
        if (b, a) in seen: errs.append(f"2-cycle {a}<->{b}")
        seen.add((a, b)); G.add_edge(a, b)
    if not nx.is_directed_acyclic_graph(G): errs.append("cycle: " + str(nx.find_cycle(G)[:3]))
    back = sum(1 for a, b in seen if ids[a] > ids[b]); n = len(ins["topics"])
    print(f"{c:12} topics={n:3} edges={len(seen):3} edges/topic={len(seen)/n:.2f} backward={back} {'ERR ' + '; '.join(errs[:3]) if errs else 'ok'}")
    bad += bool(errs)
sys.exit(1 if bad else 0)
