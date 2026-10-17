"""Assemble module rows into Modules and split module content into Topic candidates.
Deterministic, offline. Everything dropped is returned in `dropped` so nothing disappears silently."""
from __future__ import annotations
import re
from .nep_tables import CourseTables

ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10}
NUM_RE = re.compile(r"^(?:0?\d{1,2}|[IVX]{1,4})\.?$")
SELF_RE = re.compile(r"\bSelf[\s\-]*(?:Learning|Study)\b.*", re.I | re.S)
PREREQ_RE = re.compile(r"^\s*Pre-?\s*requisites?\b", re.I)
SUBNUM_RE = re.compile(r"(?:(?<=\s)|^)\d{1,2}\.\d{1,2}\.?(?=\s)")
LEADNUM_RE = re.compile(r"(?:(?<=\s)|^)\d{1,2}\.\s+(?=[A-Z])")
GENERIC_FRAG = {"introduction", "overview", "basics", "basic concepts", "concepts", "fundamentals", "applications", "application", "summary", "conclusion", "definition", "definitions", "terminology", "examples", "example", "types", "type", "history", "properties", "features", "classification", "need", "advantages", "disadvantages", "concept", "scope", "importance", "characteristics"}
LEAD_JUNK = re.compile(r"^(?:and|or|with|its|their|the|of|for|in)\s+", re.I)
DROP_PAREN = re.compile(r"\((?:[^()]*(?:without proof|derivation|numericals?|numerical problems?|proof)[^()]*)\)", re.I)

def _num(s: str):
    s = s.strip().rstrip(".")
    if s.upper() in ROMAN:
        return ROMAN[s.upper()]
    return int(s) if s.isdigit() else None

def assemble_modules(ct: CourseTables):
    modules, prereq, skipped = [], [], []
    for r in ct.rows:
        n = r.number.strip()
        hdr = re.search(r"Sr|Module|No\b", n, re.I) and not NUM_RE.match(n)
        if hdr:
            skipped.append(("header_row", r.page)); continue
        text = (r.name + " " + r.content).strip() if ct.ncols < 5 else r.content
        if PREREQ_RE.match(r.name) or PREREQ_RE.match(r.content) or n in ("0", "00", "---", "--", "-", "–", "—"):
            prereq.append(r.content or r.name); continue
        if n and NUM_RE.match(n):
            m = dict(number=_num(n), label=n, name=r.name, content=r.content if ct.ncols >= 5 else text,
                     hours=0, co=r.co, pages=[r.page])
            if r.hours.isdigit(): m["hours"] = int(r.hours)
            modules.append(m)
        elif modules:
            m = modules[-1]
            add = (r.name + " " + r.content).strip() if ct.ncols < 5 else r.content
            if ct.ncols >= 5 and r.name and not m["name"]: m["name"] = r.name
            elif ct.ncols >= 5 and r.name and r.name not in m["name"]: m["name"] += " " + r.name
            m["content"] = (m["content"] + " " + add).strip()
            if r.hours.isdigit(): m["hours"] += int(r.hours)
            if r.co and r.co not in m["co"]: m["co"] = (m["co"] + " " + r.co).strip()
            if r.page not in m["pages"]: m["pages"].append(r.page)
        elif n or r.content:
            skipped.append(("orphan_row", r.page))
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

BULLET_RE = re.compile(r"[•●▪‣·]")
SUBITEM_SEP = re.compile(r"(?:(?<=\s)|^)\d{1,2}\.\d{1,2}\.?\s*(?=[A-Za-z])")
NOTE_RE = re.compile(r"\((?:\s*(?:excluding|note|for details|any|refer|only|no numerical|numericals? excluded)[^()]*)\)|(?<![A-Za-z])Note\s*:.*$", re.I)

TAIL_RE = re.compile(r"(?:Text\s*books?|Reference\s*books?|Textbooks?\s*:|Web\s+References?|Suggested\s+Reading).*$", re.I | re.S)

def split_topics(content: str):
    """returns (topics, self_learning_text, dropped)"""
    dropped = []
    tm = TAIL_RE.search(content)
    if tm:
        dropped.append(("textbook_tail_cut", tm.group(0)[:60])); content = content[:tm.start()]
    m = SELF_RE.search(content)
    self_txt = m.group(0).strip() if m else ""
    if m: content = content[:m.start()]
    content = DROP_PAREN.sub("", content); content = NOTE_RE.sub("", content)
    content = BULLET_RE.sub(";", content)
    content = SUBITEM_SEP.sub(";", content); content = LEADNUM_RE.sub(";", content)
    parts = []
    for chunk in _split_outside(content, ";,:"):
        for sub in re.split(r"(?<=[a-z\)])\.\s+(?=[A-Z])", chunk):
            parts.append(sub)
    topics = []
    for p in parts:
        t = re.sub(r"\s+", " ", p).strip(" .-–—\t")
        t = LEAD_JUNK.sub("", t).strip(" .-–—")
        if not t or not re.search(r"[A-Za-z]{2}", t):
            if t: dropped.append(("no_letters", t))
            continue
        if re.fullmatch(r"(?:etc|and so on|others?)\.?", t, re.I):
            dropped.append(("filler", t)); continue
        if len(t) > 120:
            dropped.append(("overlong", t[:80])); continue
        if t.lower().strip(" .") in GENERIC_FRAG:
            dropped.append(("generic_fragment", t)); continue
        words = t.split()
        if len(words) > 8:
            halves = re.split(r"\s+and\s+", t)
            if len(halves) > 1 and all(len(h.split()) >= 2 for h in halves):
                topics.extend(h.strip(" .") for h in halves); continue
        topics.append(t)
    return topics, self_txt, dropped

def parse_course(ct: CourseTables, pdf: str, family: str = "") -> dict:
    modules, prereq, skipped = assemble_modules(ct)
    out_mods, all_dropped = [], list(skipped)
    for m in modules:
        topics, self_txt, dropped = split_topics(m["content"])
        all_dropped += dropped
        out_mods.append(dict(number=m["number"], label=m["label"], name=m["name"], hours=m["hours"], co=m["co"],
                             pages=m["pages"], topics=topics, self_learning=self_txt, content_raw=m["content"]))
    return dict(course_code=ct.code, title=ct.title, family=family, source_pdf=pdf, header_page=ct.header_page,
                has_module_table=ct.has_module_table, unstitched=ct.unstitched, orphan_tables=ct.orphan_tables, prerequisite=prereq, modules=out_mods, dropped=all_dropped)
