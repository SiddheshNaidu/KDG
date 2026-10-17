"""Spike: PRD self-check. Flags hedge words, counts evidence citations and UNKNOWNs per doc."""
import re, glob, pathlib
HEDGE = re.compile(r"\b(should work|probably|likely|presumably|i assume|assumed)\b", re.I)
docs = [pathlib.Path(p) for p in ["docs/PRD.md","docs/decisions.md","docs/requirements.md","docs/evaluation.md","docs/tasks.md","docs/glossary.md","CLAUDE.md"]+sorted(glob.glob("docs/formats/*.md"))]
print("file | evidence_refs | UNKNOWN | hedge_hits | lines")
for p in docs:
    if not p.exists(): print(p, "MISSING"); continue
    t = p.read_text(encoding="utf-8")
    ev = len(re.findall(r"docs/evidence/[\w./-]+|evidence/[\w./-]+\.(?:txt|csv)|\bmodel_v5_facts\.txt|\breference_code_facts\.txt|\bcensus\.csv|\bsignatures\.csv", t))
    print(f"{p} | {ev} | {len(re.findall(r'UNKNOWN', t))} | {len(HEDGE.findall(t))} | {t.count(chr(10))+1}")
    for m in HEDGE.finditer(t): print("   HEDGE:", t[max(0,m.start()-50):m.end()+30].replace("\n"," "))
