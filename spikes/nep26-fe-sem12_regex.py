"""Throwaway spike: run each documented regex against EVERY course occurrence in nep26-fe-sem12 and write
docs/evidence/regex_runs/nep26-fe-sem12_<name>.txt.   Usage (repo root):
  PYTHONIOENCODING=utf-8 python spikes/nep26-fe-sem12_regex.py <name|all>
"""
import importlib.util,re,sys,os,collections
def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
ex=load("spikes/nep26-fe-sem12_extract.py","ex"); sg=ex.sg; pr=sg.pr; C=ex.C; RX=ex.RX
tv=load("spikes/topic_validity.py","tv")
OUT="docs/evidence/regex_runs/"; FAM="nep26-fe-sem12"
PNAME=[p.split("/")[0] for p in pr.PDFS]
def out(name,cmdextra,regexes,matched,total,fails,extra=()):
    os.makedirs(OUT,exist_ok=True)
    with open(f"{OUT}{FAM}_{name}.txt","w",encoding="utf-8") as f:
        f.write(f"command: cd /c/Users/Siddhesh/Documents/KDG && PYTHONIOENCODING=utf-8 python spikes/nep26-fe-sem12_regex.py {name}{cmdextra}\n")
        for r in regexes: f.write(f"regex: {r}\n")
        f.write(f"matched/total: {matched}/{total}\n")
        for e in extra: f.write(e+"\n")
        f.write(f"failures ({len(fails)}), verbatim as pdf | page:line | text:\n")
        for x in fails: f.write("  "+x+"\n")
    print(name,f"{matched}/{total}","failures",len(fails))
def courses():
    for n in range(6):
        L,cs=sg.segment_pdf(n)
        for c in cs: yield n,L,c
# ---------------------------------------------------------------- detect
def run_detect():
    m=0;f=[]
    rx=re.compile(RX["detect"])
    for n in range(6):
        hit=[(i,j,l) for i,j,l in pr.lines(pr.PDFS[n]) if i<=2 and rx.search(l)]
        if hit: m+=1
        else: f.append(f"{PNAME[n]} | none on pages 1-2")
    out("detect","",[RX["detect"]+"   (searched pages 1-2, per PDF)"],m,6,f)
    # DRAFT watermark negative check
    rxd=re.compile(r"\bDRAFT\b"); hits=[]
    rxd2=re.compile(r"(?i)\bdraft")
    loose=[]
    for n in range(6):
        for i,j,l in pr.lines(pr.PDFS[n]):
            if rxd.search(l): hits.append(f"{PNAME[n]} | p{i}:{j} | {l.strip()}")
            if rxd2.search(l): loose.append(f"{PNAME[n]} | p{i}:{j} | {l.strip()}")
    out("draft_watermark","",[r"\bDRAFT\b (case-sensitive, every line of every PDF)",r"(?i)\bdraft (case-insensitive, for comparison)"],len(hits),"6 PDFs scanned (matched = lines containing the DRAFT token; 0 means no DRAFT watermark text in get_text() output)",loose,
        extra=[f"case-sensitive 'DRAFT' lines found: {len(hits)}",f"case-insensitive 'draft' lines found (all are the word 'Drafting'/'drafting'): {len(loose)}"])
# ---------------------------------------------------------------- course_code
def scheme_expected(n):
    """codes in every line before the first Objectives line, NO wrap-joining (joining misfires in summary tables where a
    bare code is followed by a bare credit digit). 3-digit codes that are the prefix of a listed 4-digit code are dropped
    (they are wrap fragments such as 'BSC202' + '2'); codes ending in X are placeholders."""
    L=list(pr.lines(pr.PDFS[n]))
    fo=min(k for k,(i,j,l) in enumerate(L) if re.search(r"(Course|Lab) Objectives",l))
    codes=set()
    for k,(i,j,l) in enumerate(L[:fo]):
        m=sg.CODE.match(l)
        if m and i>=8 and not l.strip().startswith("http"): codes.add(m.group(1))
    codes={c for c in codes if not c.endswith("X")}
    return {c for c in codes if not (re.fullmatch(r"[A-Z]{2,5}\d{3}",c) and any(d!=c and d.startswith(c) for d in codes))}
