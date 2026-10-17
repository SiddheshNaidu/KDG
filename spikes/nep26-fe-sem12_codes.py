import re,importlib.util,fitz
s=importlib.util.spec_from_file_location("pr","spikes/nep26-fe-sem12_probe.py");pr=importlib.util.module_from_spec(s);s.loader.exec_module(pr)
C=re.compile(r"^\s*([A-Z]{2,5}\d{3,4}[A-Z]?)\b")
def codes(p, minpage=13):
    out={}
    for i,j,l in pr.lines(p):
        if i>=minpage:
            m=C.match(l)
            if m and not l.strip().startswith("http"): out.setdefault(m.group(1),[]).append(i)
    return out
if __name__=="__main__":
    allc={}
    for p in pr.PDFS:
        c=codes(p); allc[p]=c
        print(p.split("/")[0], len(c), {k:(v[0],len(v)) for k,v in c.items()})
    base=set(allc[pr.PDFS[0]])
    for p in pr.PDFS[1:]:
        s_=set(allc[p]); print(p.split("/")[0],"only_here",sorted(s_-base),"missing",sorted(base-s_))
