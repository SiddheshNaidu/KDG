"""Spike: run each regex over EVERY course (34) of family nep26-se-mech; writes docs/evidence/regex_runs/nep26-se-mech_<name>.txt
Command: PYTHONIOENCODING=utf-8 python spikes/nep26-se-mech_regex.py"""
import re, sys, json, pathlib
sys.path.insert(0, "spikes")
from importlib import util
def _imp(name, path):
    s = util.spec_from_file_location(name, path); m = util.module_from_spec(s); s.loader.exec_module(m); return m
lib = _imp("lib", "spikes/nep26-se-mech_lib.py")
OUT = pathlib.Path("docs/evidence/regex_runs"); OUT.mkdir(parents=True, exist_ok=True)
FAM = "nep26-se-mech"
CMD = "PYTHONIOENCODING=utf-8 python spikes/nep26-se-mech_regex.py"
courses = lib.load_courses()
T = len(courses)
def tag(c):
    code, p = lib.first_code(c); return f"{c['sub']}:{code}"
def where(c, idx):
    p, l = c["lines"][idx]; return f"{pathlib.Path(c['pdf']).name} p{p}"

STOP = r"^(?:Text ?Books?:?|Reference Books|References:?|Total Hours.*|Online (?:References|Resources):?|Links:|Assessment\s*:?|List of Experiments\.?|Part \(B\))\s*$"
START = {
 1: r"^(?:Module\s+)?Detailed Contents?\s*$|^DETAIL(?:ED)? SYLLABUS|^Sr\.\s*$",
 2: r"^(?:Module\s+)?Detailed Contents?\s*$|^DETAIL(?:ED)? SYLLABUS|^Sr\.\s*$|^Part \(A\)\s*$",
}
def region(c, sa=2):
    L = c["lines"]; s = None
    for i, (p, l) in enumerate(L):
        if re.search(START[sa], l): s = i; break
    if s is None: return None
    e = len(L)
    for i in range(s + 1, len(L)):
        if re.search(STOP, L[i][1]): e = i; break
    return s, e
ROM = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6}
TAIL_RX = r"^(?:C[O0]|LO|L)\s?\d"
# marker styles: name -> (regex, group->number fn, needs-next-line check)
def _mk_roman(strict):
    rx = r"^(I|II|III|IV|V|VI)\s*$" if strict else r"^(I|II|III|IV|V|VI)(?:\s*$|\s+[A-Z][A-Za-z])"
    return lambda L, i, e: (ROM[re.match(rx, L[i][1]).group(1)] if re.match(rx, L[i][1]) else None)
def _mk_dotted(L, i, e):
    m = re.match(r"^([1-9])\.\s*$", L[i][1]); return int(m.group(1)) if m else None
def _mk_zero(L, i, e):
    m = re.match(r"^0([1-9])\s*$", L[i][1])
    return int(m.group(1)) if m and i + 1 < e and re.match(r"^Module\s*:", L[i + 1][1]) else None
def _mk_bare(L, i, e):
    m = re.match(r"^([1-9]|10)\s*$", L[i][1])
    if m and i + 1 < e and re.match(r"^[A-Za-z]", L[i + 1][1]) and not re.match(TAIL_RX, L[i + 1][1]) and not re.match(r"^(?:I|II|III|IV|V|VI)\s*$", L[i + 1][1]):
        return int(m.group(1))
    return None
def styles(attempt):
    if attempt == 1: return {"roman": _mk_roman(True), "dotted": _mk_dotted, "zero_module": _mk_zero, "bare": _mk_bare}
    return {"roman": _mk_roman(False), "dotted": _mk_dotted, "zero_module": _mk_zero, "bare": _mk_bare}
def consecutive_markers(c, reg, attempt=2):
    """returns (style, [(line_idx, n)]) for the style with the most consecutive 1,2,3.. markers (ties: dict order)"""
    s, e = reg; L = c["lines"]; best = ("none", [])
    for name, fn in styles(attempt).items():
        seq = []; want = 1
        for i in range(s + 1, e):
            n = fn(L, i, e)
            if n == want: seq.append((i, n)); want += 1
        if len(seq) > len(best[1]): best = (name, seq)
    return best

def write(name, attempts, note=""):
    p = OUT / f"{FAM}_{name}.txt"
    with open(p, "w", encoding="utf-8") as f:
        f.write(f"command: {CMD}\nfamily: {FAM} (courses=34: sub-family a=17 from 6.35 PDF, b=17 from 6.44 PDF)\nregex name: {name}\n{note}\n")
        for lab, rx, m, t, fails in attempts:
            f.write(f"\n--- {lab}\nregex/predicate: {rx}\nmatched/total: {m}/{t}\nfailures ({len(fails)}):\n")
            for x in fails: f.write("  " + x + "\n")
    last = attempts[-1]; print(f"{name:16s} final {last[2]}/{last[3]}  attempts={len(attempts)}")
    return last

