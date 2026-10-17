"""Runs every documented regex of family nep26-se-core against EVERY course/PDF and writes docs/evidence/regex_runs/nep26-se-core_*.txt"""
import sys,re,glob,importlib,os,collections
import fitz
sys.path.insert(0,"spikes")
E=importlib.import_module("nep26-se-core_extract"); L=E.L
TV=importlib.import_module("topic_validity")
OUT="docs/evidence/regex_runs/"
CMD="PYTHONIOENCODING=utf-8 python spikes/nep26-se-core_regex_runs.py"
def short(p): return p.split("/")[-1]
def write(name,regex,total_desc,matched,total,fails,extra=""):
    with open(OUT+f"nep26-se-core_{name}.txt","w",encoding="utf-8") as f:
        f.write(f"command: {CMD}\nregex: {regex}\ndenominator: {total_desc}\nmatched/total: {matched}/{total}\nfailures ({len(fails)}):\n")
        for x in fails: f.write("  "+x+"\n")
        if extra: f.write(extra)
    print(name,f"{matched}/{total}",len(fails),"failures")
ALL=[]
for p in L.PDFS:
    for c in E.courses(p): c["pdf"]=p; ALL.append(c)
DET=re.compile(r"^\s*(Detailed Content|Topics|Topic Description|Mapping)\s*$")
for c in ALL: c["modtable"]=any(DET.match(x[2]) for x in c["lines"])
MT=[c for c in ALL if c["modtable"]]
def loc(c): return f"{short(c['pdf'])} pages {c['pages'][0]}-{c['pages'][-1]} {c['code']} {c['title']}"

# 1 detect (PDF level), also specificity on every other PDF in data/raw
S=re.compile(r"^\s*Self-learning\s+Topics?\s*:",re.M); T=re.compile(r"^\s*Self-Study\s*:",re.M); C7=re.compile(r"^\d{7}\s*$",re.M)
def pred(f):
    t="\n".join(p.get_text() for p in fitz.open(f))
    return len(S.findall(t))>=40 and len(T.findall(t))>=2 and len(C7.findall(t))>=60, (len(S.findall(t)),len(T.findall(t)),len(C7.findall(t)))
fails=[];m=0
for p in L.PDFS:
    ok,cnt=pred(L.R+p)
    if ok:m+=1
    else: fails.append(f"{p} counts(self-learning,self-study,code)={cnt}")
fp=[]
fam={L.R+p for p in L.PDFS}
others=[f.replace("\\","/") for f in glob.glob("data/raw/**/*.pdf",recursive=True)]
for f in others:
    if f in fam: continue
    ok,cnt=pred(f)
    if ok: fp.append(f"{f} counts={cnt}")
write("detect",r"PDF-level: count(^\s*Self-learning\s+Topics?\s*:)>=40 AND count(^\s*Self-Study\s*:)>=2 AND count(^\d{7}\s*$)>=60 over line-joined get_text()","6 family PDFs",m,6,fails,f"false positives among the {len(others)-6} other PDFs in data/raw: {len(fp)}\n"+"\n".join("  "+x for x in fp)+"\n")

# 2 course_start: attempt1 and attempt2
CODE=re.compile(r"\d{7}\s*")
def starts(ls,att):
    st=[];seen=set()
    for k,(pg,j,l) in enumerate(ls):
        if CODE.fullmatch(l) and k>0:
            if att==1: ok=ls[k-1][2].strip()=="Total" and any("Credits Assigned" in x[2] for x in ls[max(0,k-9):k])
            else: ok=ls[k-1][2].strip().endswith("Total") and any("Credits Assigned" in x[2] for x in ls[max(0,k-14):k])
            if ok and pg>=16 and l.strip() not in seen: seen.add(l.strip()); st.append((pg,l.strip()))
    return st
for att in (1,2):
    m=tot=0;fails=[]
    for p in L.PDFS:
        ls=L.lines(p); found={c for _,c in starts(ls,att)}
        allc={l.strip() for pg,j,l in ls if pg>=16 and CODE.fullmatch(l)}
        tot+=len(allc); m+=len(found&allc)
        for c in sorted(allc-found):
            pg=[x[0] for x in ls if x[2].strip()==c and x[0]>=16][0]
            fails.append(f"{p} code {c} first seen page {pg} not detected")
    write(f"course_start_attempt{att}",("attempt1: " if att==1 else "attempt2: ")+(r"line ^\d{7}\s*$ whose previous line stripped == 'Total' and 'Credits Assigned' within 9 lines before" if att==1 else r"line ^\d{7}\s*$ whose previous line stripped ends with 'Total' and 'Credits Assigned' within 14 lines before"),"distinct 7-digit code lines on pages>=16 per PDF (page 15/16 is the end of the program structure in every PDF) (sum over 6 PDFs)",m,tot,fails)

