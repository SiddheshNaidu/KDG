"""Collect data/labelling/claude/src/part*.py (LAB dicts), validate against topics_nep.json (ids exist, no dup, DAG) and write
data/labelling/claude/<course>.json  {"edges":[{"a":"t3","b":"t7"}]}. Usage: python scripts/write_claude_labels.py"""
import json, glob, importlib.util, pathlib, sys
import networkx as nx
T = json.load(open("data/processed/topics_nep.json", encoding="utf-8"))
out = pathlib.Path("data/labelling/claude"); bad = 0; rows = []
for f in sorted(glob.glob("data/labelling/claude/src/part*.py")):
    spec = importlib.util.spec_from_file_location(pathlib.Path(f).stem, f); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    for c, es in m.LAB.items():
        if c not in T: print("UNKNOWN COURSE", c); bad += 1; continue
        n = T[c]["n_topics"]; seen = set(); errs = []
        for a, b in es:
            if not (1 <= a <= n and 1 <= b <= n) or a == b: errs.append(f"bad id {a}->{b}")
            elif (a, b) in seen: errs.append(f"dup {a}->{b}")
            elif (b, a) in seen: errs.append(f"2-cycle {a}<->{b}")
            seen.add((a, b))
        G = nx.DiGraph(list(seen))
        if not nx.is_directed_acyclic_graph(G): errs.append("CYCLE " + str(nx.find_cycle(G)[:3]))
        if errs: print(c, "ERR", errs[:4]); bad += 1; continue
        json.dump(dict(label_source="claude-provisional (not human verified)", split=T[c]["split"], edges=[dict(a=f"t{a}", b=f"t{b}") for a, b in sorted(seen)]), open(out / f"{c}.json", "w"), indent=0)
        rows.append((c, T[c]["split"], n, len(seen)))
print(len(rows), "courses labelled;", "topics", sum(r[2] for r in rows), "edges", sum(r[3] for r in rows), "| errors", bad)
for r in rows[-6:]: print(" ", r)
sys.exit(1 if bad else 0)
