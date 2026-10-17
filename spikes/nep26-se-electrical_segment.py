"""Spike: segment courses of nep26-se-electrical PDFs (line level, stripped, empty lines dropped)."""
import fitz,re,sys,json
PDFS={"ece":"data/raw/2019-scheme/Electrical-Computer-Engineering/6.51N-B.E.-Electrical-Computer-EngineeringSem-III-IV.pdf",
      "ee":"data/raw/2019-scheme/Electrical-Engineering/6.29-N-B.E.-Electrical-Engineering-Sem-III-IV.pdf"}
OBJ=re.compile(r"^(Course|Lab) [Oo]bjectives?:")
ROMAN=re.compile(r"^(I|II|III|IV|V|VI|VII|VIII)$")
TAIL=re.compile(r"^(\d{1,2})$")
COLINE=re.compile(r"^(CO|LO)\d$")
CODE=re.compile(r"^\d{7}$")
def lines(path):
    out=[]
    for i,p in enumerate(fitz.open(path)):
        for l in p.get_text().split("\n"):
            if l.strip(): out.append((i+1,l.strip()))
    return out
def courses(path):
    L=lines(path)
    objs=[k for k,(pg,l) in enumerate(L) if OBJ.match(l)]
    codes=[];first={}
    for k,(pg,l) in enumerate(L):
        if pg>=16 and CODE.match(l) and l not in first: first[l]=k; codes.append(l)
    segs=[]
    for n,s in enumerate(objs):
        e=objs[n+1] if n+1<len(objs) else len(L)
        segs.append((s,e))
    return L,objs,codes,segs
if __name__=="__main__":
    for k,p in PDFS.items():
        L,objs,codes,segs=courses(p)
        print(k,len(objs),len(codes),codes)
        for (s,e),c in zip(segs,codes): print(c,L[s][0],L[e-1][0],e-s)
