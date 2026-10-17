import importlib.util,sys,re
s=importlib.util.spec_from_file_location("ex","spikes/nep26-fe-sem12_extract.py");ex=importlib.util.module_from_spec(s);s.loader.exec_module(ex)
n=int(sys.argv[1]);code=sys.argv[2]
L,cs=ex.sg.segment_pdf(n); c=[x for x in cs if x["code"]==code][0]; r=ex.find_modules(ex.clean(c))
print("pages",c["lines"][0][0],"-",c["lines"][-1][0])
print("PREREQ REGION:"," | ".join(l.strip() for l in r["prereq"] if l.strip())[:700])
for m in r["modules"]:
    print("== MODULE",m["number"])
    print(" | ".join(x.strip() for x in m["raw"])[:1800])
