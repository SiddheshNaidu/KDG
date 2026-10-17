"""Assemble module rows into Modules and split module content into Topic candidates.
Deterministic, offline. Everything dropped is returned in `dropped` so nothing disappears silently."""
from __future__ import annotations
import re
from .nep_tables import CourseTables

ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10}
NUM_RE = re.compile(r"^(?:0?\d{1,2}|[IVX]{1,4})\.?$")
SELF_RE = re.compile(r"(?<![A-Za-z])Self[\s\-]*(?:Learning|Study)(?![A-Za-z]).*", re.I | re.S)
PREREQ_RE = re.compile(r"^\s*Pre-?\s*requisites?(?![A-Za-z])", re.I)
LEADNUM_RE = re.compile(r"(?:(?<=\s)|^)\d{1,2}\.\s+(?=[A-Z])")
GENERIC_FRAG = {"introduction", "overview", "basics", "basic concepts", "concepts", "fundamentals", "applications", "application", "summary", "conclusion", "definition", "definitions", "terminology", "examples", "example", "types", "type", "history", "properties", "features", "classification", "need", "advantages", "disadvantages", "concept", "scope", "importance", "characteristics", "numericals", "numerical", "objectives", "objective", "problems", "applications of"}
LEAD_JUNK = re.compile(r"^(?:and|or|with|its|their|the|of|for|in|such as|like|e\.g\.?|i\.e\.?)\s+", re.I)
DROP_PAREN = re.compile(r"\((?:[^()]*(?:without proof|derivation|numericals?|numerical problems?|proof)[^()]*)\)", re.I)
TOTAL_RE = re.compile(r"Total\s+Hours?\s*:?\s*(\d{1,3})?.*$", re.I | re.S)
HOURS_RE = re.compile(r"^\s*(\d{1,2})(?![0-9])")
ENUM_SEP = re.compile(r"(?:(?<=\s)|^)(?:\(?[A-Za-z]\)|\(?[ivx]{1,4}\))\s+(?=[A-Za-z])")
JUNK_FRAG = re.compile(r"^(?:module|unit|chapter|total hours?|hours?|home exercise|exercise|assignment)\s*[:\-]?\s*\d*$", re.I)
BULLET_RE = re.compile(r"[•●▪‣·–—]")          # bullets; en/em dash used as list markers
SUBITEM_SEP = re.compile(r"(?:(?<=\s)|^)\d{1,2}\.\d{1,2}\.?\s*(?=[A-Za-z])")
DASH_SEP = re.compile(r"\s[-]\s")
PAREN_NOTE = re.compile(r"\((?:\s*(?:excluding|note|for details|any|refer|only|no numerical|numericals? excluded)[^()]*)\)", re.I)
LAST_NOTE = re.compile(r"(?<![A-Za-z])Note\s*:.*$", re.I | re.S)
TAIL_RE = re.compile(r"(?:Text\s*books?|Reference\s*books?|Textbooks?\s*:|Web\s+References?|Suggested\s+Reading|Course\s+Outcomes?).*$", re.I | re.S)
STOP_END = {"of", "and", "or", "the", "in", "with", "for", "to", "a", "an", "on", "by", "from", "using", "as", "at", "into", "between", "its", "their", "vs", "than", "such", "like", "e.g", "i.e", "etc"}
ABBREV = ("vs", "e.g", "i.e", "etc", "fig", "eq", "no", "dr", "cf", "viz", "approx", "sec")
SHORT_OK = {"of", "in", "to", "on", "or", "an", "as", "at", "by", "is", "it", "vs", "if", "no", "up", "do", "be", "so", "we", "me", "my", "go", "us", "id", "ml", "ai", "ip", "os", "db", "ui", "ux", "io", "rf", "ac", "dc", "pn", "bi", "ar", "vr", "ci", "cd"}

