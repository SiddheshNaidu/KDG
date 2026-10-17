"""Throwaway: segment detail courses per PDF with wrapped-code joining. Importable: segment_pdf(i)->list of dict."""
import re,importlib.util
s=importlib.util.spec_from_file_location("pr","spikes/nep26-fe-sem12_probe.py");pr=importlib.util.module_from_spec(s);s.loader.exec_module(pr)
CODE=re.compile(r"^\s*([A-Z]{2,5}\d{3,4}[A-Z]?)(?![A-Za-z0-9])")
START=re.compile(r"^\s*BSC101(?!\d)")
def joined(L):
    """yield (idx,page,line,code,title_rest) for code-start lines, joining 'ABC202' + '2'."""
    out=[]
    for k,(i,j,l) in enumerate(L):
        m=CODE.match(l)
        if not m or l.strip().startswith("http"): continue
        code=m.group(1); rest=l[m.end():].strip()
        if not rest and re.fullmatch(r"[A-Z]{2,5}\d{3}",code) and k+1<len(L) and re.fullmatch(r"\s*\d\s*",L[k+1][2]) and L[k+1][0]==i:
            code+=L[k+1][2].strip()
        out.append((k,i,j,code,rest))
    return out
def segment_pdf(n):
    L=list(pr.lines(pr.PDFS[n]))
    st=min(k for k,(i,j,l) in enumerate(L) if i>=12 and START.match(l[2] if False else l))
    fo=min(i for i,j,l in L if re.search(r'(Course|Lab) Objectives',l))
    occ=[o for o in joined(L) if o[0]>=st and (o[1]>fo or o[3]=='BSC101')]
    first={}
    for o in occ: first.setdefault(o[3],o)
    order=sorted(first.values())
    courses=[]
    for a,o in enumerate(order):
        end=order[a+1][0] if a+1<len(order) else len(L)
        courses.append(dict(code=o[3],start=o[0],end=end,lines=L[o[0]:end],page=o[1]))
    # keep only those with an Objectives line in their own segment => real detail courses
    return L,courses
if __name__=="__main__":
    OBJ=re.compile(r"Objectives|Outcomes|Detailed ?Content|Experiments",re.I)
    for n in range(6):
        L,cs=segment_pdf(n)
        real=[c for c in cs if any(OBJ.search(l[2]) for l in c["lines"])]
        print(pr.PDFS[n].split("/")[0],"segments",len(cs),"with_objectives",len(real),"no_obj:",[c["code"] for c in cs if c not in real])
