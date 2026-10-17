# Format: nep26-se-chem-it-a
Status: PARTIAL   (module_row raw-line method reproduces the table oracle's row-number tokens on only 9 of 12 module-table courses after 3 attempts (limit reached); the 3 failures are listed verbatim under Failures. Everything else reached full coverage on its oracle.)

Hypothesis `nep26-se-chem-it` from `docs/evidence/signatures.csv` (Self-Learning markers seen 2x and 7x) is NOT one layout. It splits into two sub-families that share one visual template but differ in numbering, headers and which courses have detail pages:
`nep26-se-chem-it-a` = Chemical Engineering PDF (this file), `nep26-se-chem-it-b` = Information Technology PDF (`docs/formats/nep26-se-chem-it-b.md`). Evidence of the signature row: `docs/evidence/signatures.csv` rows for both PDFs (self_learning 2 vs 7; roman_module_alone 47 vs 76).

Method note. Two readings of every page were used: (1) raw `page.get_text()` line order (what a line-based parser sees) and (2) PyMuPDF `page.find_tables()` (spike `spikes/nep26_se_chem_it_tables.py`). In raw line order the module NAME lines and the DETAILED CONTENT lines of one row are interleaved word by word (see dump `docs/evidence/dumps/nep26-se-chem-it-a_2073112_p21.txt`, lines 12-30), so the name/content boundary is NOT recoverable from raw lines (UNKNOWN, `docs/open_questions.md`). `find_tables()` recovers the 5 columns. Both are documented; table-based figures are marked "method B".

## PDFs in this family (path, pages, evidence file)
| path | pages | detail courses | evidence |
|---|---|---|---|
| data/raw/2019-scheme/Chemical-Engineering/6.40-N-Chemical-Engineering-Sem-III-IV.pdf | 83 | 17 (codes 2073111-2073116, 2993511, 2993512, 2073611 in Sem III; 2074111-2074115, 2074411, 2994511, 2994512 in Sem IV) | `docs/evidence/regex_runs/nep26-se-chem-it-a_course_header.txt` (17/17), `..._facts.txt` |

Folder name `2019-scheme` is a misnomer: page 5 text says `As Per NEP 2020`, `Item No. - 6.40 (N)`, `AC - 20/5/2025`, programme `B.E. (Chemical Engineering)`, `Semester III & IV`, academic year 2025-26 (`docs/evidence/regex_runs/nep26-se-chem-it-a_detect_all_pdfs.txt`). Page layout of the PDF (`nep26-se-chem-it-a_facts.txt`, `page heads`): pages 2-4 forwarding/circular lists, page 5 cover block, pages 6-9 NEP preamble, credit structure and scheme, pages 10-13 overview scheme tables (>=3 distinct 7-digit codes per page), page 14 cover `Semester III / Vertical - 1 / Major`, pages 15-82 course detail pages, page 83 `Letter Grades and Grade Points` table and signatures.

Course types observed (from `nep26-se-chem-it-a_facts.txt`, `..._prereq_row.txt`, `..._topic_validity.txt`):
- Theory with module table, arabic rows: 2073111 (rows `01`-`06`), 2073112, 2073113, 2073114, 2074111, 2074112, 2074113 (rows `1`-`6`).
- Lab with module table plus experiment list: 2073115 (header says `LO Mappin g`).
- Lab with NO module table (Lab Objectives/Outcomes, List of Experiments, List of Assignments only): 2073116, 2074114, 2074115.
- Common courses with Roman rows and `LO` mapping, `2*+2` scheme: 2993511 Entrepreneurship Development, 2993512 Environmental Science (header `Unit Name | Topic Name | Topic Description`), 2994511 Business Model Development, 2994512 Design Thinking.
- Mini Project, no module table: 2073611, 2074411.
Module table present in 12 of 17 courses (`nep26-se-chem-it-a_topic_validity.txt`, excluded list = 5 courses).

## Detection (regex + coverage matched/total)
All four must match on the text of pages 1-6 (positive test on this PDF plus negative test over all 25 PDFs under data/raw):
- `As Per NEP 2020`
- `U\.G\. Second Year Programme`
- `Semester\s+III\s*&\s*IV`
- `Name of the Programme\s*[–-]\s*B\.E\.\s*\((?:Chemical Engineering|Information Technology)\)`
Coverage: 2/2 expected positives, 0 false positives over 25 PDFs (`docs/evidence/regex_runs/nep26-se-chem-it-a_detect_all_pdfs.txt`). Sub-family `a` vs `b` is decided by the programme name only (Chemical Engineering = a). Simple per-PDF test `Item No\.\s*[–-]\s*6\.\d+\s*\(N\)` plus `As Per NEP 2020` also matched 1/1 (`nep26-se-chem-it-a_detect.txt`) but is not discriminating by itself.

## Course header pattern
Raw lines at the top of a detail page (dump `docs/evidence/dumps/nep26-se-chem-it-a_2073112_p21.txt` is a later page; header lines are in `docs/evidence/regex_runs/nep26-se-chem-it-a_course_header.txt` regex): lines `Course`, `Code`, `Course Name`, `Teaching Scheme`, ... then the code on its own line (7 digits, trailing space in raw text), then the title lines, then scheme cells (`2`, `-`, `1`, `2`, `-`, `3` or `2*+2`). A second header table (Theory / Term work / IAT / Exam marks) repeats the code and title, so the code line occurs twice per course.
Regex (run on every non-overview page, oracle = distinct codes on overview pages): `(?m)^Course\s*\nCode\s*\n(?:.*\n){0,38}?[ \t]*(\d{7})[ \t]*\n` -> 17/17 (`nep26-se-chem-it-a_course_header.txt`). Attempts: 1.
Overview pages are excluded by the rule "page has >=3 distinct 7-digit code lines".

## Title wrapping
Titles wrap over 1-4 raw lines inside the first header table (examples: `Chemical`/`Engineering`/`Mathematics`; `Chemical`/`Engineering`/`Thermodynamics-`/`I`; `Mini Project-I`). Rule: join the lines after the code line with one space until a scheme-token line. Terminator regex `^\s*(?:\d{1,2}|--|–|\d\*\+\d)\s*$`. Oracle: title rebuilt from the second header table (or from the overview table when the second table has no code line, 2994512), compared ignoring spaces/hyphens -> 17/17 (`nep26-se-chem-it-a_title_wrap.txt`, attempt 2 of 2; attempt 1 mis-ended titles containing a lone `-` and lacked the overview fallback).

## Module row pattern
Header row (raw lines): `Sr. No` / `Name of Module` (or `Module`; `Unit Name` + `Topic Name` for 2993512) / `Detailed Content` (or `Topic Description`) / `Hours` (or `Hrs` in 2073111) / `CO` `Mapping` (or `LO Mapping`, split `Mappin`+`g` in 2073115) (dumps `..._2073112_p21.txt`, `..._2073115_p32.txt`, `..._2073111_p16.txt`).
Row cells in raw order: row number, name lines, content lines (words may be one per line), hours line, CO/LO line. The hours+CO lines are NOT always at the end of the row: in 2073111 module 4 the tail `5`/`CO4` is printed at the page break before the row's content continues on the next page (`docs/evidence/dumps/nep26-se-chem-it-a_2073111_p16_l23-82.txt`, last lines).
Method A (raw lines, `spikes/nep26_se_chem_it_mod.py`): scope starts at a `DETAILED SYLLABUS` heading or a `Detailed Content` line, ends at first Text Books/References/Assessment line; a row starts at a line equal to the next expected number (`N`, `0N` or Roman) that is not followed by a CO/LO line or a dash cell. Weakness (measured): hours cells such as `05` or `04` followed by blank lines and then the CO/LO line are mistaken for the next row number, because blank lines can sit between the hours line and the CO/LO line (2993512, 2994511, 2994512). Method B: `find_tables()`, module table = 5 columns with 4th header Hours/Hrs and 5th matching `(CO|LO)s?\s*Mappin\s*g?s?`; rows with empty first two cells are merged into the previous row.
Coverage: A reproduces B's row-number token sequence on 9/12 courses (`nep26-se-chem-it-a_module_row.txt`, attempt 3 of 3, FINAL). Row COUNT agreed on 11/12 at attempt 2; the stricter token check at attempt 3 exposed the hours-as-number defect above. PARTIAL.

## Prerequisite row
Two forms (`nep26-se-chem-it-a_prereq_row.txt`):
- table row 0: raw lines `0`, `Prerequisite` (also `Prerequisites.`, `Prerequisites`), then text or `–`/`--`/`-`. Present in 8 of 12 module-table courses: 2073112, 2073113, 2073114, 2073115, 2993511, 2074111, 2994511, 2994512. Absent in 2073111, 2993512, 2074112, 2074113.
- heading line `Prerequisite:` before the table (2073111, 2073112, 2073114, 2073115, 2074111, 2074112, 2074114, 2074115).
Regexes: `(?m)^0[ \t]*\n[ \t]*Prerequisites?\.?[ \t]*\n` (row) and `(?m)^Prerequisites?[ \t]*:[ \t]*$` (heading). Row regex agrees with the table oracle on 12/12 courses. Courses with neither: 2073116, 2993512, 2073611, 2074113, 2074411. Row 0 is excluded from module counts and from hours/CO statistics.

## Self-learning markers (all spellings seen)
Regex `(?i)self[\s\-–]*(?:learning|study)[\s\-–]*(?:topics?)?\s*:?` over raw course text (`nep26-se-chem-it-a_selflearning.txt`). Spellings (whitespace collapsed): `Self-Learning Topics:` (2), `Self -Learning Topics:` (3, space before hyphen), `Self -Learning Topics ` (1, no colon, 2073111 module 4), `Self-learning Topics` (1), `Self-learning Topics:` (2994511, 2994512, 4 each), plus sentence mentions `self-learning topic`, `self-learning`.
Courses with markers inside module rows: 2073111 (6 markers, one per module), 2994511 (4), 2994512 (4). 5 of 17 courses have any raw hit; in 2073611/2074411 the hits are the sentence `Mini Projects should focus on self-learning, innovation, ...` (not a marker). Policy sentences: `No Questions to be asked from Self-learning Topics.` (2073111 p17 line 40) and `4-6 students should be assigned a self-learning topic.` (2073111 p18 line 8) (`nep26-se-chem-it-a_facts.txt`). The marker starts mid-line inside the content cell, so a marker can be followed by topics on the same raw line (`Self-Learning Topics: Characteristics of Linear`). `self-study` spelling: none in this PDF. True number of self-learning items: UNKNOWN.

## Hours / CO tails
Hours cell: `^\d{1,2}$` -> 71/71 module rows (`nep26-se-chem-it-a_hours_tail.txt`). Spellings: `07`, `5`, `8`, `14`, `02`. CO/LO cell: `^(?:(?:CO|LO|L0|L)?\s?\d+)(?:\s*,\s*(?:CO|LO|L0|L)?\s?\d+)*$` -> 71/71 (`nep26-se-chem-it-a_co_tail.txt`; attempt 2 of 3: attempt 1 failed the 6 rows of 2074112 whose CO cell is a bare digit `1`..`6`). Shapes seen: `CO1`, `LO1`, bare `1`. Mapping header word: `CO` (theory) or `LO` (labs/common courses). Tail raw lines are two consecutive lines (hours then CO), `5`/`CO1`.

## Stop markers
End of the module table / start of back matter: first line starting with `Text Books`, `Textbooks`, `References`, `Reference Books`, or `Assessment`. Regex `(?im)^\s*(?:Text\s*Books?|Textbooks?|References?|Reference\s+Books?|Assessment)\b.*$` -> 17/17 (`nep26-se-chem-it-a_stop_books.txt`; attempt 2: attempt 1 required Text Books and missed 2073111, 2073116, 2073611, 2074115, 2074411). Weak: for Mini Project courses it can only match an `Assessment`-prefixed heading and is not a module-table stop. Course end: next course header, or a cover page (page whose first lines are `Semester III|IV`, `SEMESTER III`, `Vertical - n`, `Detail(ed) Syllabus`: pages 14, 38, 47, 51, 70, 74 in `nep26-se-chem-it-a_facts.txt` cover list; pages 10 and 12 are overview pages). Last course ends before page 83 (`Letter Grades and Grade Points` table). Whether `Online References:` / `Online Resources:` and the `List of Experiments` / `List of Assignments / Tutorials` tables appear after the books in every lab: UNKNOWN beyond the 2073115 raw run (no saved dump).

## Watermarks / noise lines
- Draft watermark: none observed (`docs/evidence/signatures.csv`, column draft_watermark = 0 for this PDF).
- Bare page-number lines: 30 of 69 pages (14-82) end with a bare 1-3 digit number (`13`, `15`, `17`, ...), mid-stream footer, e.g. `21.86: 17` (`nep26-se-chem-it-a_facts.txt`).
- Footer line `University of Mumbai, Second Year Chemical Engineering, REV2024 Scheme` (page 37 line 96, page 79 line 111).
- Cover pages `Semester III|IV / Vertical - n / Detail Syllabus` inside the page range of the previous course (pages 38, 47, 51, 70, 74).
- Whitespace-only lines are common (padding between table cells).
- Bullet glyphs: `●` (U+25CF) 52, `` 4, `` 6, `` 1 over the whole PDF.
- Math in private/style fonts (e.g. `𝑐𝑜𝑠𝑘𝑛`, `∆`, `∇`) yields candidate "topics" with no letters (R8).

## Numbering styles (Roman / arabic / 1.1 / 1.)
Per course (`nep26-se-chem-it-a_facts.txt`): `01`-`06` zero padded (2073111); `1`-`6` (2073112-2073115, 2074111-2074113); Roman `I`-`VI` (2993511, 2993512, 2994511, 2994512). Row 0 = Prerequisite. Sub-numbering `1.1`, `2.1`, ... inside content in 2073114 (R6 examples `1.1 First law of Thermodynamics...`).

## Topic separators
Inside a content cell: commas, full stops followed by a capital, colons after sub-headings (`Pressure and Fluid Statics:`), `&`, `and`, parenthetical notes `(No theorems/ proof)`, `(without proof)`, `(use Chemical engineering examples.)`, dash-lists `Manometers – Piezometers, U- tube, ...`. Sub-headings ending with `:` precede lists (R3 violations). No bullets in theory modules.

## Known oddities
1. Name/content interleaving in raw lines; one word per line in some cells (`Discrete`/`and`/`Continuous`, dump `..._2073111_p16.txt`).
2. Hours/CO tail can appear before the end of a row at a page break (2073111 module 4).
3. `Mappin`/`g` split header (2073115); `Hrs` vs `Hours`; `Name of Module` vs `Module` vs `Unit Name`; `Detailed Content` vs `Topic Description`.
4. 2074112 CO cell is a bare digit; 2074113 hours without padding (`8`, `7`).
5. Row V of 2993512 (Environmental Science) is lost by `find_tables()` (page 45 top) but present in raw lines: method A = 6 rows, method B = 5.
6. Common courses 2993511/2 and 2994511/2 use Roman rows, `LO` mapping and `2*+2` scheme in their header tables (`nep26-se-chem-it-a_facts.txt`, `nep26-se-chem-it-a_title_wrap.txt` titles). The 2994511 segment includes page 79 where 2994512 starts, so a page-range parser must assign tables on a page below a `Course Code` header table to the new course (owner rule in `spikes/nep26_se_chem_it_tables.py`).
7. 2993512 is on the same page as the end of 2993511 (page 43); courses start mid-page, so segmentation must use the header lines, not page boundaries.
8. Courses 2073116, 2074114, 2074115 have no module table.
9. A footer says `REV2024 Scheme` while the cover says NEP 2020 (UNKNOWN which is the Scheme).

## Exact regexes with measured coverage (each links to docs/evidence/regex_runs/<file>)
| name | regex (also in `spikes/nep26_se_chem_it_runs.py`) | matched/total | attempts | file |
|---|---|---|---|---|
| detect (4 regexes) | see Detection | 2/2 positives, 0 false positives / 25 PDFs | 1 | nep26-se-chem-it-a_detect_all_pdfs.txt |
| course_header | `(?m)^Course\s*\nCode\s*\n(?:.*\n){0,38}?[ \t]*(\d{7})[ \t]*\n` | 17/17 | 1 | nep26-se-chem-it-a_course_header.txt |
| title_end | `^\s*(?:\d{1,2}\|--\|–\|\d\*\+\d)\s*$` | 17/17 | 2 | nep26-se-chem-it-a_title_wrap.txt |
| module_row (method A vs B token sequence) | sequential number rule, see Module row pattern | 9/12 PARTIAL | 3 (limit) | nep26-se-chem-it-a_module_row.txt |
| prereq_row | `(?m)^0[ \t]*\n[ \t]*Prerequisites?\.?[ \t]*\n` | 12/12 | 1 | nep26-se-chem-it-a_prereq_row.txt |
| prereq_heading | `(?m)^Prerequisites?[ \t]*:[ \t]*$` | same file (no oracle for heading) | 1 | nep26-se-chem-it-a_prereq_row.txt |
| hours_cell | `^\d{1,2}$` | 71/71 | 1 | nep26-se-chem-it-a_hours_tail.txt |
| co_cell | `^(?:(?:CO\|LO\|L0\|L)?\s?\d+)(?:\s*,\s*(?:CO\|LO\|L0\|L)?\s?\d+)*$` | 71/71 | 2 | nep26-se-chem-it-a_co_tail.txt |
| selflearning | `(?i)self[\s\-–]*(?:learning\|study)[\s\-–]*(?:topics?)?\s*:?` | 5/17 courses have any hit; no ground truth | 1 | nep26-se-chem-it-a_selflearning.txt |
| stop_books | `(?im)^\s*(?:Text\s*Books?\|Textbooks?\|References?\|Reference\s+Books?\|Assessment)\b.*$` | 17/17 (weak) | 2 | nep26-se-chem-it-a_stop_books.txt |
(In markdown table cells `\|` stands for the alternation bar.)

## Failures (verbatim, per regex, per attempt 1-3)
- module_row attempt 1: `2993512: sequential raw-line rows=None, table-oracle rows=5` (heading `Topic Description` not matched by the `Detailed Content` start) -> attempt 2 gave rows=6 for 2993512 (count agreed 11/12; the oracle has 5 because find_tables drops row V, raw line `45.1: V`).
- module_row attempt 3 (FINAL, verbatim from the evidence file; token check): 
  - `2993512: raw-line rows=6 tokens=['I', 'II', 'III', 'IV', '05', 'VI'] | table-oracle rows=5 tokens=['I', 'II', 'III', 'IV', 'VI']`
  - `2994511: raw-line rows=6 tokens=['01', 'II', 'III', '04', 'V', 'VI'] | table-oracle rows=6 tokens=['I', 'II', 'III', 'IV', 'V', 'VI']`
  - `2994512: raw-line rows=6 tokens=['I', 'II', 'III', 'IV', '05', 'VI'] | table-oracle rows=6 tokens=['I', 'II', 'III', 'IV', 'V', 'VI']`
  Not refined further (3-attempt limit). Cause: an hours cell equal to the expected Arabic padded number is taken as the row number.
- co_cell attempt 1 (6 failures, verbatim): `2074112 module 1: co cell='1'` ... `2074112 module 6: co cell='6'` -> fixed in attempt 2.
- title_wrap attempt 1: `2994512 page 79: table1='Design Thinking' | table2='None'` -> fixed by overview fallback in attempt 2.
- stop_books attempt 1 (verbatim): `2073111 pages 15-18: no Text Books/Textbooks heading line`; same for 2073116 (36-38), 2073611 (48-52), 2074115 (67-71), 2074411 (71-75) -> broadened in attempt 2 (now trivially matching via `Assessment`/`References`).
All attempt histories are appended at the end of each regex_runs file.

## Topic validity census (violations by rule id, total topics)
Naive splitter (not a parser; `spikes/nep26_se_chem_it_runs.py`) over the 12 courses with a module table; module name excluded, self-learning text cut off: total 450 candidate topics, 109 violate at least one rule. By rule (a candidate may violate several): R1 52, R2 33, R3 59, R4 10, R5 1, R6 12, R7 0, R8 5 (`docs/evidence/regex_runs/nep26-se-chem-it-a_topic_validity.txt`, includes 3 examples per rule). The high R1/R2/R3 counts reflect the naive splitter on comma/period-joined cells with `Heading: list` patterns, not final parser quality.

## Golden courses (5, DRAFT) and how they were drafted
5 golden courses exist for the pair of sub-families (spread over both PDFs); this sub-family owns 2: `tests/golden/nep26-se-chem-it-a/2073112.json` (Fluid Flow Operations, theory, 82 topics) and `tests/golden/nep26-se-chem-it-a/2073111.json` (Chemical Engineering Mathematics, odd: self-learning markers, zero-padded rows, 31 topics). Sub-family b owns 3 (`nep26-se-chem-it-b.md`).
Drafting: module table cells printed by `spikes/nep26_se_chem_it_tables.py` (method B, content of that course only) were read by hand; topics split into atomic noun phrases; sub-headings (`Pressure and Fluid Statics:`), generic `Introduction`, and trailing hours/CO removed; self-learning topics EXCLUDED (policy UNKNOWN); `Bender Scmidt` normalised to `Bender-Schmidt`, duplicate names across modules disambiguated (e.g. `Continuity equation in compressible flow`). All golden topics pass `validate()` (0 violations). Status of every file: `DRAFT - needs human sign-off`; nothing is verified. No mini-project, no lab-without-module-table golden was drafted (their Topic definition is UNKNOWN).

## UNKNOWN items (also copied to docs/open_questions.md)
- Name vs content boundary from raw line order (needs find_tables or bbox).
- Self-learning items as Topics or not; true count of self-learning items.
- Bundle policy for `A and B`.
- 2993512 row V lost by `find_tables()`.
- Topics for labs without module table (2073116, 2074114, 2074115) and for Mini Projects (2073611, 2074411).
- Scheme name: cover says NEP 2020, page footer says `REV2024 Scheme`, folder says `2019-scheme`.
- Layout of the lab list tables beyond the counts above (experiment list parsing not specified).
