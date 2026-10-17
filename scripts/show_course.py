import sys, json
c = json.load(open("data/processed/topics_nep.json", encoding="utf-8"))
for k in sys.argv[1:]:
    v = c[k]; print("\n##", k, v["course_title"], v["n_topics"], v["split"])
    print(" | ".join("%d[m%d] %s" % (int(t["id"][1:]), t["module_idx"], t["name"]) for t in v["topics"]))
