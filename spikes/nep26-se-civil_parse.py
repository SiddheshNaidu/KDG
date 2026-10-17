"""Throwaway spike for family nep26-se-civil (docs/formats/nep26-se-civil.md). Not product code."""
import fitz, re, sys, json
PDF = "data/raw/2019-scheme/Civil-Engineeing/6.23-N-B.E.-Civil-Engineeing-Sem-III-IV.pdf"
NOISE = [r"^Page \| \d+\s*$", r"^University of Mumbai\s*$", r"^Second Year Civil Engineering\s*$"]
CODE_LINE = re.compile(r"^(\d{7})\s*$")
MODHDR = re.compile(r"^(\d{1,2}) *\n((?:[^\n]*\n){1,3}?)(\d{1,2}) *\n((?:CO|LO)\d) *\n", re.M)
SUBITEM = re.compile(r"^(\d{1,2})\.(\d{1,2})(?:[ ]+(\S.*?))?[ ]*$")
SELFL = re.compile(r"^Self[- ]?learning [Tt]opics?\s*:", re.I)

def pages():
    d = fitz.open(PDF)
    return [[l for l in p.get_text().split("\n")] for p in d]

def clean(lines):
    return [l for l in lines if not any(re.match(n, l) for n in NOISE)]

def course_starts(P):
    """course start page = page>=16 with a 7-digit-alone line at index<25 preceded (within 4 lines) by 'Code' line or 'Course Code' and not repeated code"""
    res = []
    for i, L in enumerate(P):
        if i + 1 < 16: continue
        for j, l in enumerate(L[:25]):
            m = CODE_LINE.match(l)
            if m and any(re.match(r"^(Course )?Code\s*$|^Course Code\s*$", x) for x in L[max(0, j-16):j]):
                res.append((i + 1, m.group(1))); break
    return res

def courses(P):
    st = course_starts(P)
    out = []
    for k, (pg, code) in enumerate(st):
        end = st[k+1][0] - 1 if k + 1 < len(st) else len(P)
        out.append(dict(code=code, start=pg, end=end))
    return out

def title(P, c):
    L = P[c["start"]-1]
    j = [i for i, l in enumerate(L) if CODE_LINE.match(l)][0]
    t = []
    for l in L[j+1:j+6]:
        if re.match(r"^(\d+[*#]?(\+\d+)?|[-–—]+|\(.*)\s*$", l.strip()) : break
        t.append(l.strip())
    return " ".join(t)

if __name__ == "__main__":
    P = pages()
    for c in courses(P):
        c["title"] = title(P, c)
        print(c)


def body_lines(P, c):
    ls = []
    for pg in range(c["start"], c["end"] + 1):
        ls += [l.rstrip() for l in clean(P[pg-1])]
    return ls

# --- v2 regexes (names are used in docs/evidence/regex_runs/nep26-se-civil_*.txt) ---
RE_COURSEHDR = re.compile(r"^Course Module / Contents\s*$", re.M)
RE_COLHDR = re.compile(r"^Module[ ]*\nCourse Module / Contents[ ]*\n(?:Hours|Hrs)[ ]*\n(?:CO|LO)[ ]*\n(?:Mapping[ ]*\n|Mappi[ ]*\nng[ ]*\n)?", re.M)
RE_MODROW = re.compile(r"^(\d{1,2})[ ]*\n((?:[^\n]*\n){1,3}?)(\d{1,2})[ ]*\n((?:(?:CO|LO)\d+,?[ ]*\n)+)", re.M)
RE_STOP = re.compile(r"^(?:Text ?books?|Reference books?|References|Online (?:References|Resources)|Assessment|List of Experiments|List of Assignments|Term Work)\b", re.I | re.M)
RE_SUB = re.compile(r"^(\d{1,2})\.(\d{1,2})(?:[ ]+(\S.*?))?[ ]*$")
RE_SELF = re.compile(r"Self[\s-]*learning\s+topics?\s*:", re.I)

def module_section(lines):
    txt = "\n".join(l.rstrip() for l in lines) + "\n"
    h = RE_COLHDR.search(txt)
    if not h: return None
    txt = txt[h.start():]
    st = RE_STOP.search(txt)
    if st: txt = txt[:st.start()]
    return txt.lstrip("\n")

def parse_modules(lines):
    sec = module_section(lines)
    if sec is None: return None
    sec = RE_COLHDR.sub("", sec)
    sec = re.sub(r"^\s*Mapping\s*$", "", sec, flags=re.M) if False else sec
    ms = list(RE_MODROW.finditer(sec))
    mods = []
    for k, m in enumerate(ms):
        end = ms[k+1].start() if k + 1 < len(ms) else len(sec)
        mods.append(dict(num=int(m.group(1)),
                         name=" ".join(x.strip() for x in m.group(2).strip().split("\n")),
                         hours=m.group(3), co=" ".join(x.strip() for x in m.group(4).split("\n") if x.strip()),
                         body=sec[m.end():end].rstrip("\n").split("\n"), lead=sec[:ms[0].start()] if k == 0 else ""))
    return mods

def split_body(mod):
    """sub-items and self-learning text from a module body"""
    subs, cur, selfl, insl = [], None, [], False
    for l in mod["body"]:
        m = RE_SUB.match(l.strip())
        if m and int(m.group(1)) == mod["num"]:
            cur = [int(m.group(2)), [m.group(3) or ""]]; subs.append(cur); insl = False
            rest = m.group(3) or ""
            if RE_SELF.search(rest): pass
            continue
        if RE_SELF.search(l):
            insl = True; selfl.append(l.strip()); continue
        if insl: selfl.append(l.strip())
        elif cur is not None: cur[1].append(l.strip())
    return subs, selfl
