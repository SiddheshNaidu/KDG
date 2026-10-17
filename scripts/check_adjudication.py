import sys, json, pathlib
for c in sys.argv[1:]:
    i = json.load(open(f"data/labelling/adjudicate/{c}.json", encoding="utf-8")); f = pathlib.Path(f"data/labelling/adjudicated/{c}.json")
    if not f.exists(): print(c, "MISSING"); continue
    keep = json.load(open(f))["keep"]; ok = {x["i"] for x in i["candidates"]}
    bad = [k for k in keep if k not in ok]; pairs = {(x["a"], x["b"]) for x in i["candidates"] if x["i"] in keep}
    two = [p for p in pairs if (p[1], p[0]) in pairs]
    print(c, "candidates", len(ok), "kept", len(keep), "ERR bad ids " + str(bad[:3]) if bad else "", "ERR both directions kept" if two else "", "ok" if not bad and not two else "")
