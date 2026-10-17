"""Independent traceability check: every extracted topic must appear in the raw page text of the pages it was read from."""
from __future__ import annotations
import re
import fitz

def compact(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())

class PageText:
    def __init__(self, pdf: str):
        self.doc = fitz.open(pdf); self._c: dict[int, str] = {}
    def page(self, n: int) -> str:
        if n not in self._c:
            self._c[n] = compact(self.doc[n - 1].get_text())
        return self._c[n]

def traceability(course: dict, pt: PageText) -> dict:
    total = hit = 0; missing = []
    for m in course["modules"]:
        pages = set(m["pages"]) | {p + 1 for p in m["pages"]}
        blob = "".join(pt.page(p) for p in sorted(pages) if p <= len(pt.doc))
        for t in m["topics"]:
            total += 1
            if compact(t) in blob: hit += 1
            else: missing.append(t[:70])
    return dict(trace_rate=round(hit / total, 3) if total else 0.0, trace_missing=missing[:5])