def run_course_code():
    m=0;t=0;f=[];info=[]
    for n in range(6):
        exp=scheme_expected(n); L,cs=sg.segment_pdf(n); got={c["code"] for c in cs}
        info.append(f"{PNAME[n]}: expected_from_scheme_tables={len(exp)} segmented={len(got)} missing={sorted(exp-got)} extra={sorted(got-exp)}")
        for c in sorted(exp):
            t+=1
            if c in got: m+=1
            else: f.append(f"{PNAME[n]} | expected code {c} (in scheme tables before first Objectives line) not segmented")
        for c in sorted(got-exp): f.append(f"{PNAME[n]} | segmented code {c} not in scheme-table expectation")
    out("course_code","",[RX["course_code"]+"   (+ join rule: bare 'ABC202' line followed by a bare 1-digit line is one code; see spikes/nep26-fe-sem12_seg.py joined())"],m,t,f,extra=info)
# ---------------------------------------------------------------- title
def run_title():
    m=0;t=0;f=[]
    for n,L,c in courses():
        t+=1
        lines=[(i,j,l) for i,j,l in c["lines"]]
        # code occurrences inside segment
        idx=[k for k,(i,j,l) in enumerate(lines) if C["course_code"].match(l) and C["course_code"].match(l).group(1)==c["code"] or (C["course_code"].match(l) and C["course_code"].match(l).group(1)==c["code"][:-1] and lines[k+1:k+2] and lines[k+1][2].strip()==c["code"][-1])]
        if len(idx)<2: f.append(f"{PNAME[n]} | {c['code']} | fewer than 2 code occurrences ({len(idx)})"); continue
        t1=ex.title_from(lines,idx[0]); t2=ex.title_from(lines,idx[1])
        norm=lambda s:re.sub(r"[^a-z0-9]","",s.lower())
        if t1 and norm(t1)==norm(t2): m+=1
        else: f.append(f"{PNAME[n]} | {c['code']} p{lines[idx[0]][0]}:{lines[idx[0]][1]} | occ1={t1!r} occ2={t2!r}")
    pre=0
    out("title","",["title = text after code on the same line + following lines until blank / '--' / '-' / pure number (max 4 lines); PASS when occurrence 1 and occurrence 2 titles agree after lowercasing and stripping non-alphanumerics"],m,t,f)
# ---------------------------------------------------------------- module etc
def module_data():
    res=[]
    for n,L,c in courses():
        lines=ex.clean(c); r=ex.find_modules(lines)
        res.append((n,c,lines,r))
    return res
def where(lines,k): i,j,_=lines[k]; return f"p{i}:{j}"
def run_table_hdr():
    m=0;t=0;f=[];info=[]
    for n,c,lines,r in module_data():
        if ex.is_lab(c["code"]): continue
        t+=1
        if r["table"]: m+=1
        else: f.append(f"{PNAME[n]} | {c['code']} | no line matching table_hdr in course segment (pages {lines[0][0]}-{lines[-1][0]})")
    lab=[(PNAME[n],c["code"],bool(r["table"])) for n,c,lines,r in module_data() if ex.is_lab(c["code"])]
    labtab=collections.Counter(x[1] for x in lab if x[2])
    out("table_hdr","",[RX["table_hdr"]+"   (denominator = course occurrences whose code is NOT lab-style [A-Z]*L\\d)"],m,t,f,
        extra=[f"lab-style courses (code [A-Z]*L\\d) total {len(lab)}; of these with a table_hdr line: {sum(1 for x in lab if x[2])} -> codes {dict(labtab)}"])
def max_co(lines,a,b):
    mx=0
    for k in range(a,b):
        for m_ in re.finditer(r"(?<![A-Za-z])(?:CO|LO)\s?-?(\d)",lines[k][2]):
            if C["tail"].match(lines[k][2]): mx=max(mx,int(m_.group(1)))
    return mx