# 3 title wrap
def norm(s): return re.sub(r"[^a-z0-9]","",s.lower())
m=0;fails=[]
for c in ALL:
    ls=c["lines"]; idx=[i for i,x in enumerate(ls) if x[2].strip()==c["code"]]
    t2=None
    if len(idx)>1:
        t=[];k=idx[1]+1
        while k<len(ls) and not L.TITLE_END.fullmatch(ls[k][2]): t.append(ls[k][2].strip()); k+=1
        t2=re.sub(r"\s+"," "," ".join(t)).strip()
    if t2 is not None and norm(t2)==norm(c["title"]): m+=1
    else: fails.append(f"{loc(c)} | teaching-table title={c['title']!r} | examination-table title={t2!r}")
write("title_wrap",r"title = lines after code line joined by ' ' until first line matching ^[\d\-–]+\s*$ ; compared (alphanumerics, case-folded) with same rule applied at 2nd occurrence of the code","all detected courses",m,len(ALL),fails)

# 4 syllabus header (attempt1: header title only; attempt2 adds 'Name of Module' column header for the header-less Computational Theory layout)
HDR=E.HDR_RX
HDR2=re.compile(r"^\s*(DETAIL(ED)?\s+SYLLABUS\s*:?|Name of Module)\s*$")
m=0;fails=[];m2=0;f2=[]
for c in MT:
    if any(HDR.match(x[2]) for x in c["lines"]): m+=1
    else: fails.append(loc(c)+" | no line matches header regex")
    if any(HDR2.match(x[2]) for x in c["lines"]): m2+=1
    else: f2.append(loc(c)+" | no line matches header regex")
D4=r"courses with a line ^\s*(Detailed Content|Topics|Topic Description|Mapping)\s*$ (module-table courses)"
write("syllabus_header_attempt1",HDR.pattern,D4,m,len(MT),fails)
write("syllabus_header_attempt2",HDR2.pattern,D4,m2,len(MT),f2,"note: in Computational Theory the line 'Name of Module' comes AFTER the first roman numerals I and II in line order (see dump), so it is a detection signal only, not a region start\n")

# 5 module row
RN=["I","II","III","IV","V","VI","VII","VIII"]
m=0;fails=[]; styles={"roman":0,"arabic":0}
for c in MT:
    r=E.region(c); mods=E.split_modules(r); labs=[x[0] for x in mods]
    arabic = bool(labs) and labs[0]=="1"
    exp6=[str(i) for i in range(1,7)] if arabic else RN[:6]
    styles["arabic" if arabic else "roman"]+=1
    if labs==exp6: m+=1
    else: fails.append(f"{loc(c)} | markers found {labs} expected {exp6}")
write("module_row",r"roman: ^\s*(I|II|III|IV|V|VI|VII|VIII)\s*$ inside region (header .. stop marker); arabic: ^\s*[1-9]\s*$ preceded by tail/hours/header line and not followed by a pure number","module-table courses; success = markers are exactly I..VI (or 1..6); '6 modules' is an observed assumption, see UNKNOWN",m,len(MT),fails,f"styles among module-table courses: {styles}\n")

# 6 prerequisite row (attempt1 table row; attempt2 adds header-level 'Prerequisite:' line)
PR=re.compile(r"^\s*Pre-?requisite[s]?\s*$",re.I)
PR2=re.compile(r"^\s*Pre-?requisite[s]?\s*[:.]",re.I)
m1=0;f1=[];m2=0;f2=[]
for c in MT:
    r=E.region(c); ok1=False
    for i,x in enumerate(r):
        if PR.match(x[2]) and i>0 and r[i-1][2].strip()=="0": ok1=True
    ok2=ok1 or any(PR2.match(x[2]) for x in c["lines"])
    if ok1:m1+=1
    else: f1.append(loc(c)+" | no ('0' line immediately before 'Prerequisite' line) in region")
    if ok2:m2+=1
    else: f2.append(loc(c)+" | neither table row nor header-level 'Prerequisite:' line")
write("prereq_row_attempt1",r"line '^\s*0\s*$' immediately followed by line '^\s*Pre-?requisite[s]?\s*$' (case-insens) inside region","module-table courses",m1,len(MT),f1)
m3=0;f3=[]
for c in MT:
    ok3=any(PR.match(x[2]) or PR2.match(x[2]) for x in c["lines"])
    if ok3:m3+=1
    else: f3.append(loc(c)+" | no line matching Prerequisite (row, row without 0, or header-level) in any course page")
write("prereq_row_attempt3",r"any course line matching ^\s*Pre-?requisite[s]?\s*$ or ^\s*Pre-?requisite[s]?\s*[:.] (case-insens)","module-table courses",m3,len(MT),f3)
write("prereq_row_attempt2",r"attempt1 OR any course line matching ^\s*Pre-?requisite[s]?\s*[:.] (case-insens)","module-table courses",m2,len(MT),f2)

# 7 self-learning marker (anchored vs any mention)
ANY=re.compile(r"(?i)self[\s\-–]*(learning|study)"); ANC=E.SELF_RX
m=tot=0;fails=[]
for p in L.PDFS:
    for pg,j,l in L.lines(p):
        if ANY.search(l):
            tot+=1
            if ANC.match(l): m+=1
            else: fails.append(f"{p} page {pg} line {j}: {l!r}")
