import fitz,sys
P=sys.argv[1]; a=int(sys.argv[2]); b=int(sys.argv[3])
d=fitz.open(P)
for i in range(a-1,b):
    print("=== p",i+1)
    for l in d[i].get_text().split("\n")[:int(sys.argv[4]) if len(sys.argv)>4 else 60]: print(repr(l))
