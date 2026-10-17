import importlib.util,re
s=importlib.util.spec_from_file_location("sg","spikes/nep26-fe-sem12_seg.py");sg=importlib.util.module_from_spec(s);s.loader.exec_module(sg)
seen=set()
for n in (0,3,5,2):
    L,cs=sg.segment_pdf(n)
    for c in cs:
        if c["code"] in seen: continue
        seen.add(c["code"])
        t=[l[2] for l in c["lines"]]
        z=sum(bool(re.fullmatch(r"\s*0\d\s*",x)) for x in t)
        r=sum(bool(re.fullmatch(r"\s*(I|II|III|IV|V|VI|VII|VIII)\s*",x)) for x in t)
        mo=sum(bool(re.match(r"\s*Module\s*[-:]?\s*(\d|[IVX]+)",x,re.I)) for x in t)
        sr=sum(bool(re.fullmatch(r"\s*\d{1,2}\s*",x)) for x in t)
        d=sum(bool(re.match(r"\s*\d+\.\d+",x)) for x in t)
        hdr=[x.strip() for x in t if re.search(r"Detailed ?Contents?|List of Experiments|Sr\.? ?No|Name of Module|Self.?(learning|study)|Pre-?requisite",x,re.I)]
        print(c["code"],"pdf",n,"pages",c["lines"][0][0],"-",c["lines"][-1][0],"| 0N:",z,"roman:",r,"Module N:",mo,"dotted:",d,"|",sorted(set(h[:28] for h in hdr))[:5])
