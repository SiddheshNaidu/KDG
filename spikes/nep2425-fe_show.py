import fitz,sys,glob
f=sorted(glob.glob("data/raw/2024-25-scheme/FE/*.pdf"))[int(sys.argv[1])]
p=int(sys.argv[2]); a=int(sys.argv[3]); b=int(sys.argv[4])
L=fitz.open(f)[p-1].get_text().split("\n")
for i,l in enumerate(L[a:b],a): print(i,repr(l))
