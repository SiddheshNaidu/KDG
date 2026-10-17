"""Spike for family nep26-se-core: segment courses, extract region, modules, topics. Throwaway, not product code."""
import re,sys,importlib
sys.path.insert(0,"spikes")
L=importlib.import_module("nep26-se-core_lib")
HDR_RX=re.compile(r"^\s*DETAIL(ED)?\s+SYLLABUS\s*:?\s*$")
STOP1_RX=re.compile(r"^\s*(Text\s*Books?|Reference\s*Books?|Textbooks?|Books|Online\s+References?|Suggested\s+List\s+of\s+[Ee]xperiments?|List\s+of\s+Experiments?|Assessment|Term\s+Work)\b\s*[:.]?")
STOP_RX=re.compile(r"^\s*(Text\s*Books?|Reference\s*Books?|Textbooks?|Books|Online\s+References?|Suggested\s+List\s+of\s+[Ee]xperiments?|List\s+of\s+Experiments?)\s*[:.]?\s*$|^\s*(Assessment|Term\s+Work)\s*:")
ROMAN_RX=re.compile(r"^\s*(I|II|III|IV|V|VI|VII|VIII)\s*$")
ROMAN2_RX=re.compile(r"^\s*(II|III|IV|V|VI|VII|VIII)\s+(?=[A-Z][a-z])(.*)$")
SELF_RX=re.compile(r"^\s*Self[\s\-]*(learning|study)\b",re.I)
TAIL_RX=re.compile(r"^\s*((CO|LO)\s?\.?\s?\d|L\d)(\s*[,&]\s*((CO|LO|L)\s?\.?\s?)?\d)*\s*,?\s*$")
NUM_RX=re.compile(r"^\s*\d{1,2}\s*$")
HDRWORDS={"Sr.","No","No.","Name of","Module","Name of Module","Name of the Module","Detailed Content","Topics","Hours","Hrs","CO","LO","Mapping","Unit","Name","Topic Name","Topic Description","Sr. No.","(Theory of"}
def courses(pdf):
    ls=L.lines(pdf); sg=L.segment(ls); out=[]
    starts=[ls[k][0] for k,e in sg]
    for n,(k,e) in enumerate(sg):
        p0=starts[n]; p1=(starts[n+1]-1) if n+1<len(sg) else ls[-1][0]
        # last course: cut at first line 'Letter Grades' page? keep to end
        txt=[x for x in ls if p0<=x[0]<=p1]
        out.append(dict(code=ls[k][2].strip(),title=re.sub(r"\s+"," ",L.title_of(ls,k)).strip(),pages=list(range(p0,p1+1)),lines=txt))
    return out
def strip_header_blocks(lines):
    """remove 'Course / Code ... code title numbers' header table blocks (can float inside the syllabus table in -b layout)"""
    out=[];i=0;n=len(lines)
    while i<n:
        pg,j,l=lines[i]
        if l.strip()=="Course" and i+1<n and lines[i+1][2].strip() in("Code","Name","Objectives:","Outcomes:") and lines[i+1][2].strip() in ("Code",):
            # skip until after code line + title + numeric run (teaching table: exactly 7 values; examination table: numeric run,
            # but a single digit followed by alphabetic text is a module number and is kept)
            m=i; teaching=False
            while m<n and not L.CODE_RX.fullmatch(lines[m][2]):
                if "Teaching Scheme" in lines[m][2]: teaching=True
                m+=1
            m+=1
            while m<n and not L.TITLE_END.fullmatch(lines[m][2]): m+=1
            cnt=0
            while m<n and (L.TITLE_END.fullmatch(lines[m][2]) or not lines[m][2].strip()):
                if lines[m][2].strip():
                    if teaching and cnt>=7: break
                    if not teaching and re.fullmatch(r"[1-9]",lines[m][2].strip()):
                        q=m+1
                        while q<n and not lines[q][2].strip(): q+=1
                        if q<n and re.search(r"[A-Za-z]{3}",lines[q][2]): break
                    cnt+=1
                m+=1
            i=m; continue
        out.append(lines[i]); i+=1
    return out
def region(c):
    ls=strip_header_blocks(c["lines"])
    s=None
    for i,(pg,j,l) in enumerate(ls):
        if HDR_RX.match(l): s=i;break
    if s is None:
        for i,(pg,j,l) in enumerate(ls):
            if ROMAN_RX.match(l) and l.strip()=="I": s=i;break
    if s is None: return []
    e=len(ls)
    for i in range(s+1,len(ls)):
        if STOP_RX.match(ls[i][2]): e=i;break
    return ls[s:e]

