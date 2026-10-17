import fitz,glob
for f in sorted(glob.glob("data/raw/2024-25-scheme/FE/*.pdf")):
    d=fitz.open(f); print(f.split("/")[-1],[ (i+1,len(p.get_images()),len(p.get_drawings()),len(list(p.annots()))) for i,p in enumerate(d)], d.metadata.get("producer"))
d=fitz.open(sorted(glob.glob("data/raw/2024-25-scheme/FE/*.pdf"))[2])
t="".join(p.get_text() for p in d)
import re
for k in ["entroid","riction","forc\n","Robot"]: print(k,[m.start() for m in re.finditer(k,t)][:6])
p=d[2]
print(p.rect, [b[:4] for b in p.get_text("blocks") if "forc" in b[4]][:3])
