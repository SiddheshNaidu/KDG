"""Throwaway spike (not product code): extract modules/topics for nep26-fe-sem12 courses. Run from repo root."""
import re,importlib.util
s=importlib.util.spec_from_file_location("sg","spikes/nep26-fe-sem12_seg.py");sg=importlib.util.module_from_spec(s);s.loader.exec_module(sg)
pr=sg.pr
FAMILY="nep26-fe-sem12"
# ---- regexes under test ----
RX={
 "detect": r"As Per NEP 2020",
 "course_code": r"^\s*([A-Z]{2,5}\d{3,4}[A-Z]?)(?![A-Za-z0-9])(.*)$",
 "table_hdr": r"^\s*(?:Detailed ?Contents?|Details)\s*$",
 "lab_hdr": r"^\s*List of Experiments",
 "prereq": r"^\s*(?:0\s+)?(?:No\s+)?[Pp]re-?requisites?\b",
 "self_learning": r"^\s*(?:#\s*[Ss]elf[\s-]*[Ll]earning\s+topics?\s*:?|[Ss]elf-study activities)",
 "tail": r"^\s*(?:(?:CO|LO)\s?\d+(?:\s*[,&/]\s*(?:CO|LO)?\s?\d+)*\s*,?|\d{1,2}|--|-|,)\s*$",
 "stop": r"^\s*(?:Text\s?[Bb]ooks?|TEXT/REFERENCE BOOKS|References?|Online (?:References|Resources)|Assessment\s*:|Term ?[Ww]ork|List of Assignments|Sr\.? ?No\.? Website Name|Website Name)\b",
 "module_roman": r"^\s*(I|II|III|IV|V|VI|VII|VIII)\s*$",
 "module_arabic": r"^\s*0?([1-9])\.?\s*$",
 "module_trade": r"^\s*Trade[\s-]*(\d)?\s*$",
 "module_word": r"^\s*Module\s*(\d)\s*[-–:]?\s*(.*)$",
 "bullet": "^\\s*[•]\\s*",
}
C={k:re.compile(v) for k,v in RX.items()}
ROMAN=["","I","II","III","IV","V","VI","VII","VIII","IX","X"]
def is_lab(code): return bool(re.match(r"^[A-Z]*L\d",code))
def clean(c):
    """lines without page-number line (line 1 of each page)."""
    return [(i,j,l.rstrip()) for i,j,l in c["lines"] if j!=1]
def title_from(lines,k,code_len_join=False):
    """title = text after code on same line + following non-blank lines until blank / '--' / '-' / pure number (max 4 lines).
    Attempt 2: blank lines directly after the code are skipped; trailing footnote marks like ' 2#' / ' 2*' are removed."""
    m=C["course_code"].match(lines[k][2]); rest=m.group(2).strip(); parts=[rest] if rest else []
    q=k+1
    if not rest and q<len(lines) and re.fullmatch(r"\s*\d\s*",lines[q][2]) and re.fullmatch(r"[A-Z]{2,5}\d{3}",m.group(1)): q+=1
    if not parts:
        while q<len(lines) and not lines[q][2].strip(): q+=1
    while q<len(lines) and len(parts)<4:
        t=lines[q][2].strip()
        if not t or re.fullmatch(r"(--|-|\d+(\.\d+)?)",t): break
        parts.append(t); q+=1
    t=re.sub(r"\s+"," "," ".join(parts)).strip()
    return re.sub(r"\s\d[#*]+$","",t)
def outcome_count(lines):
    """number of numbered Course/Lab outcomes."""
    txt=[l for _,_,l in lines]
    st=[k for k,l in enumerate(txt) if re.match(r"\s*(Course|Lab) Outcomes",l)]
    if not st: return None
    n=0
    for l in txt[st[0]+1:st[0]+40]:
        if re.match(r"\s*\d\.\s",l): n+=1
        if re.match(r"\s*(DETAILED|Module|Sr|Detailed|List of)",l): break
    return n