summary = {}
# 1. course_code
rx = r"^\s*(\d{7})\s*$"
f = []; m = 0
for c in courses:
    code, p = lib.first_code(c)
    if code is not None and p == c["start"]: m += 1
    else: f.append(f"{tag(c)} start p{c['start']} first code on p{p}")
summary["course_code"] = write("course_code", [("attempt 1", rx + "  (first match must be on the course-start page)", m, T, f)])

# 2. title
TERM = r"^\s*(?:\d{1,2}\*?(?:\+\d)?|-{1,2})\s*$"
def title_of(c):
    L = c["lines"]
    for i, (p, l) in enumerate(L):
        if re.match(lib.CODE_RX, l):
            out = []
            for j in range(i + 1, min(i + 6, len(L))):
                if re.match(TERM, L[j][1]): return " ".join(out), j - i - 1
                out.append(L[j][1])
            return None, None
    return None, None
f = []; m = 0; titles = {}
for c in courses:
    t, n = title_of(c); titles[tag(c)] = t
    if t and 1 <= n <= 3: m += 1
    else: f.append(f"{tag(c)} title={t!r} lines={n}")
summary["title"] = write("title", [("attempt 1", TERM + "  (title = lines between first 7-digit code line and first line matching this; 1-3 lines)", m, T, f)], note="titles: " + json.dumps(titles, ensure_ascii=False))

# 3. region start / stop
res = []
for a in (1, 2):
    f = []; m = 0
    for c in courses:
        if region(c, a): m += 1
        else: f.append(f"{tag(c)} pages {c['start']}-{c['end']-1}: no line matches START[{a}]")
    res.append((f"attempt {a}", START[a], m, T, f))
summary["region_start"] = write("region_start", res)
f = []; m = 0
for c in courses:
    r = region(c)
    if r and r[1] < len(c["lines"]): m += 1
    else: f.append(f"{tag(c)} region={r} (no stop marker before end of course pages)")
summary["region_stop"] = write("region_stop", [("attempt 1 (region start = START[2])", STOP, m, T, f)])

# 4. module_marker (3 attempts), experiment_marker
RXDESC = {1: r"roman ^(I|II|III|IV|V|VI)\s*$ | dotted ^[1-9]\.\s*$ | zero_module ^0[1-9]\s*$ (next line ^Module\s*:) | bare ^([1-9]|10)\s*$ (next line starts with a letter, not a CO/LO tail, not a roman numeral)",
          2: r"as attempt 1 but roman also allows a title on the same line: ^(I|II|III|IV|V|VI)(?:\s*$|\s+[A-Z][A-Za-z])"}
res = []; mm = {}
for a in (1, 2):
    f = []; m = 0; counts = {}
    for c in courses:
        r = region(c)
        if not r: f.append(f"{tag(c)} no region (no START match)"); counts[tag(c)] = None; continue
        st, seq = consecutive_markers(c, r, a); counts[tag(c)] = (st, len(seq))
        if len(seq) >= 6: m += 1
        else: f.append(f"{tag(c)} best style={st} consecutive markers found={[n for _, n in seq]} region {where(c, r[0])} lines {r[0]}-{r[1]}")
    res.append((f"attempt {a}", RXDESC[a] + "; predicate: >=6 consecutive markers 1..N", m, T, f)); mm = counts
summary["module_marker"] = write("module_marker", res, note="final attempt (style,count) per course: " + json.dumps(mm))
# experiment_marker: only courses that contain an experiment-table heading
EXH = r"^(?:Part \(A\)|A\. List of Experiments.*|List of Experiments\.?|Expt\.)\s*$|^Sr No$"
EXM = r"^(0[1-9]|1\d|[1-9]\.?)\s*$"
res = []
for att, nxt in ((1, r"^[A-Za-z]"), (2, r"^[A-Za-z(]"), (3, r"^(?!\d{1,2}\.?\s*$)\S")):
    f = []; m = 0; tot = 0; ec = {}
    for c in courses:
        L = c["lines"]; h = [i for i, (p, l) in enumerate(L) if re.search(r"^(?:Part \(A\)|A\. List of Experiments.*|List of Experiments\.?|Expt\.)\s*$", l)]
        if not h: continue
        tot += 1; i0 = h[0]; seq = []; want = 1
        for i in range(i0 + 1, len(L)):
            if re.match(r"^Part \(B\)|^Sr No\s*$|^Assessment|^Group C|^Text|^Reference", L[i][1]) and seq: break
            mm_ = re.match(EXM, L[i][1])
            if mm_ and int(mm_.group(1).rstrip(".")) == want and i + 1 < len(L) and re.match(nxt, L[i + 1][1]): seq.append(i); want += 1
        ec[tag(c)] = len(seq)
        if len(seq) >= 1: m += 1
        else: f.append(f"{tag(c)} {where(c, i0)}: heading {L[i0][1]!r} found, 0 consecutive experiment markers")
    res.append((f"attempt {att}", EXH + "  then markers " + EXM + " (consecutive from 1, next line must match " + nxt + "); unit = courses having an experiment heading", m, tot, f))
