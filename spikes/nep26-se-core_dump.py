"""Writes the three raw dumps (<=60 lines each, unedited get_text() line order, trailing spaces kept)."""
import fitz
R="data/raw/2019-scheme/Computer-Engineering/6.24-N-B.E.-Computer-Engineering-Sem-III-IV.pdf"
D=fitz.open(R)
def dump(name,page,a,n=60):
    ls=D[page-1].get_text().split("\n")
    sel=ls[a:a+n]
    open("docs/evidence/dumps/"+name,"w",encoding="utf-8",newline="\n").write("\n".join(sel)+"\n")
    print(name,len(sel),"lines from page line index",a)
dump("nep26-se-core_computer-engineering-2113111-normal-theory_p17.txt",17,0)
dump("nep26-se-core_computer-engineering-2113114-odd-theory-arabic-modules_p24.txt",24,82)
import re
for pg in (30,31):
    for j,l in enumerate(D[pg-1].get_text().split("\n")):
        if re.search(r"(?i)list of experiments",l): print("lab marker",pg,j,repr(l))
dump("nep26-se-core_computer-engineering-2113116-lab_p30.txt",30,85,31)
