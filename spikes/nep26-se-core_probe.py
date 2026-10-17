import fitz,sys,re
p=sys.argv[1]; a=int(sys.argv[2]); b=int(sys.argv[3]); lim=int(sys.argv[4]) if len(sys.argv)>4 else 80
d=fitz.open(p)
n=0
for i in range(a-1,b):
    ls=d[i].get_text().split("\n")
    print(f"--- p{i+1} ({len(ls)} lines)")
    for l in ls:
        print(repr(l)); n+=1
        if n>=lim: sys.exit()
