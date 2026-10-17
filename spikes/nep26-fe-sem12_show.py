import sys,re,importlib.util,fitz
s=importlib.util.spec_from_file_location("pr","spikes/nep26-fe-sem12_probe.py");pr=importlib.util.module_from_spec(s);s.loader.exec_module(pr)
d=fitz.open(pr.B+pr.PDFS[int(sys.argv[1])])
pn=int(sys.argv[2]);a=int(sys.argv[3]);b=int(sys.argv[4])
t=d[pn-1].get_text().split("\n")
print("page",pn,"nlines",len(t))
for k in range(a,min(b,len(t))+1): print(k,repr(t[k-1]))
