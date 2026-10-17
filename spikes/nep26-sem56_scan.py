import fitz,re
d=fitz.open("data/raw/_unclassified/SEM-V.pdf")
pat=re.compile(r"^\s*\d{7,8}\s*$")
for i,p in enumerate(d,1):
    ls=p.get_text().split("\n")
    for n,l in enumerate(ls):
        if pat.match(l):
            ctx=[x.strip() for x in ls[max(0,n-1):n+4]]
            print(i,n,"|".join(ctx)[:150])
