"""Module-table parser spike for nep26-sem56 (throwaway). Row = lines between Roman N and Roman N+1 (or stop marker)."""
import sys,re
sys.path.insert(0,"spikes")
import importlib; P=importlib.import_module("nep26-sem56_parse")
ORD=["I","II","III","IV","V","VI","VII","VIII"]
TAIL=re.compile(r"^\s*((C[O0]|L[O0])\s?\d+(\s*(,|&|-|–|to|and)\s*((C[O0]|L[O0])\s?)?\d+)*)\s*$")
TAIL_LAX=re.compile(r"^\s*(C[O0]|LO|L0)\s?\d")  # unused helper
HRS=re.compile(r"^\s*(\d{1,2})\s*$")
SELF=re.compile(r"(?i)\bself[\s\-–]*(learning|study)\b")
def parse(L):
    r=P.parse_modules(L)
    if r is None: return None
    reg,stop=r
    rows=[];cur=None;exp=0;pre=[];inpre=False
    for p,n,l in reg:
        s=l.strip()
        if cur is None and exp==0 and not inpre and re.match(r"^0+$",s): inpre=True; continue
        if cur is None and P.PRE.match(s): continue
        if exp<len(ORD) and s==ORD[exp]:
            cur={"num":s,"lines":[],"tail":None,"hours":None,"page":p,"pos":(p,n)};rows.append(cur);exp+=1;inpre=False;continue
        if cur is None:
            if inpre: pre.append(s)
            continue
        cur["lines"].append((p,n,s))
    for r in rows:
        ls=r["lines"]
        for k,(p,n,s) in enumerate(ls):
            if TAIL.match(s):
                r["tail"]=s
                j=k-1
                while j>=0 and ls[j][2]=="": j-=1
                if j>=0 and HRS.match(ls[j][2]) and s.lstrip()[0] in 'Cc':
                    r["hours"]=ls[j][2]; del ls[j]; k-=1
                del ls[k]   # remove tail line
                break
    return rows,pre,stop,reg
def reg_stop(L,stop):
    return None
if __name__=="__main__":
    pages=P.load();segs,first=P.segments(pages)
    for c,s,e in segs:
        L=P.lines_of(pages,s,e)
        r=parse(L) if any(P.DS.match(l) for _,_,l in L) else None
        if not r: print(c,"noDS");continue
        rows,pre,stop,reg=r
        print(c,"mods",len(rows),"hrs",[x["hours"] for x in rows],"tails",[x["tail"] for x in rows],"self",[bool(any(SELF.search(y[2]) for y in x["lines"])) for x in rows],"stop",reg_stop(L,stop))
