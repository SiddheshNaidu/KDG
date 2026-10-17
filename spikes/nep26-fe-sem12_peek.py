import importlib.util,sys
s=importlib.util.spec_from_file_location("ex","spikes/nep26-fe-sem12_extract.py");ex=importlib.util.module_from_spec(s);s.loader.exec_module(ex)
n=int(sys.argv[1]);code=sys.argv[2];pat=sys.argv[3];off=int(sys.argv[4]);cnt=int(sys.argv[5])
import re
L,cs=ex.sg.segment_pdf(n)
c=[x for x in cs if x["code"]==code][0]; t=ex.clean(c)
k=[i for i,x in enumerate(t) if re.search(pat,x[2])]
print("matches",len(k)); k=k[0]
for x in t[max(0,k+off):k+off+cnt]: print(f"p{x[0]}:{x[1]}",repr(x[2][:85]))
