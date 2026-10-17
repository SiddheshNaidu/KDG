import fitz,re,sys
sys.stdout.reconfigure(encoding='utf-8')
from importlib import import_module
P={"M":"data/raw/2019-scheme/Mechanical-Engineering/6.35-N-B.E.-Mechanical-EngineeringSem-III-IV.pdf","A":"data/raw/2019-scheme/Mecanical-Automation-Engineering/6.44-N-B.E.-Mecanical-Automation-Engineering-Sem-III-IV.pdf"}
for k,p in P.items():
    d=fitz.open(p)
    for i,pg in enumerate(d):
        if i<14: continue
        L=[l.strip() for l in pg.get_text().split("\n")]
        # first page of course: contains 'Credits Assigned'
        if "Credits Assigned" in L:
            j=L.index("Total"); 
            print(k,i+1,L[j+1:j+5])
