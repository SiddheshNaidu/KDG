import fitz,re
d=fitz.open("data/raw/_unclassified/SEM-V.pdf")
code=re.compile(r"^\s*(\d{7,8})\s*$")
first={}
for i,p in enumerate(d,1):
    if i<10: continue
    for l in p.get_text().split("\n"):
        m=code.match(l)
        if m and m.group(1) not in first: first[m.group(1)]=i
print(first, len(first))
