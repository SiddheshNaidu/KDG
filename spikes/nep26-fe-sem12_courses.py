"""Segment each PDF into detail courses (code, first_page, first_line) and diff code sets across PDFs."""
import re,importlib.util
s=importlib.util.spec_from_file_location("pr","spikes/nep26-fe-sem12_probe.py");pr=importlib.util.module_from_spec(s);s.loader.exec_module(pr)
CODE=re.compile(r"^\s*([A-Z]{2,5}\d{3,4}[A-Z]?)(?![A-Za-z0-9])")
OBJ=re.compile(r"^\s*(Course|Lab) Objectives",re.I)
START=re.compile(r"^\s*BSC101(?!\d)")
def segment(p):
    L=list(pr.lines(p))
    first_obj=min(i for i,j,l in L if OBJ.match(l))
    start=min((i,j) for i,j,l in L if i>=12 and START.match(l))
    occ={}
    for i,j,l in L:
        if (i,j)>=start:
            m=CODE.match(l)
            if m and not l.strip().startswith("http"): occ.setdefault(m.group(1),[]).append((i,j))
    order=sorted(occ.items(),key=lambda kv:kv[1][0])
    return L,order,first_obj
if __name__=="__main__":
    sets={}
    for p in pr.PDFS:
        L,order,fo=segment(p); sets[p]=[c for c,_ in order]
        print("##",p.split("/")[0],"pages",L[-1][0],"first_obj_page",fo,"ncourses",len(order))
        print(" ".join(f"{c}@{o[0][0]}x{len(o)}" for c,o in order))
    base=set(sets[pr.PDFS[0]]); U=set().union(*map(set,sets.values()))
    print("unique codes",len(U))
    for p in pr.PDFS: print(p.split("/")[0],"not_in_AIML",sorted(set(sets[p])-base),"AIML_not_here",sorted(base-set(sets[p])))
