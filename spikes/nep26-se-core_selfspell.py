"""Counts of anchored self-learning/self-study marker spellings per PDF (evidence for doc section Self-learning markers)."""
import sys, re, importlib, collections
sys.path.insert(0, "spikes")
L = importlib.import_module("nep26-se-core_lib")
SP = [("Self-learning Topics:", re.compile(r"^\s*Self-learning\s+Topics?\s*:")),
      ("Self-learning (bare, 'Topics:' on following line)", re.compile(r"^\s*Self-learning\s*$")),
      ("Self-Study :/Self-Study:", re.compile(r"^\s*Self-Study\s*:")),
      ("other anchored", re.compile(r"^\s*Self[\s\-]*(learning|study)\b"))]
out = ["command: PYTHONIOENCODING=utf-8 python spikes/nep26-se-core_selfspell.py", "pdf | spelling counts (first matching spelling wins; 'other anchored' = anchored but none of the first three)"]
other = []
for p in L.PDFS:
    c = collections.Counter(); nxt = collections.Counter()
    ls = L.lines(p)
    for i, (pg, j, l) in enumerate(ls):
        for name, rx in SP[:3]:
            if rx.match(l):
                c[name] += 1
                if name.startswith("Self-learning (bare"):
                    n2 = ls[i + 1][2].strip() if i + 1 < len(ls) else ""
                    nxt["next line == 'Topics:'" if n2.startswith("Topics") else "next line other: " + n2[:30]] += 1
                break
        else:
            if SP[3][1].match(l): other.append(f"{p} page {pg} line {j}: {l!r}")
    out.append(f"{p.split('/')[0]} | " + "; ".join(f"{k}={v}" for k, v in c.items()) + " | bare-marker followers: " + str(dict(nxt)))
out.append(f"other anchored ({len(other)}):")
out += ["  " + x for x in other]
open("docs/evidence/regex_runs/nep26-se-core_self_marker_spellings.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
