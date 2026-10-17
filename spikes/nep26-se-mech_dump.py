"""Writes raw dumps (first 60 raw lines of page.get_text().split('\n'), unedited) to docs/evidence/dumps/. Command: PYTHONIOENCODING=utf-8 python spikes/nep26-se-mech_dump.py"""
import fitz, sys
sys.path.insert(0, "spikes")
from importlib import util
s = util.spec_from_file_location("lib", "spikes/nep26-se-mech_lib.py"); lib = util.module_from_spec(s); s.loader.exec_module(lib)
JOBS = [("a", "2403112", 21), ("b", "2393112", 20), ("a", "2403113", 24), ("a", "2403115", 31)]
for sub, code, page in JOBS:
    raw = fitz.open(lib.PDFS[sub])[page - 1].get_text().split("\n")[:60]
    out = f"docs/evidence/dumps/nep26-se-mech_{sub}-{code}_p{page}.txt"
    with open(out, "w", encoding="utf-8", newline="\n") as f: f.write("\n".join(raw))
    print(out, len(raw))
