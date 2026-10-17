import importlib.util,re
s=importlib.util.spec_from_file_location("ex","spikes/nep26-fe-sem12_extract.py");ex=importlib.util.module_from_spec(s);s.loader.exec_module(ex)
import sys
for n,c in ex.all_courses():
    if n!=int(sys.argv[1]): continue
    L=ex.clean(c); r=ex.find_modules(L)
    print(c["code"],"lab" if ex.is_lab(c["code"]) else "thy","table",r["table"] is not None,"mods",len(r["modules"]),[m["style"][0]+m["number"] for m in r["modules"]],"stop",r["stop"],"| title:",ex.title_from([(1,1,l) for _,_,l in [(0,0,x[2]) for x in c["lines"]]],0)[:40])
