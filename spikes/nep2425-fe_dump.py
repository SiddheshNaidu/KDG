import fitz,glob,sys
d="data/raw/2024-25-scheme/FE/"
for f in sorted(glob.glob(d+"*.pdf")):
    doc=fitz.open(f)
    print("==",f,len(doc))
    for i,p in enumerate(doc):
        L=p.get_text().split("\n")
        print(" p",i+1,len(L))
