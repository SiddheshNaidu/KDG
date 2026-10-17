import fitz,re,glob
R="data/raw/2019-scheme/"
PDFS=["A-I-AI-DS/6.41N-A-I-AI-DS-Sem-III-IV.pdf","AI-DS/6.20N-B.E.-AI-DS.-Sem-III-IV.pdf","AI-ML/6.21-N-B.E.-AI-ML-sem-III-IV.pdf","Computer-Engineering/6.24-N-B.E.-Computer-Engineering-Sem-III-IV.pdf","Computer-Science-Engineering/6.54-N-B.E-Computer-Science-EngineeringSem-III-IV.pdf","Data-Science/6.39-N-B.E.-Data-Science-Sem-III-IV.pdf"]
def lines(pdf):
    d=fitz.open(R+pdf); out=[]
    for i,pg in enumerate(d):
        t=pg.get_text().split("\n")
        if t and t[-1]=="": t=t[:-1]
        for j,l in enumerate(t): out.append((i+1,j,l))
    return out

CODE_RX=re.compile(r"\d{7}\s*")
TITLE_END=re.compile(r"[\d\-–]+\s*")
def segment(ls):
    """course starts: code line directly after 'Total' line, with 'Credits Assigned' within 9 lines before; first occurrence per code in detail section"""
    starts=[]; seen=set()
    for k,(pg,j,l) in enumerate(ls):
        if CODE_RX.fullmatch(l) and k>0 and ls[k-1][2].strip().endswith("Total") and any("Credits Assigned" in x[2] for x in ls[max(0,k-14):k]):
            c=l.strip()
            if pg>=15 and c not in seen:
                seen.add(c); starts.append(k)
    segs=[]
    for n,k in enumerate(starts):
        e=starts[n+1] if n+1<len(starts) else len(ls)
        segs.append((k,e))
    return segs
def title_of(ls,k):
    t=[]; m=k+1
    while m<len(ls) and not TITLE_END.fullmatch(ls[m][2]):
        t.append(ls[m][2].strip()); m+=1
    return " ".join(t)
