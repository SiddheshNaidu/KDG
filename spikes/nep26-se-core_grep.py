import fitz,sys,re
p=sys.argv[1]; rx=re.compile(sys.argv[2])
d=fitz.open(p)
for i,pg in enumerate(d):
    for j,l in enumerate(pg.get_text().split("\n")):
        if rx.search(l): print(i+1,j,repr(l))
