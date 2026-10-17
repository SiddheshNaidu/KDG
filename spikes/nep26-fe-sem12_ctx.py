import importlib.util,re,sys
s=importlib.util.spec_from_file_location("sg","spikes/nep26-fe-sem12_seg.py");sg=importlib.util.module_from_spec(s);s.loader.exec_module(sg)
n=int(sys.argv[1]);code=sys.argv[2];pat=sys.argv[3];ctx=int(sys.argv[4]);mx=int(sys.argv[5]) if len(sys.argv)>5 else 40
L,cs=sg.segment_pdf(n)
c=[x for x in cs if x["code"]==code][0]
t=c["lines"];shown=0;last=-99
for k,(i,j,l) in enumerate(t):
    if re.search(pat,l):
        for q in range(max(last+1,k-ctx),min(len(t),k+ctx+1)):
            print(f"p{t[q][0]}:{t[q][1]}",repr(t[q][2][:90])); shown+=1
        last=k+ctx; print("--")
        if shown>mx: break
