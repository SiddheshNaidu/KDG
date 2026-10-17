"""Throwaway: naive topic splitting + topic_validity census for nep26-sem56. Command: PYTHONIOENCODING=utf-8 python spikes/nep26-sem56_topics.py [--show CODE]"""
import re, sys, json, collections
sys.path.insert(0, "spikes")
import importlib
M = importlib.import_module("nep26-sem56_modules")
P = M.P
TV = importlib.import_module("topic_validity")
SM = re.compile(r"(?i)\bself[\s\-–]*(learning|study)\b")
def join(lines):
    out = ""
    for s in lines:
        s = s.strip()
        if not s: continue
        out = out + s if out.endswith("-") else (out + " " + s if out else s)
    return out
def content(r):
    ls = []
    for p, n, s in r["lines"]:
        if SM.search(s): break
        ls.append(s)
    return join(ls)
def split_topics(txt):
    t = re.sub(r"[•●▪]", ";", txt)
    t = re.sub(r"\b[IVX]+\.\d+\s", " ; ", t)          # I.1 style
    t = re.sub(r"(?<![\w.])\d+\.\d+\s", " ; ", t)       # 1.1 style
    t = re.sub(r"(?:(?<=\s)|^)\d{1,2}\.\s", " ; ", t)  # 1. style
    t = re.sub(r"(?:(?<=\s)|^)[a-z]\)\s", " ; ", t)    # a) style
    parts = re.split(r"[;:,]|\.\s|\.$| – | — ", t)
    return [x.strip(" .-") for x in parts if x.strip(" .-")]
def run():
    pages = P.load(); segs, first = P.segments(pages)
    cnt = collections.Counter(); total = 0; per = {}
    for c, s, e in segs:
        L = P.lines_of(pages, s, e)
        if not any(P.DS.match(l) for _, _, l in L): continue
        rows = M.parse(L)[0]
        tp = []
        for r in rows:
            tp += split_topics(content(r))
        v = collections.Counter()
        for t in tp:
            for rule in TV.validate(t): v[rule] += 1; cnt[rule] += 1
        per[c] = (len(tp), sum(v.values()), dict(v)); total += len(tp)
    return cnt, total, per
if __name__ == "__main__":
    if "--show" in sys.argv:
        code = sys.argv[sys.argv.index("--show") + 1]
        pages = P.load(); segs, first = P.segments(pages)
        for c, s, e in segs:
            if c != code: continue
            L = P.lines_of(pages, s, e)
            for r in M.parse(L)[0]:
                nm = []
                print("== module", r["num"], "hours", r["hours"], "tail", r["tail"]); print(content(r))
                sl = [x[2] for x in r["lines"]]
                i = next((k for k, x in enumerate(sl) if SM.search(x)), None)
                if i is not None: print("  SELF:", join(sl[i:]))
        sys.exit()
    cnt, total, per = run()
    lines = ["command: PYTHONIOENCODING=utf-8 python spikes/nep26-sem56_topics.py",
             "rules: spikes/topic_validity.py validate() (R1..R8, PROPOSED rules in docs/formats/topic_validity.md)",
             "topic extraction used (naive spike splitter, NOT a parser): module content = row lines before first self-learning line; lines joined (a line ending in '-' joins without space); numbering tokens (1.1, I.1, 1., a)) and bullets removed; split on ; : , '. ' ' – '",
             "population: the 21 courses with a module table (15 theory incl. IKS501, 6 labs with LO modules); 126 modules; labs without module table (9 courses) are NOT included (no module rows)",
             "total topics: %d" % total, "violations by rule id: %s" % dict(sorted(cnt.items())),
             "topics with >=1 violation (rule hits summed): %d" % sum(v[1] for v in per.values()),
             "per course (topics, rule hits, by rule):"]
    for c, (n, h, d) in per.items(): lines.append("  %s: %d topics, %d hits, %s" % (c, n, h, d))
    open("docs/evidence/regex_runs/nep26-sem56_topic_validity.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines[:8]))
