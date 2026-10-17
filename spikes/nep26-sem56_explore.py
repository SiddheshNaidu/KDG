import fitz,re,sys
d=fitz.open("data/raw/_unclassified/SEM-V.pdf")
for i in range(int(sys.argv[1]),int(sys.argv[2])+1):
    ls=d[i-1].get_text().split("\n")
    print("=== p",i,len(ls)); print("\n".join(f"{n}|{l}" for n,l in enumerate(ls)))
