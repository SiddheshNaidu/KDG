import importlib.util,re,hashlib
s=importlib.util.spec_from_file_location("sg","spikes/nep26-fe-sem12_seg.py");sg=importlib.util.module_from_spec(s);s.loader.exec_module(sg)
OBJ=re.compile(r"Objectives|Outcomes|Detailed ?Content|Experiments",re.I)
data={}
for n in range(6):
    L,cs=sg.segment_pdf(n)
    for c in cs:
        if not any(OBJ.search(l[2]) for l in c["lines"]): continue
        txt=re.sub(r"\s+","",re.sub(r"^\d+ $","", "".join(l[2] for l in c["lines"][1:] if l[1]!=1) ))  # whitespace-insensitive
        data.setdefault(c["code"],{})[n]=(c["page"],hashlib.md5(txt.encode()).hexdigest()[:8],len(txt))
names=["AIML","CSE-AIML","DS","EXTC","IT","MECH"]
print("code | "+" | ".join(names))
for code,v in sorted(data.items()):
    row=[]
    for n in range(6):
        row.append(f"p{v[n][0]}:{v[n][1]}" if n in v else "--")
    distinct=len({x[1] for x in v.values()})
    print(code,len(v),"distinct_text",distinct,*row)
print("unique codes",len(data),"occurrences",sum(len(v) for v in data.values()))
