"""Compare the 6 PDFs: course-code sets and whole-course text equality (page-number lines and whitespace removed;
text range = from the course's first code line to the next course's first code line, so a neighbour's table header can leak in)."""
import importlib.util,re,hashlib,itertools
s=importlib.util.spec_from_file_location("ex","spikes/nep26-fe-sem12_extract.py");ex=importlib.util.module_from_spec(s);s.loader.exec_module(ex)
names=["AIML","CSE-AIML","DS","EXTC","IT","MECH"]
H={};T={}
for n,c in ex.all_courses():
    t=re.sub(r"\s+","","".join(l[2] for l in ex.clean(c)[1:]))
    T.setdefault(c["code"],{})[n]=t
    H.setdefault(c["code"],{})[n]=(c["page"],hashlib.md5(t.encode()).hexdigest()[:8])
lines=["command: cd /c/Users/Siddhesh/Documents/KDG && PYTHONIOENCODING=utf-8 python spikes/nep26-fe-sem12_pdfdiff.py > docs/evidence/regex_runs/nep26-fe-sem12_pdf_diff.txt",
       f"unique course codes (detail courses with objectives/outcomes/table): {len(H)}; course occurrences: {sum(len(v) for v in H.values())}"]
sets={n:{c for c,v in H.items() if n in v} for n in range(6)}
for n in range(6): lines.append(f"{names[n]}: {len(sets[n])} courses; codes not in AIML: {sorted(sets[n]-sets[0])}; AIML codes absent here: {sorted(sets[0]-sets[n])}")
lines.append("pairwise: number of shared codes whose course text is byte-identical after whitespace removal / shared codes")
for a,b in itertools.combinations(range(6),2):
    sh=[c for c in H if a in H[c] and b in H[c]]; same=[c for c in sh if T[c][a]==T[c][b]]
    lines.append(f"{names[a]} vs {names[b]}: {len(same)}/{len(sh)} identical; differing: {sorted(set(sh)-set(same))}")
open("docs/evidence/regex_runs/nep26-fe-sem12_pdf_diff.txt","w",encoding="utf-8").write("\n".join(lines)+"\n")
print("\n".join(lines))
