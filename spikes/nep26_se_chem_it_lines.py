import fitz,sys
def lines(pdf):
    d=fitz.open(pdf)
    for i,p in enumerate(d,1):
        for j,l in enumerate(p.get_text().split("\n")):
            yield i,j,l
PDFS={"a":"data/raw/2019-scheme/Chemical-Engineering/6.40-N-Chemical-Engineering-Sem-III-IV.pdf","b":"data/raw/2019-scheme/Information-Technology/6.34-N-B.E.-Information-Technology-Sem-III-IV.pdf"}
if __name__=="__main__":
    k=sys.argv[1]; pg=int(sys.argv[2]); n=int(sys.argv[3]) if len(sys.argv)>3 else 70
    c=0
    for i,j,l in lines(PDFS[k]):
        if i==pg:
            print(j,repr(l)); c+=1
            if c>=n: break
