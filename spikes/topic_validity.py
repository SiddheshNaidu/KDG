"""Spike (PROPOSED rules, see docs/formats/topic_validity.md). Usage: import validate(topic)->list[str] of violated rule ids."""
import re
GENERIC = {"introduction","overview","basics","basic concepts","concepts","fundamentals","applications","case study","case studies",
           "summary","conclusion","definition","definitions","terminology","examples","types","history","scope","introduction to","self learning topics"}
PROCEDURAL = re.compile(r"^(installation|setup|set up|install|download|configure|configuration of|write a program|implement|experiment|lab|practical)\b", re.I)
def validate(t: str):
    v = []
    s = t.strip()
    w = s.split()
    if not 1 <= len(w) <= 8: v.append("R1_word_count_1_to_8")
    if len(s) > 80: v.append("R2_len_over_80_chars")
    if re.search(r"[;:]", s): v.append("R3_contains_colon_or_semicolon")
    if s.lower().strip(" .:,") in GENERIC: v.append("R4_generic_heading")
    if PROCEDURAL.search(s): v.append("R5_procedural")
    if re.match(r"^\d+(\.\d+)*[\s.)]", s): v.append("R6_leading_numbering")
    if re.search(r"\b(Hrs?\.?|Hours)\b|\bCO\s?\d", s): v.append("R7_hours_or_CO_leak")
    if not re.search(r"[A-Za-z]", s): v.append("R8_no_letters")
    return v
if __name__ == "__main__":
    import sys, json
    for t in sys.argv[1:]: print(t, validate(t))