def run_module_row():
    m=0;t=0;f=[];stats=collections.Counter();agree=0;agree_t=0;disagree=[]
    for n,c,lines,r in module_data():
        if not r["table"]: continue
        t+=1; k=len(r["modules"]); styles={mm["style"] for mm in r["modules"]}
        stats[tuple(sorted(styles))]+=1
        mc=max_co(lines,*r["table"])
        ok = k>=1 and [mm["n"] for mm in r["modules"]]==list(range(1,k+1))
        if ok and mc and k<mc and 'trade' not in styles: ok=False   # trade-style courses map several COs to one Trade (see VSEC101 note), so the CO check is not applied to them
        if ok: m+=1
        else: f.append(f"{PNAME[n]} | {c['code']} | found {k} modules, max CO/LO tail index in table region = {mc} (table at {where(lines,r['table'][0])})")
        if mc:
            agree_t+=1
            if mc==k: agree+=1
            else: disagree.append(f"{PNAME[n]} | {c['code']} | modules found {k} vs max CO/LO tail index {mc}")
    ex_=[f"denominator = course occurrences that have a table_hdr line ({t}); matched = contiguous module numbers 1..K with K>=1 AND (unless Trade-style) K >= max CO/LO index seen in whole-line tails of the table region",
         "module styles found (count of course occurrences): "+str(dict(stats)),
         f"informational: K == max CO/LO tail index: {agree}/{agree_t}; K != max index list:"]+["    "+x for x in disagree]
    out("module_row","",[RX["module_roman"],RX["module_arabic"],RX["module_trade"],"rule: module n starts at the first line (after table_hdr, before stop) that equals n (Roman, or Arabic with optional leading 0 / trailing '.', or 'Trade-n' possibly split over two lines; Roman numeral may be split over two adjacent non-blank lines) and whose next non-blank line has letters, is not a tail line and is not itself a Roman numeral"],m,t,f,extra=ex_)
def run_prereq():
    """strict regex anywhere inside the table region (table_hdr..stop); records WHERE it sits relative to module markers."""
    m=0;t=0;f=[];sp=collections.Counter();absent=set();pos=collections.Counter()
    rx=C["prereq"]; loose=re.compile(r"(?i)pre-?requisite")
    for n,c,lines,r in module_data():
        if not r["modules"]: continue
        t+=1
        txt=[l for _,_,l in lines]; a,b=r["table"]
        hits=[k for k in range(a+1,b) if rx.search(txt[k])]
        lo=[k for k in range(a+1,b) if loose.search(txt[k])]
        if hits:
            m+=1
            sp[re.sub(r"\s+"," ",re.sub(r"^\s*0\s+","",txt[hits[0]]).strip())[:14]]+=1
            pos["before module 1" if all(True for _ in [0]) and True else ""]+=0
        else: absent.add(c["code"])
        for k in lo:
            if not rx.search(txt[k]): f.append(f"{PNAME[n]} | {c['code']} {where(lines,k)} | loose-only (strict missed): {txt[k].strip()[:80]!r}")
    # position census: before first module marker vs inside a module
    for n,c,lines,r in module_data():
        if not r["modules"]: continue
        txt=[l for _,_,l in lines]; a,b=r["table"]
        first=None
        starts=[]
        # recompute first module marker line index via raw content: region before module 1 is r["prereq"]
        pre_hit=any(rx.search(l) for l in r["prereq"])
        pos["before module 1" if pre_hit else ("inside module(s) only" if any(rx.search(l) for mm in r["modules"] for l in mm["raw"]) else "none")]+=1
    out("prereq","",[RX["prereq"],"region searched = table_hdr..stop; denominator = course occurrences with >=1 module found; failures = lines containing 'prerequisite' (loose, case-insensitive) that the strict regex does not match (e.g. prose mid-sentence)"],m,t,f,
        extra=["course occurrences with NO strict match anywhere in the table region (observation, not failures): "+", ".join(sorted(absent)),
               "first-spelling census (first 14 chars after optional leading '0'): "+str(dict(sp)),
               "position census (course occurrences): "+str(dict(pos))])
def run_self_learning():
    rx=C["self_learning"]; loose=re.compile(r"(?i)self.{0,3}(learn|stud)")
    strict=0;loo=0;f=[];sp=collections.Counter()
    for n,c,lines,r in module_data():
        for i,j,l in lines:
            if loose.search(l):
                loo+=1
                m_=rx.search(l)
                if m_: strict+=1; sp[(re.sub(r"\s+"," ",m_.group(0)).strip(), "line-start" if l.lstrip().startswith("#") or l.lstrip().lower().startswith("self") else "mid-line")]+=1
                else: f.append(f"{PNAME[n]} | {c['code']} p{i}:{j} | {l.strip()}")
    out("self_learning","",[RX["self_learning"],"loose reference: (?i)self.{0,3}(learn|stud)  (every line of every course segment)"],strict,loo,f,
        extra=["spellings matched (count over all PDFs x courses): "+str(dict(sp))])
