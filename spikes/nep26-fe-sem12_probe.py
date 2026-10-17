import fitz,sys,re
B="data/raw/2019-scheme/"
PDFS=["AIML/6.9N-AIML.pdf","CSE-AIML/6.14N-CSE-AIML.pdf","DS/6.28N-DS.pdf","EXTC/6.19-N-EXTC.pdf","Information-Technology/6.22-NIT.pdf","Mechanical-Engineering/6.23-NB.E.-Mechanical-Engineering-Sem-I-II-2.pdf"]
def lines(p):
    d=fitz.open(B+p)
    for i,pg in enumerate(d,1):
        for j,l in enumerate(pg.get_text().split("\n"),1): yield i,j,l
if __name__=="__main__":
    code=re.compile(r"^[A-Z]{2,5}\d{3}[A-Z]?$")
    for p in PDFS[:1]:
        for i,j,l in lines(p):
            if code.match(l.strip()): print(i,j,l)
