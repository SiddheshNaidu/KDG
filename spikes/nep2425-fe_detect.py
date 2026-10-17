"""Detection regex for nep2425-fe tested against EVERY PDF under data/raw (matched = PDFs matching).
Usage: PYTHONIOENCODING=utf-8 python spikes/nep2425-fe_detect.py"""
import fitz, re, glob
CMD = "PYTHONIOENCODING=utf-8 python spikes/nep2425-fe_detect.py"
RX = re.compile(r"^[ \t]*(?:ESC|ESL|BSC|BSL|AEC|VSEC|VSEL|VEC)[ ]?1\d{2}[ \t]*(?:\S.*)?$", re.M)
IAT = re.compile(r"IAT-I")
files = sorted(glob.glob("data/raw/**/*.pdf", recursive=True))
fe, other = [], []
for f in files:
    d = fitz.open(f)
    t = "\n".join(p.get_text() for p in d)
    hit = bool(RX.search(t)) and bool(IAT.search(t)) and len(d) <= 8
    (fe if "2024-25-scheme/FE" in f.replace("\\", "/") else other).append((f, hit, len(RX.findall(t))))
lines = [f"command: {CMD}", f"regex_code: {RX.pattern} (re.M) AND regex_iat: {IAT.pattern} both present in document text AND page count <= 8 (attempt 2; attempt 1 without the page-count clause matched 5/5 family but 6 false positives: DS/AIML/CSE-AIML/EXTC/IT/Mechanical PDFs under 2019-scheme/ that embed the same FE course codes, 60 code lines each)",
         f"matched/total in family (5 FE pdfs): {sum(h for _, h, _ in fe)}/{len(fe)}",
         f"false positives among {len(other)} other PDFs under data/raw: {sum(h for _, h, _ in other)}", "failures (family PDFs not matched):"]
lines += [f"  {f}" for f, h, _ in fe if not h] or ["  (none)"]
lines += ["false positives (other PDFs matched):"] + ([f"  {f} ({n} code lines)" for f, h, n in other if h] or ["  (none)"])
lines += ["family PDF hit counts:"] + [f"  {f}: {n}" for f, h, n in fe]
open("docs/evidence/regex_runs/nep2425-fe_detection.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
