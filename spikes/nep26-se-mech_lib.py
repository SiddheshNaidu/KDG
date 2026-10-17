"""Spike lib for family nep26-se-mech (throwaway). Loads courses from the 2 PDFs; PyMuPDF page.get_text() line order."""
import fitz, re, sys
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
PDFS = {"a": "data/raw/2019-scheme/Mechanical-Engineering/6.35-N-B.E.-Mechanical-EngineeringSem-III-IV.pdf",
        "b": "data/raw/2019-scheme/Mecanical-Automation-Engineering/6.44-N-B.E.-Mecanical-Automation-Engineering-Sem-III-IV.pdf"}
START_RX = r"^Credits Assigned\s*$"          # course-start page marker
CODE_RX = r"^\s*(\d{7})\s*$"
def load_courses():
    out = []
    for sub, path in PDFS.items():
        d = fitz.open(path)
        pages = [[l for l in pg.get_text().split("\n")] for pg in d]
        starts = []
        for i, L in enumerate(pages):
            if any(re.match(START_RX, l.strip()) for l in L) and i >= 14:   # i>=14: skip front-matter scheme tables (pages 1-14)
                starts.append(i)
        for n, s in enumerate(starts):
            e = starts[n + 1] if n + 1 < len(starts) else len(pages)
            lines = [(p + 1, l.strip()) for p in range(s, e) for l in pages[p] if l.strip()]
            out.append({"sub": sub, "pdf": path, "start": s + 1, "end": e, "lines": lines, "raw_first": pages[s]})
    return out
def first_code(c):
    for p, l in c["lines"]:
        m = re.match(CODE_RX, l)
        if m: return m.group(1), p
    return None, None
