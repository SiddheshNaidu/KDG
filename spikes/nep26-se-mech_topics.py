"""Spike: topic validity census for family nep26-se-mech.
(1) NAIVE census: every course with a module region is cut into modules (marker styles from nep26-se-mech_regex.py), tail lines
    (hours / CO / LO) are dropped, 'Module:' and 'Self-learning Topics:' prefixes removed, URLs removed, text split on , . bullets and 'N.N ' numbering
    (numbering prefix is NOT stripped, so R6 shows what a parser must strip). This measures the rules on a naive splitter, NOT parser quality.
(2) GOLDEN census: validate() over tests/golden/nep26-se-mech/*.json topics.
Command: PYTHONIOENCODING=utf-8 python spikes/nep26-se-mech_topics.py"""
import re, sys, json, io, glob, pathlib, contextlib
sys.path.insert(0, "spikes")
from importlib import util
def _imp(name, path):
    s = util.spec_from_file_location(name, path); m = util.module_from_spec(s); s.loader.exec_module(m); return m
with contextlib.redirect_stdout(io.StringIO()):
    rg = _imp("rg", "spikes/nep26-se-mech_regex.py")      # re-runs regex spike (idempotent) to reuse region()/markers
tv = _imp("tv", "spikes/topic_validity.py")
TAIL = re.compile(r"^(?:\d{1,2}\.?|-|(?:C[O0]|LO|L)\s?\d.*|CO|LO|Mapp|ing)\s*$")
def modules_of(c):
    r = rg.region(c)
    if not r: return None
    st, seq = rg.consecutive_markers(c, r)
    if not seq: return None
    L = c["lines"]; idx = [i for i, _ in seq] + [r[1]]; mods = []
    for k in range(len(seq)):
        body = []
        for i in range(idx[k] + 1, idx[k + 1]):
            l = L[i][1]
            if TAIL.match(l): continue
            body.append(l)
        mods.append(" ".join(body))
    return mods
def split_topics(text):
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"^Module\s*:\s*", "", text)
    text = re.sub(r"Self[- ]learning [Tt]opics?\s*:?", ", ", text)
    parts = re.split(r"[,•●]|(?<![0-9A-Z])\.(?=\s|$)|\s(?=\d\.\d+\.?\s)", text)
    return [p.strip() for p in parts if re.search(r"\S", p)]
counts = {}; total = 0; ncourses = 0; per_course = {}; examples = {}
for c in rg.courses:
    mods = modules_of(c)
    if mods is None: per_course[rg.tag(c)] = None; continue
    ncourses += 1; n = 0; bad = 0
    for mtxt in mods:
        for t in split_topics(mtxt):
            n += 1; v = tv.validate(t)
            if v: bad += 1
            for r_ in v:
                counts[r_] = counts.get(r_, 0) + 1; examples.setdefault(r_, [])
                if len(examples[r_]) < 3: examples[r_].append(f"{rg.tag(c)}: {t[:90]!r}")
    total += n; per_course[rg.tag(c)] = (n, bad)
with open("docs/evidence/regex_runs/nep26-se-mech_topic_validity.txt", "w", encoding="utf-8") as f:
    f.write("command: PYTHONIOENCODING=utf-8 python spikes/nep26-se-mech_topics.py\nrules: docs/formats/topic_validity.md via spikes/topic_validity.py validate()\n")
    f.write(f"\n== (1) NAIVE splitter census over {ncourses} courses with a detected module region (of 34)\n")
    f.write(f"total candidate topics: {total}\nviolating at least one rule: {sum(b for v in per_course.values() if v for _, b in [v])}\n")
    for r_ in sorted(counts): f.write(f"  {r_}: {counts[r_]}\n    e.g. " + "\n    e.g. ".join(examples[r_]) + "\n")
    f.write("per course (topics, topics-with-violation): " + json.dumps(per_course) + "\n")
    f.write("\n== (2) GOLDEN census (hand-drafted topics, DRAFT)\n")
    gt = 0; gc = {}
    for p in sorted(glob.glob("tests/golden/nep26-se-mech/*.json")):
        g = json.load(open(p, encoding="utf-8")); n = 0
        for m in g["modules"]:
            for t in m["topics"]:
                n += 1; v = tv.validate(t)
                for r_ in v: gc[r_] = gc.get(r_, 0) + 1; f.write(f"  VIOLATION {pathlib.Path(p).name} module {m['number']}: {t!r} -> {v}\n")
        gt += n; f.write(f"  {pathlib.Path(p).name}: {n} topics\n")
    f.write(f"golden total topics: {gt}\ngolden violations by rule: {json.dumps(gc)}\n")
print(f"naive: {total} topics over {ncourses} courses; violations {counts}")
