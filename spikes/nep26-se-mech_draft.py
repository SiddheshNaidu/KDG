"""Spike: verify the signatures.csv 'DRAFT watermark' hypothesis for nep26-se-mech. Command: PYTHONIOENCODING=utf-8 python spikes/nep26-se-mech_draft.py"""
import fitz, re, sys
sys.path.insert(0, "spikes")
from importlib import util
s = util.spec_from_file_location("lib", "spikes/nep26-se-mech_lib.py"); lib = util.module_from_spec(s); s.loader.exec_module(lib)
o = open("docs/evidence/regex_runs/nep26-se-mech_draft_watermark.txt", "w", encoding="utf-8")
o.write("command: PYTHONIOENCODING=utf-8 python spikes/nep26-se-mech_draft.py\nsignatures.csv used re.I and unanchored 'DRAFT' on stripped lines (spikes/signatures.py).\n")
for rx in (r"DRAFT", r"(?i)DRAFT", r"(?i)\bDRAFT\b", r"^\s*DRAFT\s*$"):
    n = 0; ex = []
    for sub, p in lib.PDFS.items():
        for i, pg in enumerate(fitz.open(p)):
            for l in pg.get_text().split("\n"):
                if re.search(rx, l): n += 1; ex.append(f"{sub} p{i+1}: {l.strip()!r}")
    o.write(f"\nregex {rx!r}: {n} lines over both PDFs\n" + "".join("  " + e + "\n" for e in ex))
o.close(); print(open("docs/evidence/regex_runs/nep26-se-mech_draft_watermark.txt", encoding="utf-8").read())