def _hours(s: str) -> int:
    m = HOURS_RE.match(s or "")
    return int(m.group(1)) if m else 0

def _num(s: str):
    s = s.strip().rstrip(".")
    if s.upper() in ROMAN:
        return ROMAN[s.upper()]
    return int(s) if s.isdigit() else None

def clean_name(name: str) -> str:
    n = re.sub(r"^\s*Module\s*\d+\s*[-:.]*\s*", "", name or "", flags=re.I)
    toks = n.split(); out = []
    for t in toks:
        if out and len(t) <= 2 and t.isalpha() and t.islower() and t.lower() not in SHORT_OK and len(out[-1]) >= 6 and out[-1][-1].isalpha():
            out[-1] += t        # rejoin a word wrapped mid-word in a narrow column ('Introductio'+'n', 'Electrodynami'+'cs')
        else:
            out.append(t)
    return " ".join(out).strip(" :.-")

def assemble_modules(ct: CourseTables):
    modules, prereq, skipped = [], [], []
    printed_total = None
    ct.prereq_hours = 0
    for r in ct.rows:
        for fld in ("name", "content", "hours", "co", "number"):
            v = getattr(r, fld)
            tm = TOTAL_RE.search(v)
            if tm:
                if tm.group(1): printed_total = int(tm.group(1))
                setattr(r, fld, v[:tm.start()].strip())
        n = r.number.strip()
        hdr = re.search(r"Sr|Module|No(?![A-Za-z])", n, re.I) and not NUM_RE.match(n)
        if hdr:
            skipped.append(("header_row", r.page)); continue
        text = (r.name + " " + r.content).strip() if ct.ncols < 5 else r.content
        if PREREQ_RE.match(r.name) or PREREQ_RE.match(r.content) or n in ("0", "00", "---", "--", "-", "–", "—"):
            prereq.append(r.content or r.name); ct.prereq_hours = getattr(ct, "prereq_hours", 0) + _hours(r.hours); continue
        if n and NUM_RE.match(n):
            m = dict(number=_num(n), label=n, name=r.name, content=r.content if ct.ncols >= 5 else text,
                     hours=0, co=r.co, pages=[r.page])
            m["hours"] = _hours(r.hours)
            modules.append(m)
        elif modules:
            m = modules[-1]
            add = (r.name + " " + r.content).strip() if ct.ncols < 5 else r.content
            if ct.ncols >= 5 and r.name and not m["name"]: m["name"] = r.name
            elif ct.ncols >= 5 and r.name and r.name not in m["name"]: m["name"] += " " + r.name
            m["content"] = (m["content"] + " " + add).strip()
            m["hours"] += _hours(r.hours)
            if r.co and r.co not in m["co"]: m["co"] = (m["co"] + " " + r.co).strip()
            if r.page not in m["pages"]: m["pages"].append(r.page)
        elif n or r.content:
            skipped.append(("orphan_row", r.page))
    ct.printed_total = printed_total
    return modules, prereq, skipped

def _split_outside(text: str, seps: str):
    out, buf, depth = [], [], 0
    for ch in text:
        if ch in "([": depth += 1
        elif ch in ")]": depth = max(0, depth - 1)
        if ch in seps and depth == 0:
            out.append("".join(buf)); buf = []
        else:
            buf.append(ch)
    out.append("".join(buf))
    return out

def _split_sentences(chunk: str):
    """split at '. ' / '.Capital' unless the dot belongs to an abbreviation."""
    parts, start = [], 0
    for m in re.finditer(r"(?<=[A-Za-z0-9\)])\.\s*(?=[A-Z])", chunk):
        before = chunk[start:m.start()].split()
        last = before[-1].lower().rstrip(".") if before else ""
        if last in ABBREV or re.fullmatch(r"[a-z]", last):
            continue
        parts.append(chunk[start:m.start()]); start = m.end()
    parts.append(chunk[start:])
    return parts

