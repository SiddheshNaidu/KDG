"""Spike: can PyMuPDF find_tables() give course headers + module tables across ALL PDFs? Measures only."""
import fitz, re, glob, sys, json, collections
CODE = re.compile(r"^(?:\d{7,8}|[A-Z]{2,5}\d{3,5}[A-Z]?)$")
def norm(c): return re.sub(r"\s+", " ", (c or "")).strip()
def probe(pdf):
    d = fitz.open(pdf); cur = None; courses = []; mod_tables = 0
    for pn in range(len(d)):
        try: tabs = d[pn].find_tables().tables
        except Exception: continue
        for t in tabs:
            rows = [[norm(c) for c in r] for r in t.extract()]
            if not rows: continue
            h = " ".join(rows[0])
            if "Course Code" in h and ("Teaching" in h or "Course Name" in h):
                for r in rows[1:]:
                    if r and CODE.match(r[0].replace(" ", "")):
                        cur = dict(code=r[0].replace(" ", ""), title=r[1] if len(r) > 1 else "", page=pn + 1, rows=[], hdr=False); courses.append(cur); break
                continue
            if cur is None: continue
            if re.search(r"Detailed Content", h, re.I):
                cur["hdr"] = True; cur["rows"] += rows[1:]; mod_tables += 1; cur["_open"] = True
            elif cur.get("_open") and 4 <= max(len(r) for r in rows) <= 5 and re.search(r"CO\s?\d|LO\s?\d|^\d{1,2}$", " ".join(r[-1] if r else "" for r in rows) + " " + " ".join(r[-2] if len(r) > 1 else "" for r in rows)):
                cur["rows"] += rows
    return courses, mod_tables
if __name__ == "__main__":
    tot = collections.Counter()
    for pdf in sorted(glob.glob("data/raw/**/*.pdf", recursive=True)):
        cs, mt = probe(pdf); withmod = [c for c in cs if c["hdr"]]
        print(f"{pdf.split('/')[-1][:44]:44} headers={len(cs):3} with_module_table={len(withmod):3} mod_tables={mt}")
        tot["headers"] += len(cs); tot["with"] += len(withmod)
    print(dict(tot))
