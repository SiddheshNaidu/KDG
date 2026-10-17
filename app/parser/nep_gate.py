"""Accept/reject gate. A course is accepted for the training corpus only if EVERY check passes.
Rejections carry reasons; nothing is dropped silently. Thresholds are PROPOSED and tuned only on counts, never on labels."""
from __future__ import annotations
import re
import sys, pathlib

LAB_CO = re.compile(r"(?<![A-Za-z])LO?\s?\d", re.I)
LAB_CODE = re.compile(r"^[A-Z]{2,4}L\d{3,4}$")
LAB_TITLE = re.compile(r"\b(?:lab|laboratory|workshop|practical|mini[\s-]*project|capstone|seminar|internship)\b", re.I)
GENERIC = {"introduction", "overview", "basics", "basic concepts", "concepts", "fundamentals", "applications", "summary", "conclusion", "definition", "terminology", "examples", "types", "history"}
OTHER_LEAK = re.compile(r"Course\s+Outcome|Course\s+Objective|Teaching\s+Scheme|Examination\s+Scheme", re.I)

LEGIT_LONG = {"polytetrafluoroethylene", "interconnectedness", "recrystallization", "differentiability", "characterization", "multiprogramming", "nondeterministic", "electrochemical", "telecommunications", "electroencephalography"}

def has_glued_words(t: str) -> bool:
    """Some PDFs lose spaces ('Simpleapplicationbasedproblems', 'LaserBeamMachining'); such text must not reach the model."""
    for w in re.findall(r"[A-Za-z]+", t):
        if len(w) >= 18 and w.lower() not in LEGIT_LONG:
            return True
        if len(w) >= 14 and re.search(r"[a-z][A-Z][a-z]", w):
            return True
    return False

def topic_hard_violation(t: str) -> bool:
    """HARD violations make a topic junk. Long phrases (>8 words) are only SOFT (reported, tolerated up to a share)."""
    outside = re.sub(r"\([^()]*\)", "", t)      # ':' or ';' inside a parenthetical is fine
    return (has_glued_words(t) or len(t) > 120 or bool(re.search(r"[;:]", outside)) or t.lower().strip(" .") in GENERIC
            or bool(re.match(r"^\d+\.\d+", t))
            or bool(re.search(r"(?:(?<![A-Za-z])Hrs?\.?|(?<![A-Za-z])CO\s?\d(?:\s*,\s*CO\s?\d)*)\s*$", t))
            or not re.search(r"[A-Za-z]{2}", t))

def topic_soft_long(t: str) -> bool:
    return len(t.split()) > 8

def gate_course(c: dict) -> dict:
    reasons = []
    if c.get("unstitched"): reasons.append(f"unstitched_continuation_pages:{c['unstitched']}")
    if c.get("orphan_tables"): reasons.append("module_table_too_far_from_header")
    mods = c["modules"]
    if not c["has_module_table"]: reasons.append("no_module_table")
    if LAB_TITLE.search(c["title"]) or LAB_CODE.match(c["course_code"]) or any(LAB_CO.search(m["co"]) for m in mods): reasons.append("lab_course")
    nums = [m["number"] for m in mods]
    if nums != list(range(1, len(nums) + 1)): reasons.append(f"module_numbers_not_sequential:{nums}")
    pt = c.get("printed_total_hours")
    ph = c.get("prereq_hours", 0)
    # Completeness: NEP theory courses have 6 modules; fewer/more is accepted only when the PDF's printed total confirms the sum.
    if pt is None and len(mods) != 6: reasons.append(f"module_count_{len(mods)}_without_printed_total")
    if pt is not None and not 4 <= len(mods) <= 8: reasons.append(f"module_count_{len(mods)}")
    if any(m["hours"] <= 0 for m in mods): reasons.append("module_without_hours")
    if pt is not None and pt != sum(m["hours"] for m in mods) + ph: reasons.append(f"printed_total_hours_mismatch:{pt}!={sum(m['hours'] for m in mods)}+{ph}")
    if any(len(m["topics"]) < 1 for m in mods): reasons.append("module_without_topics")
    if sum(len(m["topics"]) for m in mods) < 15: reasons.append("fewer_than_15_topics_in_course")
    dropped_over = sum(1 for d in c.get("dropped", []) if d[0] == "overlong"); n_all = sum(len(m["topics"]) for m in mods) + dropped_over
    if n_all and dropped_over / n_all > 0.10: reasons.append("overlong_topics_dropped_over_10pct")
    topics = [t for m in mods for t in m["topics"]]
    bad = [t for t in topics if topic_hard_violation(t)]
    rate = len(bad) / len(topics) if topics else 1.0
    if rate > 0.03: reasons.append("topic_hard_violation_rate_over_3pct")
    long_share = sum(1 for t in topics if topic_soft_long(t)) / len(topics) if topics else 1.0
    if long_share > 0.25: reasons.append("long_topic_share_over_25pct")
    if any(OTHER_LEAK.search(m["content_raw"]) for m in mods): reasons.append("other_section_leak")
    if not re.search(r"[A-Za-z]{3}", c["title"]): reasons.append("no_title")
    return dict(printed_total=pt, long_share=round(long_share, 3), accepted=not reasons, reasons=reasons, n_topics=len(topics), invalid_rate=round(rate, 3),
                total_hours=sum(m["hours"] for m in mods))
