"""Spike (throwaway): line+x0 extraction of module rows for nep26-se-electrical. Not product code."""
import fitz,re,sys,importlib
seg=importlib.import_module("nep26-se-electrical_segment")
NOISE={"Course","Code","Course Name","Teaching Scheme","Examination Scheme","(Contact Hours/Week)","Credits Assigned","Credits assigned",
 "Theory","Pract.","Tut.","Total","Marks","Theory Marks","Term","Work","Exam.","Exam","Sem.","Duration","(in Hrs.)","in Hrs.)","Internal Assessment Test",
 "(IAT)","Internal Assessment (IAT)","Internal assessment (IAT)","Internal Assessment","End","IAT-","IAT-I","IAT-II","IAT-I +","IAT-II","IAT-I IAT-II","IAT-I","+IAT-II","(Total)",
 "Practical/","Oral","Pract. / Tut.","Pract./Tut.","Prese-","ntation","/Oral","ntation/","Test","1","2","Name of Module","Detailed Content","Hours","CO","Mapping","LO","Sr.","No.","Detail Contents",
 "Name of the Module Detail Content","Module","Total Marks","Pract./","Term Work","Presentation","Presentation/Oral","Work","Exam. Duration","Tut"}
def dict_lines(path):
    out=[]
    for i,p in enumerate(fitz.open(path)):
        for b in p.get_text("dict")["blocks"]:
            for l in b.get("lines",[]):
                t="".join(s["text"] for s in l["spans"]).strip()
                if t: out.append((i+1,round(l["bbox"][0]),t))
    return out
def extract(path):
    DL=dict_lines(path)
    raw=seg.lines(path)
    assert [t for _,t in raw]==[t for _,_,t in DL], "dict order != text order"
    L,objs,codes,segs=seg.courses(path)
    res=[]
    for (s,e),code in zip(segs,codes):
        kind="theory" if L[s][1].startswith("Course") else "lab"
        lines=DL[s:e]
        lo=s
        while lo>0 and DL[lo-1][0]>=DL[s][0]-1: lo-=1
        res.append(dict(code=code,kind=kind,start_page=lines[0][0],lines=lines,ctx=DL[lo:e]))
    return res
def modules(c):
    """returns list of dict(number,name,content,hours,co) using x0 columns; noise stripped by vocabulary."""
    lines=c["lines"]; code=c["code"]
    # find title lines after code occurrences
    titles=set()
    for i,(pg,x,t) in enumerate(lines):
        if t==code:
            j=i+1
            while j<len(lines) and not re.fullmatch(r"--?|\d+|\d\*\+\d|Theory",lines[j][2]) : titles.add(lines[j][2]); j+=1
    start=[i for i,(pg,x,t) in enumerate(lines) if t.startswith("Detailed Syllabus")]
    start=start[0] if start else 0
    keep=[];innoise=False
    n=len(lines)
    for i in range(start+1,n):
        pg,x,t=lines[i]
        nxt=lines[i+1][2] if i+1<n else ""
        is_tail = bool(re.fullmatch(r"\d{1,2}",t) and re.fullmatch(r"(CO|LO)\d",nxt)) or bool(re.fullmatch(r"(CO|LO)\d",t))
        vocab = (t in NOISE or t==code or t in titles or re.fullmatch(r"--?",t) or re.fullmatch(r"\d+",t) and not is_tail) and not is_tail
        if t in("Text Books:","Textbooks:","Text books:","Reference Books:","References:") : break
        keep.append((pg,x,t,vocab))
    # drop noise vocabulary (only lines that are vocab); stray module numbers 'I','II' after 'IAT-' are in vocab through previous-line rule
    out=[];prev=""
    for pg,x,t,v in keep:
        if re.fullmatch(r"(I|II)",t) and prev=="IAT-": prev=t; continue
        prev=t
        if v and not (re.fullmatch(r"(I|II|III|IV|V|VI)",t) or (re.fullmatch(r"[1-6]",t) and x<100)): continue
        out.append((pg,x,t))
    mods=[];cur=None
    for pg,x,t in out:
        if (re.fullmatch(r"(I|II|III|IV|V|VI)",t) and x<95) or (re.fullmatch(r"[1-6]",t) and x<95 and (cur is None or int(t)==cur["n"]+1)):
            cur=dict(number=t,n=int(t) if t.isdigit() else ["I","II","III","IV","V","VI"].index(t)+1,name=[],content=[],hours=None,co=None); mods.append(cur); continue
        if cur is None: continue
        if re.fullmatch(r"\d{1,2}",t) and x>=440: cur["hours"]=t; continue
        if re.fullmatch(r"(CO|LO)\d",t): cur["co"]=t; continue
        (cur["name"] if x<150 else cur["content"]).append(t)
    for m in mods: m["name"]=" ".join(m["name"]); m["content"]=" ".join(m["content"])
    return mods
if __name__=="__main__":
    k=sys.argv[1]
    for c in extract(seg.PDFS[k]):
        if c["kind"]!="theory": continue
        ms=modules(c)
        print(c["code"],[(m["number"],m["name"][:22],len(m["content"].split()),m["hours"],m["co"]) for m in ms])
