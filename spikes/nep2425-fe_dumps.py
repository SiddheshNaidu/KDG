"""Writes the 3 UNEDITED raw-line dumps (first 60 lines of page.get_text() split on newline) to docs/evidence/dumps/."""
import fitz
D = "data/raw/2024-25-scheme/FE/"
for course, pdf, page in [("BSC103", "Applied Chemistry syllabus 2024-25.pdf", 2), ("ESC101", "NEW EM SYLLABUS 2024-25.pdf", 2), ("ESL102", "02 Syllabus.pdf", 4)]:
    L = fitz.open(D + pdf)[page - 1].get_text().split("\n")[:60]
    open(f"docs/evidence/dumps/nep2425-fe_{course}_p{page}.txt", "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print(course, page, len(L))
