"""Throwaway spike for family nep26-sem56. Segments SEM-V.pdf into courses and parses theory module tables."""
import fitz,re,sys,collections
PDF="data/raw/_unclassified/SEM-V.pdf"
CODE=re.compile(r"^\s*(\d{7}|[A-Z]{3}\d{3})\s*$")
DS=re.compile(r"(?i)^\s*detailed\s+syllabus\s*:?\s*$")
ROMAN=re.compile(r"^\s*(I|II|III|IV|V|VI|VII|VIII)\s*$")
HOURS=re.compile(r"^\s*(\d{1,2})\s*$")
CO=re.compile(r"^\s*(CO\s?\d(\s*(,|&|-|–|to)\s*(CO)?\s?\d)*)\s*$")
STOP=re.compile(r"(?i)^\s*(text\s*(and\s+reference\s+)?books?\b|books\s*:)")
HDREND=re.compile(r"(?i)^\s*(C[O0]|LO)(\s+mapping)?\s*$")
MAPPING=re.compile(r"(?i)^\s*mapping\s*$")
SELF=re.compile(r"(?i)^\s*self[\s-]*(learning|study)\b")
PRE=re.compile(r"(?i)^\s*pre-?\s*requisites?\s*$")
def load():
    d=fitz.open(PDF); pages=[p.get_text().split("\n") for p in d]; return pages
def segments(pages):
    first={}
    for i,ls in enumerate(pages,1):
        if i<10: continue
        for n,l in enumerate(ls):
            m=CODE.match(l)
            if m and m.group(1) not in first: first[m.group(1)]=(i,n)
    codes=sorted(first,key=lambda c:first[c])
    segs=[]
    for k,c in enumerate(codes):
        s=first[c][0]; e=(first[codes[k+1]][0]-1) if k+1<len(codes) else len(pages)
        # course starts on page s; if next course starts on same page, end = s
        if k+1<len(codes) and first[codes[k+1]][0]==s: e=s
        segs.append((c,s,max(e,s)))
    return segs,first
def title(pages,c,page,n):
    t=[]
    for l in pages[page-1][n+1:n+8]:
        s=l.strip()
        if re.match(r"^[\d\-–—]+$",s) or s=="" and t==[] and False: break
        if s=="": 
            if t: break
            continue
        t.append(s)
    out=""
    for s in t: out = out+s if out.endswith("-") else (out+" "+s if out else s)
    return out
def lines_of(pages,s,e):
    out=[]
    for p in range(s,e+1):
        for n,l in enumerate(pages[p-1]): out.append((p,n,l))
    return out

NUMROW=re.compile(r"^\s*([\d\-–—]+|)\s*$")
def strip_tables(reg):
    """Remove inserted 'Course / Code / Course Name ...' header tables (teaching/examination scheme) from a region. Returns (kept, removed)."""
    kept=[];removed=[];i=0
    while i<len(reg):
        if reg[i][2].strip()=="Course" and i+1<len(reg) and reg[i+1][2].strip()=="Code":
            j=i+2;c=None
            while j<len(reg) and j<i+45:
                if CODE.match(reg[j][2]): c=j;break
                j+=1
            if c is not None:
                k=c+1
                while k<len(reg) and not NUMROW.match(reg[k][2]) or (k<len(reg) and reg[k][2].strip()==""): 
                    if k>=len(reg) or k>c+8: break
                    k+=1
                while k<len(reg) and NUMROW.match(reg[k][2]): k+=1
                removed+=reg[i:k]; i=k; continue
        kept.append(reg[i]); i+=1
    return kept,removed

def parse_modules(L):
    ds=[i for i,(p,n,l) in enumerate(L) if DS.match(l)]
    if not ds: return None
    i=ds[0]+1
    # skip column-header block: first lone CO/LO line (plus optional 'Mapping') after the DS marker
    h=None
    for j in range(i,len(L)):
        if HDREND.match(L[j][2]): h=j;break
    if h is None: return None
    i=h+1
    if i<len(L) and MAPPING.match(L[i][2]): i+=1
    stop=len(L)
    for j in range(i,len(L)):
        if STOP.match(L[j][2]): stop=j;break
    kept,removed=strip_tables(L[i:stop])
    return kept, stop
if __name__=="__main__":
    pages=load(); segs,first=segments(pages)
    for c,s,e in segs:
        p,n=first[c]
        print(c,s,e,repr(title(pages,c,p,n)))
