import importlib.util,re,collections
s=importlib.util.spec_from_file_location("ex","spikes/nep26-fe-sem12_extract.py");ex=importlib.util.module_from_spec(s);s.loader.exec_module(ex)
names=["AIML","CSE-AIML","DS","EXTC","IT","MECH"]
rows=collections.defaultdict(list)
for n,c in ex.all_courses():
    lines=ex.clean(c); r=ex.find_modules(lines)
    if r["modules"]:
        st=r["modules"][0]["style"]; mk=r["modules"][0]["marker"].strip()
        mk2=mk if st!="trade" else "Trade-n"
        kind=f"{st}:first_marker={mk2!r}"
    else:
        kind="no_module_table"+(" (lab list)" if any(ex.C["lab_hdr"].match(l[2]) for l in lines) else "")
    rows[c["code"]].append((kind,len(r["modules"]),(r["stop"] or "-")[:14]))
out=["command: cd /c/Users/Siddhesh/Documents/KDG && PYTHONIOENCODING=utf-8 python spikes/nep26-fe-sem12_variants.py > docs/evidence/regex_runs/nep26-fe-sem12_layout_variants.txt",
     "per course code: layout kind (over the PDFs where it occurs: count), module count, stop marker"]
for code in sorted(rows):
    c=collections.Counter(rows[code])
    out.append(f"{code}: "+" ; ".join(f"{v}x {k[0]} K={k[1]} stop={k[2]!r}" for k,v in c.items()))
open("docs/evidence/regex_runs/nep26-fe-sem12_layout_variants.txt","w",encoding="utf-8").write("\n".join(out)+"\n")
print("\n".join(out))
