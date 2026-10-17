import fitz,sys
d=fitz.open(sys.argv[1])
for pg in map(int,sys.argv[2].split(",")):
    L=[l.strip() for l in d[pg-1].get_text().split("\n") if l.strip()]
    print("=== p",pg); print(" | ".join(L)[:int(sys.argv[3])])
