import fitz,re
d=fitz.open("data/raw/_unclassified/SEM-V.pdf")
pats={"DS":r"DETAILED SYLLABUS","TB":r"^\s*Text\s*Books?","REF":r"^\s*References?\s*:","SLT":r"Self-?\s*learning","SS":r"Self-?\s*Study","PRE":r"Prerequisite","DRAFT":r"DRAFT","SLE":r"Suggested List","ASS":r"^\s*Assessment","CC":r"^\s*Course\s*$","SELF":r"(?i)self"}
for i,p in enumerate(d,1):
    ls=p.get_text().split("\n")
    out=[]
    for k,r in pats.items():
        c=sum(1 for l in ls if re.search(r,l))
        if c: out.append(f"{k}{c}")
    if i>=10: print(i,len(ls),ls[2:5] if False else "",*out)
