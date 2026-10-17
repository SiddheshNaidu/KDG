"""Spike: read-only census of PDFs. Not part of the product."""
import csv, re, sys, pathlib, fitz
root = pathlib.Path(sys.argv[1]); out = sys.argv[2]
rows = []
for p in sorted(root.rglob("*.pdf")):
    d = fitz.open(p); texts = [pg.get_text() for pg in d]; full = "\n".join(texts)
    first = "\n".join(texts[:3])
    rows.append(dict(
        path=str(p.relative_to(root)).replace("\\", "/"), pages=len(d), chars=len(full),
        nep_word_all=len(re.findall(r"\bNEP\b", full)),
        nep_policy_all=len(re.findall(r"National Education Policy", full, re.I)),
        nep_word_first3=len(re.findall(r"\bNEP\b", first)),
        rev2019_all=len(re.findall(r"Rev(?:ision|ised)?[-\s]*2019|C[-\s]*Scheme", full, re.I)),
        draft_copy=len(re.findall(r"DRAFT COPY", full)),
        scanned=int(len(full) < 20 * max(1, len(d))),
        first_line=re.sub(r"\s+", " ", texts[0].strip())[:90] if texts else ""))
w = csv.DictWriter(open(out, "w", newline="", encoding="utf-8"), fieldnames=rows[0].keys())
w.writeheader(); w.writerows(rows)
for r in rows: print(r["path"][-58:].ljust(58), r["pages"], r["chars"], "NEP:", r["nep_word_all"], r["nep_policy_all"], "rev19:", r["rev2019_all"], "draft:", r["draft_copy"], "scan:", r["scanned"])
