"""Throwaway: writes raw first-60-line dumps (page.get_text().split('\n') order, unedited) to docs/evidence/dumps/"""
import fitz
d = fitz.open("data/raw/2019-scheme/Civil-Engineeing/6.23-N-B.E.-Civil-Engineeing-Sem-III-IV.pdf")
for code, pg in (("2093112", 21), ("2093114", 29), ("2093115", 32)):
    L = d[pg - 1].get_text().split("\n")[:60]
    open("docs/evidence/dumps/nep26-se-civil_%s_p%d.txt" % (code, pg), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
