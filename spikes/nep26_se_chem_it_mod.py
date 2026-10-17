"""Spike: module-table extraction for nep26-se-chem-it (throwaway). Row start = expected sequential number line."""
import re,sys
sys.path.insert(0,'spikes')
from nep26_se_chem_it_seg import segment
ROMAN=["I","II","III","IV","V","VI","VII","VIII","IX","X"]
STOP=re.compile(r"^\s*(Text\s*Books?|Textbooks?|Reference Books?|References?|Online References|Online Resources|Free Online Courses|Assessment)\s*:?\s*$",re.I)
COTAIL=re.compile(r"^\s*(CO|LO)\s?\d")
DETAIL=re.compile(r"^\s*Detailed\s+Content\s*$",re.I)
def table(s):
    t0=[n for n,(i,j,l) in enumerate(s) if DETAIL.match(l)]
    if not t0: return None
    a=t0[0]
    b=len(s)
    for n in range(a,len(s)):
        if STOP.match(s[n][2]): b=n;break
    return a,b
def numcand(l,k):
    x=l.strip()
    return x in (str(k),f"{k:02d}",ROMAN[k-1] if k<=10 else None)
HEAD=re.compile(r"(?i)^\s*DETAILED\s+SYLLABUS")
def rows(s):
    """attempt 2: every table scope starts at a 'DETAILED SYLLABUS' heading or a 'Detailed Content' line not within 30 lines
    of a start; ends at next start or first STOP heading; row counter restarts per scope."""
    starts=[]
    for n,(i,j,l) in enumerate(s):
        if HEAD.match(l) or (DETAIL.match(l) and not (starts and n-starts[-1]<30)):
            if not (starts and n-starts[-1]<30): starts.append(n)
    if not starts: return None
    out=[]
    for t,a in enumerate(starts):
        b=len(s)
        for n in range(a+1,len(s)):
            if STOP.match(s[n][2]) and t==len(starts)-1 or (t<len(starts)-1 and n>=starts[t+1]):
                b=n;break
            if STOP.match(s[n][2]): b=n;break
        k=1;cur=None
        for n in range(a+1,b):
            l=s[n][2]
            nxt=s[n+1][2] if n+1<len(s) else ""
            # attempt 3: also reject a number-like line followed by a dash cell (row 0 hours cell '01' then '--')
            if numcand(l,k) and not COTAIL.match(nxt) and not re.match(r"^\s*(--|-|–)\s*$",nxt):
                cur={"num":l.strip(),"start":(s[n][0],s[n][1]),"lines":[]};out.append(cur);k+=1;continue
            if cur is not None: cur["lines"].append(s[n][2])
    return out
if __name__=="__main__":
    for kk in "ab":
        for code,s in segment(kk):
            rr=rows(s)
            print(kk,code,None if rr is None else [(x["num"],x["start"]) for x in rr])
