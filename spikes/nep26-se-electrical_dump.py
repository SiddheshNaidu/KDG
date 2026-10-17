"""Spike: dump first 60 raw get_text() lines of a page, unedited."""
import fitz, sys
PDF = "data/raw/2019-scheme/Electrical-Computer-Engineering/6.51N-B.E.-Electrical-Computer-EngineeringSem-III-IV.pdf"
d = fitz.open(PDF)
for course, pg in (("2213112", 19), ("2214112", 43), ("2213115", 28)):
    L = d[pg - 1].get_text().split("\n")[:60]
    with open(f"docs/evidence/dumps/nep26-se-electrical_{course}_p{pg}.txt", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    print(course, pg, len(L))
