import fitz,re,sys
sys.stdout.reconfigure(encoding='utf-8')
P={"M":"data/raw/2019-scheme/Mechanical-Engineering/6.35-N-B.E.-Mechanical-EngineeringSem-III-IV.pdf","A":"data/raw/2019-scheme/Mecanical-Automation-Engineering/6.44-N-B.E.-Mecanical-Automation-Engineering-Sem-III-IV.pdf"}
if __name__=="__main__":
  for k,p in P.items():
    d=fitz.open(p)
    for i,pg in enumerate(d):
        L=pg.get_text().split("\n")
        codes=[l for l in L if re.fullmatch(r"\d{7}|[A-Z]{2,}\d{3,}",l.strip())]
        det=[l for l in L if re.search(r"detailed",l,re.I)]
        if codes or det: print(k,i+1,len(L),codes[:3],det[:2])
