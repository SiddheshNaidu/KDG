"""Position (line index within its page) of the header-table code line for each course; evidence for the a/b sub-family split."""
import sys, importlib
sys.path.insert(0, "spikes")
L = importlib.import_module("nep26-se-core_lib")
out = ["command: PYTHONIOENCODING=utf-8 python spikes/nep26-se-core_hdrpos.py",
       "measure: line index (0-based, page.get_text() order) of the first teaching-table code line (attempt2 course_start) within its page, per course in list order; threshold 'floating' = index > 45",
       "sub-family a = header block at top of page for all but at most 1 course/PDF; b = floating for >=5 courses"]
for p in L.PDFS:
    ls = L.lines(p)
    st = []
    for k, e in L.segment(ls):
        st.append((ls[k][0], ls[k][1]))
    fl = sum(1 for _, j in st if j > 45)
    out.append(f"{p.split('/')[0]}: page:idx = " + ", ".join(f"{a}:{b}" for a, b in st) + f" | floating={fl}/17")
open("docs/evidence/regex_runs/nep26-se-core_header_block_position.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out[3:]))