write("self_marker",r"(?i)^\s*Self[\s\-]*(learning|study)\b","all lines (6 PDFs) containing (?i)self[\s\-–]*(learning|study); failures are mid-sentence mentions (prose), see doc",m,tot,fails)

# 8 tail per module block
TL=E.TAIL_RX
m=tot=0;fails=[]
for c in MT:
    for lab,blk in E.split_modules(E.region(c)):
        tot+=1
        if any(TL.match(s) for s in blk): m+=1
        else: fails.append(f"{loc(c)} module {lab}: no CO/LO/L tail line in module block")
write("co_lo_tail_attempt2",TL.pattern,"module blocks of module-table courses",m,tot,fails,"attempt1 regex was ^\\s*(CO|LO)\\s?\\.?\\s?\\d(\\s*[,&]\\s*\\d)*\\s*$ (no Bloom L1.. tails); superseded by attempt2 above; attempt1 measured in-session before change, not saved separately\n")

# 9 stop marker
SM=E.STOP_RX
m=0;fails=[]
for c in MT:
    r=E.region(c); ls=E.strip_header_blocks(c["lines"])
    s=None
    for i,x in enumerate(ls):
        if HDR.match(x[2]): s=i;break
    if s is None:
        for i,x in enumerate(ls):
            if x[2].strip()=="I": s=i;break
    e=s+len(r) if s is not None else None
    if e is not None and e<len(ls) and SM.match(ls[e][2]): m+=1
    elif e is not None and e<len(ls): fails.append(loc(c)+f" | region ended without a stop-marker line (next line: {ls[e][2]!r})")
    else: fails.append(loc(c)+" | region ran to end of course pages")
write("stop_marker",SM.pattern,"module-table courses",m,len(MT),fails)

# 10 topic validity census
cnt=collections.Counter(); tot=0; bad=0; per=[]
for c in MT:
    mods=E.extract(c)
    for md in mods:
        for t in md["topics"]:
            tot+=1; v=TV.validate(t)
            if v: bad+=1
            for x in v: cnt[x]+=1
    per.append((c["code"],sum(len(md["topics"]) for md in mods)))
with open(OUT+"nep26-se-core_topic_validity.txt","w",encoding="utf-8") as f:
    f.write(f"command: {CMD}\nextractor: spikes/nep26-se-core_extract.py extract() (best-effort heuristic, self-learning text excluded); validator: spikes/topic_validity.py validate()\ncourses processed: {len(MT)} (module-table courses)\ntotal topics: {tot}\ntopics with >=1 violation: {bad}\nviolations by rule id (a topic may violate several):\n")
    for k in sorted(cnt): f.write(f"  {k}: {cnt[k]}\n")
    f.write("rules with 0 violations: "+", ".join(r for r in ["R1_word_count_1_to_8","R2_len_over_80_chars","R3_contains_colon_or_semicolon","R4_generic_heading","R5_procedural","R6_leading_numbering","R7_hours_or_CO_leak","R8_no_letters"] if r not in cnt)+"\n")
    f.write("topics per course: "+", ".join(f"{a}:{b}" for a,b in per)+"\n")
print("census",tot,bad,dict(cnt))

# 11 hours + tail pair per module block
m=tot=0;fails=[]
for c in MT:
    for lab,blk in E.split_modules(E.region(c)):
        tot+=1
        ok=any(re.fullmatch(r"\s*\d{1,2}\s*",blk[i]) and E.TAIL_RX.match(blk[i+1]) for i in range(len(blk)-1))
        if ok: m+=1
        else: fails.append(f"{loc(c)} module {lab}: no (hours line ^\s*\d{{1,2}}\s*$ immediately followed by CO/LO/L tail line) in cleaned module block")
write("hours_tail_pair",r"cleaned block lines i,i+1 with ^\s*\d{1,2}\s*$ then tail regex","module blocks of module-table courses",m,tot,fails)

# 12 watermark / noise
W=re.compile(r"(?i)draft|watermark|confidential|specimen")
NZ=re.compile(r"UNIVERSITY OF MUMBAI \(With Effect from 2025-2026\)|^\s*AC\s*[–-]\s*20/5/2025|^\s*Item No\.")
hits=[];nz=collections.Counter()
for p in L.PDFS:
    for pg,j,l in L.lines(p):
        if W.search(l): hits.append(f"{p} page {pg} line {j}: {l!r}")
        if NZ.search(l): nz[(p.split('/')[0],pg)]+=1
write("watermark",W.pattern,"all lines of 6 PDFs; matched = number of PDFs-lines hit (0 means no watermark text observed)",len(hits),sum(len(L.lines(p)) for p in L.PDFS),hits,"noise lines found by "+NZ.pattern+" (pdf,page): "+str(dict(nz))+"\n")
