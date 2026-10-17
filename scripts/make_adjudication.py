"""Build adjudication inputs: for every course, the edges the two labelling passes did NOT agree on, shuffled and without any
information about which pass proposed them. data/labelling/adjudicate/<course>.json"""
import json, random, pathlib
M = pathlib.Path("data/labelling/merged"); OUT = pathlib.Path("data/labelling/adjudicate"); OUT.mkdir(exist_ok=True)
T = json.load(open("data/processed/topics_nep.json", encoding="utf-8")); SKIP = {"24061132", "PEC6024", "PCC501", "2116111", "2115116", "2405511"}   # excluded from training (verify_new_1/2)
tot = 0
for f in sorted(M.glob("*.json")):
    c = f.stem
    if (pathlib.Path("data/labelling/adjudicated") / f.name).exists(): continue   # keep inputs of courses that are already adjudicated (candidate indices must not move)
    if c in SKIP: continue
    m = json.load(open(f)); nm = {t["id"]: t for t in T[c]["topics"]}
    cand = [tuple(e) for e in m["a_only"] + m["b_only"]] + [tuple(e) for e in m["reverse"]] + [(b, a) for a, b in m["reverse"]]
    cand = sorted(set(cand)); random.Random(f"adj-{c}").shuffle(cand)
    json.dump(dict(course=c, title=T[c]["course_title"], topics=[dict(id=t["id"], name=t["name"], module=t["module_idx"]) for t in T[c]["topics"]],
                   candidates=[dict(i=k, a=a, b=b, a_name=nm[a]["name"], b_name=nm[b]["name"]) for k, (a, b) in enumerate(cand)]),
              open(OUT / f.name, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    tot += len(cand)
print("candidates to adjudicate:", tot, "in", len(list(OUT.glob('*.json'))), "courses")
