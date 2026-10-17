import fitz,sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0,'spikes')
from importlib import util
s=util.spec_from_file_location('scan','spikes/nep26-se-mech_scan.py'); m=util.module_from_spec(s); s.loader.exec_module(m)
k=sys.argv[1]; d=fitz.open(m.P[k]); w=int(sys.argv[3]) if len(sys.argv)>3 else 70
for pn in sys.argv[2].split(","):
    L=[l.strip() for l in d[int(pn)-1].get_text().split("\n")]
    print("=== p",pn); print(" | ".join(l[:w] for l in L if l))
