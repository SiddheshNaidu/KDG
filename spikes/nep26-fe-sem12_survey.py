import sys,re,importlib.util
s=importlib.util.spec_from_file_location("pr","spikes/nep26-fe-sem12_probe.py");pr=importlib.util.module_from_spec(s);s.loader.exec_module(pr)
H=re.compile(r"^\s*([A-Z]{2,5}\d{3}[A-Z]?)\s+(\S.*?)\s*$")
for p in pr.PDFS[:int(sys.argv[1])]:
    print("##",p)
    for i,j,l in pr.lines(p):
        m=H.match(l)
        if m and i>12: print(i,j,repr(l))