def find_modules(lines):
    """returns dict(table=(a,b) or None, prereq=[lines], modules=[{number,name,raw:[lines],selfl:[...]}])"""
    txt=[l for _,_,l in lines]
    a=next((k for k,l in enumerate(txt) if C["table_hdr"].match(l)),None)
    if a is None: return dict(table=None,prereq=[],modules=[],stop=None)
    b=len(txt); stop=None
    for k in range(a+1,len(txt)):
        if C["stop"].match(txt[k]): b=k; stop=txt[k].strip(); break
    def nxt(k):
        q=k+1
        while q<b and not txt[q].strip(): q+=1
        return q
    nxt_=nxt
    def marker(k,n):
        l=txt[k]
        if C["module_roman"].match(l) and l.strip()==ROMAN[n]: style="roman"
        elif C["module_roman"].match(l) and ROMAN[n].startswith(l.strip()) and l.strip()!=ROMAN[n] and nxt(k)<b and l.strip()+txt[nxt(k)].strip()==ROMAN[n]:
            style="roman"; k=nxt(k)   # Attempt 2: numeral split over two lines (IKS201: 'II'+'I', 'I'+'V', 'V'+'I' across a page break)
        elif C["module_arabic"].match(l) and int(l.strip().rstrip('. '))==n: style="arabic"
        elif C["module_trade"].match(l):
            d=C["module_trade"].match(l).group(1)
            if d is None:
                q2=nxt(k)
                if q2<b and re.fullmatch(r"\s*\d\s*",txt[q2]): d=txt[q2].strip(); k=q2
            if d is None or int(d)!=n: return None
            style="trade"
        else: return None
        q=nxt(k)
        if q>=b: return None
        t=txt[q].strip()
        if C["tail"].match(t) or not re.search(r"[A-Za-z]",t) or C["module_roman"].match(t): return None
        return style
    starts=[];n=1;k=a+1
    while k<b:
        st=marker(k,n)
        if st:
            ex_=0
            if st=="roman" and txt[k].strip()!=ROMAN[n]: ex_=nxt_(k)-k
            starts.append((k+ex_,n,st)); n+=1; k+=ex_
        k+=1
    pre=[]; mods=[]
    first=starts[0][0] if starts else b
    pre=[l for l in txt[a+1:first] if C["prereq"].search(l) or True]
    for idx,(k,n,st) in enumerate(starts):
        e=starts[idx+1][0] if idx+1<len(starts) else b
        raw=[l for l in txt[k+1:e] if not C["tail"].match(l) and l.strip()]
        mods.append(dict(number=ROMAN[n] if st=="roman" else (f"Trade-{n}" if st=="trade" else f"{n:02d}"),n=n,style=st,raw=raw,marker=txt[k]))
    return dict(table=(a,b),prereq=pre,modules=mods,stop=stop)
def split_name_content(raw,style="roman"):
    """module name = leading lines before the first dotted item / bullet / prereq / '#'.
    roman style: also stop at first line longer than 34 chars; arabic style: up to 4 lines."""
    name=[];k=0
    while k<len(raw) and len(name)<4:
        l=raw[k].strip()
        if re.match(r"\d+\.\d+",l) or C["bullet"].match(raw[k]) or l.startswith("#") or re.match(r"(?i)pre-?requisite",l): break
        if style=="roman" and len(l)>34: break
        name.append(l);k+=1
    if style!="roman" and k>=len(raw): name=name[:1]; k=1
    nm=re.sub(r"\s+"," "," ".join(name)).strip()
    nm=re.sub(r"^Module\s*\d\s*[-\u2013:]?\s*","",nm)
    return nm,raw[k:]
def topics_from(content):
    txt=" ".join(l.strip() for l in content)
    selfl=[]
    m=re.search(r"#\s*[Ss]elf[\s-]*[Ll]earning[^:]*:?",txt)
    if m: selfl=[txt[m.end():]]; txt=txt[:m.start()]
    txt=re.sub(r"(?i)\bpre-?requisite\s*:.*?(?=\b\d\.\d|$)","",txt)
    txt=re.sub(r"[•]"," ; ",txt)
    txt=re.sub(r"\b\d+\.\d+\.?\s*"," ; ",txt)
    parts=re.split(r"[;,.:]|\s[–-]\s|\(|\)",txt)
    out=[re.sub(r"\s+"," ",p).strip(" -–") for p in parts]
    return [p for p in out if p],selfl
def all_courses():
    for n in range(6):
        L,cs=sg.segment_pdf(n)
        for c in cs:
            yield n,c
if __name__=="__main__":
    import sys
    n=int(sys.argv[1]);code=sys.argv[2]
    L,cs=sg.segment_pdf(n)
    c=[x for x in cs if x["code"]==code][0]; r=find_modules(clean(c))
    print("table",r["table"],"stop",r["stop"],"nmods",len(r["modules"]))
    for m in r["modules"]:
        nm,ct=split_name_content(m["raw"],m["style"]); tp,sl=topics_from(ct)
        print(m["number"],"|",nm,"|",len(tp),tp[:6],"| selfl:",[s[:50] for s in sl])
