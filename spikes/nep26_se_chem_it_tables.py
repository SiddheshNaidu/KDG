"""Spike: table-based module extraction (PyMuPDF find_tables) for nep26-se-chem-it. Throwaway."""
import re,sys,fitz
sys.path.insert(0,'spikes')
from nep26_se_chem_it_seg import segment
from nep26_se_chem_it_lines import PDFS
def cleanc(c): return re.sub(r"\s+"," ",(c or "").replace("\n"," ")).strip()
def header_ys(page):
    ys=[];prev=None
    ls=[]
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines",[]):
            ls.append(("".join(s["text"] for s in l["spans"]).strip(),l["bbox"]))
    ls.sort(key=lambda x:(x[1][1],x[1][0]))
    for n in range(len(ls)-1):
        if ls[n][0]=="Course" and ls[n+1][0]=="Code": ys.append(ls[n][1][1])
    return ys
def course_pages(k):
    segs=segment(k); out=[]
    for t,(code,s) in enumerate(segs):
        pages=sorted({i for i,j,l in s})
        out.append((code,pages))
    return out
def is_hdr(data):
    return cleanc(data[0][0]).startswith("Course Code") if data and data[0] else False
def extract(k,code,pages,doc,next_header_page_y=None):
    """return list of module rows [num,name,content,hours,co] merged across pages. Owner logic: tables after a page's
    'Course Code' header table belong to that course; tables before belong to the previous course."""
    rows=[];started=False
    for pn in pages:
        p=doc[pn-1]
        tabs=sorted(p.find_tables().tables,key=lambda t:t.bbox[1])
        datas=[t.extract() for t in tabs]
        hidx=[n for n,dd in enumerate(datas) if is_hdr(dd)]
        sel=list(range(len(tabs)))
        if hidx:
            owner=None
            for dd in datas[hidx[0]]:
                for c in dd:
                    m=re.search(r"(\d{7})",cleanc(c))
                    if m and not owner: owner=m.group(1)
            if owner==code: sel=[n for n in sel if n>hidx[-1]]
            else: sel=[n for n in sel if n<hidx[0]]
        for n in sel:
            data=datas[n]
            if not data or is_hdr(data): continue
            hdr=[cleanc(c) for c in data[0]]
            is_mod = len(data[0])==5 and re.match(r"(?i)^(hours?|hrs)$",hdr[3]) is not None and re.search(r"(?i)(CO|LO)s?\s*Mappin\s*g?s?",hdr[4]) is not None
            cont = started and len(data[0])==5
            if cont and not is_mod and re.match(r"(?i)^sr\.?\s*no",hdr[0]): started=False; continue
            if not (is_mod or cont): continue
            if is_mod: started=True; data=data[1:]
            for r in data:
                c=[cleanc(x) for x in r]
                if len(c)!=5: continue
                if c[0]=="" and c[1]=="" and rows: rows[-1][2]+=" "+c[2]
                elif c[0]=="" and not c[1] and not c[2]: continue
                else: rows.append(c[:])
    return rows
if __name__=="__main__":
    for k in "ab":
        doc=fitz.open(PDFS[k])
        for code,pages in course_pages(k):
            r=extract(k,code,pages,doc)
            print(k,code,pages,len(r),[ (x[0],x[1][:22],x[3],x[4]) for x in r])
