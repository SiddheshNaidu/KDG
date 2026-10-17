"""Spike: segment nep26-se-chem-it PDFs into courses (throwaway)."""
import re,sys,collections
sys.path.insert(0,'spikes')
from nep26_se_chem_it_lines import lines,PDFS
CODE=re.compile(r"^\s*(\d{7})\s*$")
GRADE=re.compile(r"^\s*Grade\s*$|Grading|Marks Obtained|Range of Marks|Sd/-")
def load(k):
    return list(lines(PDFS[k]))
def segment(k, L=None):
    L=L or load(k)
    cnt=collections.defaultdict(set)
    for i,j,l in L:
        m=CODE.match(l)
        if m: cnt[i].add(m.group(1))
    starts=[];seen=set()
    for n in range(len(L)-1):
        if L[n][2].strip()=="Course" and L[n+1][2].strip()=="Code" and len(cnt[L[n][0]])<3:
            for m in range(n+2,n+40):
                mm=CODE.match(L[m][2])
                if mm:
                    if mm.group(1) not in seen: seen.add(mm.group(1)); starts.append((n,mm.group(1)))
                    break
    # end of last course: first line matching grading appendix after last start
    endL=len(L)
    for n in range(starts[-1][0],len(L)):
        if re.search(r"Grade Point|Grading|Range of Marks|Marks Obtained", L[n][2]): endL=n; break
    segs=[]
    for t,(n,code) in enumerate(starts):
        e=starts[t+1][0] if t+1<len(starts) else endL
        segs.append((code,L[n:e]))
    return segs
if __name__=="__main__":
    for k in "ab":
        for code,s in segment(k):
            print(k,code,s[0][0],s[-1][0],len(s))