LABEL_ARABIC_PRE=re.compile(r"^\s*Mapping\s*$")
def clean_noise(lines):
    out=[]
    for pg,j,l in lines:
        s=l.strip()
        if not s: continue
        if s in HDRWORDS: continue
        if re.fullmatch(r"[-–—]+",s): continue
        out.append((pg,j,s))
    return out
def split_modules(reg):
    ls=clean_noise(reg)
    # attempt2 of module_row: numeral may share the line with the first name word ('VI Special-purpose'); accept only if it is the next numeral in sequence
    RN=["I","II","III","IV","V","VI","VII","VIII"]; exp=0; ls2=[]
    for x in ls:
        if ROMAN_RX.match(x[2]):
            exp+=1
        else:
            m_=ROMAN2_RX.match(x[2])
            if m_ and exp<len(RN) and m_.group(1)==RN[exp]:
                ls2.append((x[0],x[1],m_.group(1))); ls2.append((x[0],x[1],m_.group(2).strip())); exp+=1; continue
        ls2.append(x)
    ls=ls2
    roman=[i for i,x in enumerate(ls) if ROMAN_RX.match(x[2])]
    mods=[]
    if roman:
        marks=roman; labels=[ls[i][2] for i in marks]
    else:
        marks=[]; labels=[]
        for i,x in enumerate(ls):
            if re.fullmatch(r"[1-9]",x[2]) and i+1<len(ls) and not (TAIL_RX.match(ls[i+1][2])) and (i==0 or TAIL_RX.match(ls[i-1][2]) or i<3 or True):
                prev=ls[i-1][2] if i else ""
                nxt=ls[i+1][2]
                if (i==0 or TAIL_RX.match(prev) or NUM_RX.match(prev) or prev in HDRWORDS or HDR_RX.match(prev)) and not NUM_RX.match(nxt):
                    marks.append(i); labels.append(x[2])
    # lines before the first marker: prerequisite text, then (oddity) the head of module 1 content from first numbered item
    pre=[x[2] for x in ls[:marks[0]]] if marks else []
    carry=[]
    for q,s_ in enumerate(pre):
        if re.match(r"^\d+[.)]\s",s_): carry=pre[q:];break
    for n,i in enumerate(marks):
        e=marks[n+1] if n+1<len(marks) else len(ls)
        blk=[x[2] for x in ls[i+1:e]]
        if n==0 and carry:
            # carried lines are content: put after the name lines handled later -> mark with sentinel
            blk=blk+["@@CARRY@@"]+carry
        mods.append((labels[n],blk))
    return mods
def module_parse(label,blk):
    # drop hours/CO tails
    b=[s for s in blk if not TAIL_RX.match(s) and not NUM_RX.match(s)]
    name=[];k=0
    while k<len(b):
        s=b[k]
        if len(s)>20 or re.search(r"[,:.]\s*$",s) or SELF_RX.match(s) or re.match(r"^\d+[.)]",s): break
        name.append(s);k+=1
    rest=b[k:]
    content=[];selfl=[];insl=False
    if "@@CARRY@@" in rest:
        q=rest.index("@@CARRY@@"); rest=rest[q+1:]+rest[:q]
    for s in rest:
        if SELF_RX.match(s): insl=True
        (selfl if insl else content).append(s)
    return " ".join(name)," ".join(content)," ".join(selfl)
def split_topics(content):
    items=re.split(r"(?:^|\s)\d+[.)]\s+",content)
    tops=[]
    for it in items:
        depth=0;cur="";parts=[]
        for ch_i,ch in enumerate(it):
            if ch in "([": depth+=1
            if ch in ")]": depth=max(0,depth-1)
            if depth==0 and ch in ",;:." and (ch_i+1==len(it) or it[ch_i+1]==" ") :
                parts.append(cur);cur="";continue
            cur+=ch
        parts.append(cur)
        for p in parts:
            p=re.sub(r"\s+"," ",p).strip(" ,;:.-–")
            if re.search(r"[A-Za-z]",p): tops.append(p)
    return tops
def extract(c):
    r=region(c)
    mods=[]
    for lab,blk in split_modules(r):
        nm,ct,sl=module_parse(lab,blk)
        mods.append(dict(number=lab,name=nm,topics=split_topics(ct),self_learning=sl))
    return mods