def run_tail():
    rx=C["tail"]; loose=re.compile(r"\b(CO|LO)\s?-?\d")
    strict=0;loo=0;f=[];vals=collections.Counter()
    for n,c,lines,r in module_data():
        if not r["table"]: continue
        a,b=r["table"]
        for k in range(a,b):
            l=lines[k][2]
            if loose.search(l):
                loo+=1
                if rx.match(l): strict+=1; vals[re.sub(r"\s+","",l)[:6]]+=0
                else: f.append(f"{PNAME[n]} | {c['code']} {where(lines,k)} | {l.strip()[:90]}")
    out("tail","",[RX["tail"],"loose reference: \\b(CO|LO)\\s?-?\\d on lines inside table region (table_hdr..stop)"],strict,loo,f)
def run_stop():
    m=0;t=0;f=[];sp=collections.Counter()
    for n,c,lines,r in module_data():
        if not r["table"]: continue
        t+=1
        if r["stop"]: m+=1; sp[re.sub(r"\s+"," ",r["stop"])[:24]]+=1
        else: f.append(f"{PNAME[n]} | {c['code']} | no stop marker after table_hdr (segment ends p{lines[-1][0]})")
    out("stop","",[RX["stop"]],m,t,f,extra=["stop-line spellings (first 24 chars): "+str(dict(sp))])
def run_lab_hdr():
    m=0;t=0;f=[]
    rx=C["lab_hdr"]
    for n,c,lines,r in module_data():
        if not ex.is_lab(c["code"]): continue
        t+=1
        if any(rx.match(l) for _,_,l in lines): m+=1
        else: f.append(f"{PNAME[n]} | {c['code']} | no 'List of Experiments' line")
    out("lab_hdr","",[RX["lab_hdr"]+"   (denominator = lab-style code occurrences)"],m,t,f)
# ---------------------------------------------------------------- topics
def run_topics():
    per=collections.Counter();tot=0;uniq={};perpdf=collections.defaultdict(lambda:[0,0]);ex_viol=collections.defaultdict(list)
    seen=set();excluded=collections.Counter()
    for n,c,lines,r in module_data():
        if not r["modules"]: excluded[c["code"]]+=1; continue
        for mm in r["modules"]:
            nm,ct=ex.split_name_content(mm["raw"],mm["style"])
            tp,sl=ex.topics_from(ct)
            for t_ in tp:
                tot+=1; perpdf[PNAME[n]][0]+=1
                v=tv.validate(t_)
                if v: perpdf[PNAME[n]][1]+=1
                for x in v:
                    per[x]+=1
                    if len(ex_viol[x])<4: ex_viol[x].append(f"{PNAME[n]}|{c['code']}|{t_[:70]}")
                if (c["code"],t_) not in seen:
                    seen.add((c["code"],t_)); uq=uniq.setdefault("n",[0,0]); uq[0]+=1; uq[1]+=bool(v)
    ex_=[f"total topics (all PDFs x course occurrences, with module tables): {tot}",
         f"topics with >=1 violation: {sum(v[1] for v in perpdf.values())}  ({100*sum(v[1] for v in perpdf.values())/max(tot,1):.1f}%)",
         f"unique (course_code,topic) pairs: {uniq['n'][0]}, with >=1 violation: {uniq['n'][1]}",
         "violations by rule id (a topic may violate several): "+str(dict(sorted(per.items()))),
         "per PDF [topics, topics_with_violation]: "+str(dict(perpdf)),
         "course codes excluded (no modules found by module_row): "+str(dict(excluded)),
         "examples per rule:"]+[f"  {k}: {v}" for k,v in sorted(ex_viol.items())]
    out("topic_validity","",["spike extractor: spikes/nep26-fe-sem12_extract.py topics_from() split on [;,.:] / ' - ' / parentheses / bullets / dotted numbering; validate() from spikes/topic_validity.py"],tot-sum(v[1] for v in perpdf.values()),tot,[],extra=ex_)
RUN={"detect":run_detect,"draft_watermark":run_detect,"course_code":run_course_code,"title":run_title,"table_hdr":run_table_hdr,"module_row":run_module_row,"prereq":run_prereq,"self_learning":run_self_learning,"tail":run_tail,"stop":run_stop,"lab_hdr":run_lab_hdr,"topic_validity":run_topics}
if __name__=="__main__":
    w=sys.argv[1]
    for k,fn in RUN.items():
        if w in("all",k) and not (w=="all" and k=="draft_watermark"): fn()