def split_topics(content: str, last_module: bool = False):
    """returns (topics, self_learning_text, dropped)"""
    dropped = []
    tm = TAIL_RE.search(content)
    if tm:
        dropped.append(("textbook_tail_cut", tm.group(0)[:60])); content = content[:tm.start()]
    if last_module:
        nm = LAST_NOTE.search(content)
        if nm:
            dropped.append(("exam_note_cut", nm.group(0)[:60])); content = content[:nm.start()]
    m = SELF_RE.search(content)
    self_txt = m.group(0).strip() if m else ""
    if m: content = content[:m.start()]
    content = DROP_PAREN.sub("", content); content = PAREN_NOTE.sub("", content)
    content = BULLET_RE.sub(";", content); content = ENUM_SEP.sub(";", content)
    content = SUBITEM_SEP.sub(";", content); content = LEADNUM_RE.sub(";", content)
    content = DASH_SEP.sub(";", content)
    parts = []
    for chunk in _split_outside(content, ";,:"):
        parts.extend(_split_sentences(chunk))
    topics = []
    for p in parts:
        t = re.sub(r"\s+", " ", p).strip(" .-–—\t")
        t = LEAD_JUNK.sub("", t).strip(" .-–—")
        t = t.strip("()[] ").strip() if t.count("(") != t.count(")") else t
        if not t or not re.search(r"[A-Za-z]{2}", t):
            if t: dropped.append(("no_letters", t))
            continue
        if re.fullmatch(r"(?:etc|and so on|others?)\.?", t, re.I):
            dropped.append(("filler", t)); continue
        if JUNK_FRAG.match(t):
            dropped.append(("junk_fragment", t)); continue
        if len(t) > 120:
            dropped.append(("overlong", t[:80])); continue
        if t.lower().strip(" .") in GENERIC_FRAG:
            dropped.append(("generic_fragment", t)); continue
        if len(t.split()) == 1 and len(t) < 4 and not t.isupper():
            dropped.append(("tiny_fragment", t)); continue
        ws = t.split()
        if ws[-1].lower().strip(".,") in STOP_END:
            dropped.append(("dangling_fragment", t)); continue
        if t[0].islower() and (len(ws) <= 2 or ws[0].lower() in STOP_END):
            dropped.append(("lowercase_fragment", t)); continue
        words = t.split()
        if len(words) > 10:
            halves = re.split(r"\s+and\s+", t)
            if len(halves) > 1 and all(len(h.split()) >= 3 for h in halves):
                topics.extend(h.strip(" .") for h in halves); continue
        topics.append(t)
    return topics, self_txt, dropped

def parse_course(ct: CourseTables, pdf: str, family: str = "") -> dict:
    modules, prereq, skipped = assemble_modules(ct)
    out_mods, all_dropped = [], list(skipped)
    for i, m in enumerate(modules):
        topics, self_txt, dropped = split_topics(m["content"], last_module=(i == len(modules) - 1))
        all_dropped += dropped
        co = m["co"]
        if re.search(r"CO\d.*\s\d{2,3}$", co):
            co = re.sub(r"\s*\d{2,3}$", "", co).strip()        # 'CO6 39' = CO6 + leaked total hours
        out_mods.append(dict(number=m["number"], label=m["label"], name=clean_name(m["name"]), hours=m["hours"], co=co,
                             pages=m["pages"], topics=topics, self_learning=self_txt, content_raw=m["content"]))
    return dict(course_code=ct.code, title=ct.title, family=family, source_pdf=pdf, header_page=ct.header_page,
                has_module_table=ct.has_module_table, unstitched=ct.unstitched, conflict_pages=ct.conflict_pages,
                orphan_tables=ct.orphan_tables, prerequisite=prereq, printed_total_hours=getattr(ct, "printed_total", None), prereq_hours=getattr(ct, "prereq_hours", 0),
                modules=out_mods, dropped=all_dropped)
