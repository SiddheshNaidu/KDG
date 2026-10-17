import fitz,sys
sys.stdout.reconfigure(encoding='utf-8')
pdf=sys.argv[1]; pg=int(sys.argv[2]); n=int(sys.argv[3]) if len(sys.argv)>3 else 60
d=fitz.open(pdf)
if pg<0: print(len(d)); sys.exit()
for i,l in enumerate(d[pg-1].get_text().split("\n")[:n]): print(i,repr(l))
