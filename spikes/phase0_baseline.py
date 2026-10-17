"""Spike (Phase 0): measure the OLD parser (reference/, read-only) against DRAFT golden courses.
Usage: PYTHONIOENCODING=utf-8 python spikes/phase0_baseline.py
Matching: topics normalised (lowercase, alnum tokens). exact = identical normalised string;
loose = token Jaccard >= 0.6 (greedy one-to-one). Golden topics are hand-drafted atomic concepts,
so loose match is reported next to exact; neither is a verdict on parser quality for labelling use."""
import sys, json, glob, csv, re, pathlib, time, collections
sys.path.insert(0, "reference"); sys.path.insert(0, "spikes")
from topic_validity import validate
from app.parser.nep_syllabus_parser import parse_nep_pdf_bytes
from app.parser.format_router import parse_syllabus_pdf_bytes_routed

def norm(s): return re.findall(r"[a-z0-9]+", s.lower())
def jac(a, b):
    A, B = set(a), set(b); return len(A & B) / len(A | B) if A | B else 0.0
def match(pred, gold, loose):
    P = [norm(x) for x in pred]; G = [norm(x) for x in gold]; used = set(); tp = 0
    for p in P:
        best, bj = None, 0
        for i, g in enumerate(G):
            if i in used: continue
            s = (1.0 if p == g else 0.0) if not loose else jac(p, g)
            if (s >= (1.0 if not loose else 0.6)) and s > bj: best, bj = i, s
        if best is not None: used.add(best); tp += 1
    pr = tp / len(P) if P else 0.0; rc = tp / len(G) if G else 0.0
    f = 2 * pr * rc / (pr + rc) if pr + rc else 0.0
    return pr, rc, f

cache = {}
def parsed(pdf):
    if pdf not in cache:
        b = open(pdf, "rb").read(); t = time.perf_counter()
        try: ok, cs, _ = parse_nep_pdf_bytes(b); err = None
        except Exception as e: ok, cs, err = False, [], repr(e)[:80]
        try: rok, rcs, fmt, _, rerr = parse_syllabus_pdf_bytes_routed(b)
        except Exception as e: rok, rcs, fmt, rerr = False, [], "exc", repr(e)[:80]
        cache[pdf] = dict(nep=({c.code: c for c in cs}, ok, err), routed=({c.code: c for c in rcs}, rok, fmt, rerr), secs=round(time.perf_counter() - t, 1))
    return cache[pdf]

rows = []
for f in sorted(glob.glob("tests/golden/*/*.json")):
    g = json.load(open(f, encoding="utf-8")); code = str(g["course_code"]); pdf = g["source_pdf"]
    gold = [t for m in g["modules"] for t in m["topics"]]
    r = dict(family=g["family"], golden=pathlib.Path(f).name, code=code, gold_topics=len(gold), gold_modules=len(g["modules"]))
    if not pathlib.Path(pdf).exists(): r.update(error="pdf_missing"); rows.append(r); continue
    P = parsed(pdf)
    for tag in ("nep", "routed"):
        courses = P[tag][0]; c = courses.get(code)
        if c is None: r[f"{tag}_found"] = 0; r[f"{tag}_note"] = f"gate/format={P[tag][1:]}"[:80]; continue
        pred = [t["name"] for t in c.topics] if c.topics and isinstance(c.topics[0], dict) else [str(t) for t in c.topics]
        viol = sum(1 for t in pred if validate(t))
        ex = match(pred, gold, False); lo = match(pred, gold, True)
        r.update({f"{tag}_found": 1, f"{tag}_pred_topics": len(pred), f"{tag}_pred_modules": len(c.modules),
                  f"{tag}_junk_rate": round(viol / len(pred), 3) if pred else "",
                  f"{tag}_exact_f1": round(ex[2], 3), f"{tag}_loose_p": round(lo[0], 3), f"{tag}_loose_r": round(lo[1], 3), f"{tag}_loose_f1": round(lo[2], 3)})
    rows.append(r)
keys = []
for r in rows:
    for k in r:
        if k not in keys: keys.append(k)
out = "docs/evidence/baseline/old_parser_vs_golden.csv"
w = csv.DictWriter(open(out, "w", newline="", encoding="utf-8"), fieldnames=keys); w.writeheader(); w.writerows(rows)
print("goldens", len(rows), "PDF parse secs", {k.split('/')[-1][:20]: v['secs'] for k, v in cache.items()})
by = collections.defaultdict(list)
for r in rows: by[r["family"]].append(r)
print("family | n | nep_found | routed_found | nep_loose_f1_mean(found) | nep_junk_mean(found)")
for fam, rs in by.items():
    fo = [x for x in rs if x.get("nep_found")]
    m = lambda k: round(sum(x[k] for x in fo) / len(fo), 3) if fo else "n/a"
    junk = [x["nep_junk_rate"] for x in fo if x.get("nep_junk_rate") != ""]
    print(fam, "|", len(rs), "|", len(fo), "|", sum(1 for x in rs if x.get("routed_found")), "|", m("nep_loose_f1"), "|", round(sum(junk) / len(junk), 3) if junk else "n/a")
