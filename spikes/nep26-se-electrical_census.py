"""Spike: topic-validity census for nep26-se-electrical.
Part A: validate() over the 5 DRAFT golden courses' topics.
Part B: validate() over NAIVE candidates split from module content (x0>=150 column) of all 16 module-table courses x 2 PDFs
        (naive split: on ',', ';', '.', ' - ', en dash, 'N]' markers; headings before ':' left attached). Part B measures how far naive splitting is from valid topics."""
import re, json, glob, collections, importlib, sys, os
sys.path.insert(0, "spikes")
from topic_validity import validate
x = importlib.import_module("nep26-se-electrical_extract")
FAM = "nep26-se-electrical"
out = []
def census(topics):
    c = collections.Counter(); bad = 0
    for t in topics:
        v = validate(t)
        if v: bad += 1
        for r in v: c[r] += 1
    return c, bad
def fmt(title, topics, show=0):
    c, bad = census(topics)
    out.append(f"{title}: total topics={len(topics)} topics_with_any_violation={bad}")
    for r in sorted(c): out.append(f"  {r}: {c[r]}")
    if not c: out.append("  (no violations)")
    return c
# Part A
out.append(f"command: PYTHONIOENCODING=utf-8 python spikes/{FAM}_census.py\nscript: spikes/{FAM}_census.py ; rules: spikes/topic_validity.py validate()\n")
allA = []
for fn in sorted(glob.glob(f"tests/golden/{FAM}/*.json")):
    d = json.load(open(fn, encoding="utf-8"))
    tp = [t for m in d["modules"] for t in m["topics"]]
    allA += tp
    fmt(f"A golden {d['course_code']}", tp)
out.append("")
fmt("A TOTAL golden (5 courses)", allA)
# Part B
def split(content):
    s = re.sub(r"\b\d\]", ",", content)
    parts = re.split(r"\s*[,;]\s*|(?<=[a-z\)])\.\s+|\s+[-–]\s+|\s*–\s*", s)
    return [p.strip(" .") for p in parts if p.strip(" .")]
B = []; per = {}
for k, p in x.seg.PDFS.items():
    for c in x.extract(p):
        if c["kind"] != "theory" and not c["code"].endswith("4411"): continue
        ms = x.modules(c)
        tp = [t for m in ms for t in split(m["content"])]
        per[(k, c["code"])] = len(tp)
        B += tp
out.append("")
fmt("B naive-split candidates, all 16 module-table courses x 2 PDFs (32 course instances)", B)
out.append("  per-course candidate counts: " + str(per))
os.makedirs("docs/evidence/regex_runs", exist_ok=True)
open(f"docs/evidence/regex_runs/{FAM}_topic_validity.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