summary["experiment_marker"] = write("experiment_marker", res, note="final attempt experiments per course: " + json.dumps(ec))

# 5. hours_tail / co_tail
HR = r"^\d{1,2}\.?\s*$|^-\s*$"
CO = {1: r"^(?:C[O0]|LO|L)\s?[1-9]\b",
      2: r"^(?:C[O0]|LO|L)\s?[1-9]\b|^L\d(?:,\s*L?\d)*,?\s*$"}
def tails(c, reg, rxx, bare_after_hours=False):
    s, e = reg; L = c["lines"]; mk = {i for i, _ in consecutive_markers(c, reg)[1]}; n = 0
    for i in range(s + 1, e):
        if i in mk: continue
        if re.search(rxx, L[i][1]): n += 1
        elif bare_after_hours and re.match(r"^[1-9]$", L[i][1]) and i > 0 and re.match(r"^0\d$", L[i - 1][1]): n += 1
    return n
f = []; m = 0; cnt = {}
for c in courses:
    r = region(c)
    if not r: f.append(f"{tag(c)} no region"); continue
    mk = consecutive_markers(c, r)[1]; n = tails(c, r, HR); cnt[tag(c)] = (len(mk), n)
    if mk and n >= len(mk): m += 1
    else: f.append(f"{tag(c)} markers={len(mk)} hours-like lines={n}")
summary["hours_tail"] = write("hours_tail", [("attempt 1", HR + "  (excluding marker lines of the chosen style); predicate: hours-like lines >= modules", m, T, f)], note="(markers,hours) per course: " + json.dumps(cnt))
res = []
for a, (rxx, bare) in {1: (CO[1], False), 2: (CO[2], False), 3: (CO[2], True)}.items():
    f = []; m = 0
    for c in courses:
        r = region(c)
        if not r: f.append(f"{tag(c)} no region"); continue
        mk = consecutive_markers(c, r)[1]; n = tails(c, r, rxx, bare)
        if mk and n >= len(mk): m += 1
        else:
            sample = [c["lines"][i][1] for i in range(r[0], r[1]) if re.match(r"^(?:CO|LO|L|C0)", c["lines"][i][1])][:3]
            f.append(f"{tag(c)} markers={len(mk)} co-like lines={n} sample={sample}")
    res.append((f"attempt {a}", rxx + ("  OR bare digit ^[1-9]$ directly after a ^0\d$ line" if bare else "") + "; predicate: co/lo-like lines >= modules", m, T, f))
summary["co_tail"] = write("co_tail", res)


# 6. self-learning
BROAD = r"(?i)self[\s\-]*(?:learning|study)"
STRICT = r"^Self[- ]learning [Tt]opics?\s*:?"
bl = []; sl = []
for c in courses:
    for i, (p, l) in enumerate(c["lines"]):
        if re.search(BROAD, l):
            bl.append((c, i, l))
            if re.search(STRICT, l): sl.append((c, i, l))
f = [f"{tag(c)} {where(c, i)}: {l!r}" for c, i, l in bl if not re.search(STRICT, l)]
spell = {}
for c, i, l in bl:
    k = re.search(BROAD, l).group(0); spell[k] = spell.get(k, 0) + 1
summary["self_learning"] = write("self_learning", [("attempt 1 (line level: strict-matched lines / broad-matched lines)", STRICT + f"   (broad detector: {BROAD})", len(sl), len(bl), f)], note="broad spellings (line level): " + json.dumps(spell) + "\ncourses with a strict marker: " + str(sorted({tag(c) for c, i, l in sl})))

# 7. total_hours
TH = r"^Total Hours?\b"
f = []; m = 0
for c in courses:
    if any(re.search(TH, l) for p, l in c["lines"]): m += 1
    else: f.append(f"{tag(c)} pages {c['start']}-{c['end']-1}: no 'Total Hours' line")
summary["total_hours"] = write("total_hours", [("attempt 1", TH, m, T, f)])

# 8. NEP banner (PDF level)
import fitz
NB = r"As Per NEP 2020"
f = []; m = 0
for sub, path in lib.PDFS.items():
    d = fitz.open(path); hit = [i + 1 for i in range(6) if re.search(NB, d[i].get_text(), re.I)]
    if hit: m += 1
    else: f.append(f"{path} pages 1-6: no match")
summary["nep_banner"] = write("nep_banner", [("attempt 1", NB + " (re.I, pages 1-6)", m, 2, f)], note="unit = PDF")
json.dump({k: v[2:4] for k, v in summary.items()}, open("spikes/nep26-se-mech_summary.json", "w"))
