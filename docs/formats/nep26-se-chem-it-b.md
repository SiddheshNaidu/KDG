# Format: nep26-se-chem-it-b
Status: PARTIAL   (two reasons, both measured: (1) module_row raw-line method reproduces the table oracle's row-number tokens on only 9 of 12 module-table courses after 3 attempts (limit reached); (2) course_header covers 13 of 17 overview codes because 4 courses listed on the overview pages have no detail pages in this PDF. Every other regex reached full coverage on its oracle.)

Sub-family `b` of the hypothesis `nep26-se-chem-it` (see `docs/formats/nep26-se-chem-it-a.md` for why the hypothesis splits). `b` = Information Technology PDF. Evidence of the signature row: `docs/evidence/signatures.csv` (self_learning 7, roman_module_alone 76 for this PDF).

Method note. Two readings of every page were used: raw `page.get_text()` line order and `page.find_tables()` (spike `spikes/nep26_se_chem_it_tables.py`, "method B"). In raw order the module name lines and content lines of a row are interleaved, so the name/content boundary is not recoverable from raw lines (dump `docs/evidence/dumps/nep26-se-chem-it-b_2344112_p41.txt`; UNKNOWN in `docs/open_questions.md`). Row 0 cells and the Roman row number are separate raw lines.

## PDFs in this family (path, pages, evidence file)
| path | pages | detail courses | evidence |
|---|---|---|---|
| data/raw/2019-scheme/Information-Technology/6.34-N-B.E.-Information-Technology-Sem-III-IV.pdf | 70 | 13 (Sem III: 2343111-2343116, 2343611; Sem IV: 2344111-2344115, 2344411) | `docs/evidence/regex_runs/nep26-se-chem-it-b_course_header.txt` (13/17 of overview codes), `..._facts.txt` |

Folder `2019-scheme` is a misnomer: page 5 says `AC - 20/5/2025`, `Item No. - 6.34 (N)`, `As Per NEP 2020`, programme `B.E. (Information Technology)`, `Semester III & IV`, 2025-26 (`nep26-se-chem-it-b_detect_all_pdfs.txt`, `nep26-se-chem-it-b_facts.txt` page heads). Page layout (`nep26-se-chem-it-b_facts.txt`): pages 2-4 forwarding lists, 5 cover block, 6-10 NEP text/credit structure/scheme, 11-14 overview scheme tables (17 codes: 9 in Sem III, 8 in Sem IV), 15 cover `Vertical - 1 / Major / Sem. - III`, 16-69 course detail pages with covers at 35 (`Sem. - IV`), 53 (`Vertical - 4 / VSEC`), 62 (`Vertical - 6 / CEP`), page 70 `Letter Grades and Grade Points` and signatures.

The overview pages also list 2993511, 2993512, 2994511, 2994512 (common courses), but this PDF has no detail pages for them (`nep26-se-chem-it-b_course_header.txt` failures). The same four codes do have detail pages in the Chemical Engineering PDF (`nep26-se-chem-it-a_course_header.txt`). Where their syllabus is for IT: UNKNOWN.

Course types (from `nep26-se-chem-it-b_facts.txt`, `..._prereq_row.txt`):
- Theory, module table with Roman rows: 2343111 Applied Mathematics Thinking-I, 2343112 Advance Data Structure & Analysis, 2343113 Database Management System & Application, 2343114 Automata Theory, 2344111 Applied Mathematics Thinking-II, 2344112 Operating System, 2344113 Computer Network & Network Design.
- Lab with module table (`LO` mapping): 2343115 ADSA Lab (3rd header `Suggested list of Practical`), 2344114 Unix Lab, 2344115 Network Design Lab.
- Lab without module table: 2343116 SQL Lab (Experiment List table: `Sr. No. | Experiment List | Hours | LO Mapping`).
- Mini-Project with module tables: 2343611 Mini-Project - Full Stack Java Programming (Roman rows, LO); 2344411 Mini-Project - Programming Paradigm has TWO module tables (arabic rows 1-6 with `CO 1` style, then Roman rows I-VI with `LO 1` style, `nep26-se-chem-it-b_facts.txt` hours list).
Module table present in 12 of 13 courses (`nep26-se-chem-it-b_topic_validity.txt`).

## Detection (regex + coverage matched/total)
All four must match on text of pages 1-6 (negative test over all 25 PDFs under data/raw):
- `As Per NEP 2020`
- `U\.G\. Second Year Programme`
- `Semester\s+III\s*&\s*IV`
- `Name of the Programme\s*[–-]\s*B\.E\.\s*\((?:Chemical Engineering|Information Technology)\)`
2/2 expected positives, 0 false positives (`nep26-se-chem-it-b_detect_all_pdfs.txt`). `b` vs `a` is decided by programme name (`Information Technology` = b). Per-PDF test `Item No\.\s*[–-]\s*6\.\d+\s*\(N\)` + `As Per NEP 2020`: 1/1 (`nep26-se-chem-it-b_detect.txt`, not discriminating alone).

## Course header pattern
Same as sub-family a: lines `Course`, `Code`, `Course Name`, `Teaching Scheme`, ..., then the 7-digit code line, title lines, scheme cells; the code and title repeat in a second header table. Regex (non-overview pages; oracle = distinct codes on overview pages): `(?m)^Course\s*\nCode\s*\n(?:.*\n){0,38}?[ \t]*(\d{7})[ \t]*\n` -> 13/17 (`nep26-se-chem-it-b_course_header.txt`, attempt 1). The 4 failures are absent courses, not regex defects (verbatim below).
Course start is near the top of a page here (page 16, 20, 23, ... line 13) and courses mostly start on a fresh page, but 2344115 spills to page 54 where 2344411 starts (`nep26-se-chem-it-b_facts.txt` page ranges 50-54 and 54-63), so segment by header lines.

## Title wrapping
Titles wrap over 1-4 raw lines (`Applied`/`Mathematics`/`Thinking-I`; `Computer Network &`/`Network Design`; `Mini-Project - Full`/`Stack Java`/`Programming`). Rule: join lines after the code line with one space until a scheme-token line. Terminator `^\s*(?:\d{1,2}|--|–|\d\*\+\d)\s*$` -> 13/13 against the second table (`nep26-se-chem-it-b_title_wrap.txt`, attempt 2 of 2; attempt 1 cut `Mini-Project - Programming Paradigm` at the lone `-` line). Reconstructed titles are listed in that file.

## Module row pattern
Header lines: `Sr.` `No.` / `Name of Module` or `Module` / `Detailed Content` (2343115: `Suggested list of Practical`) / `Hours` / `CO` `Mapping` (variants `CO Mappings`, `LO Mapping`, `LO Mappings`, 2344411 second table `LO`) (`nep26-se-chem-it-b_facts.txt` header cells; dump `docs/evidence/dumps/nep26-se-chem-it-b_2343111_p16.txt` lines 12-19).
Row 0 raw lines: `0`, `Prerequisite`, prerequisite text lines, then hours (`01`) and CO (`--`) lines of row 0 (dump `..._2343111_p16.txt` lines 20-24). The Roman row number follows (`I`, line 25), then the name (`Laplace Transform`), then content lines, then hours `06` and CO `CO1` (lines 26-32). Rows 2-6 repeat `II`, name, content, hours, CO (`docs/evidence/dumps/nep26-se-chem-it-b_2344112_p41.txt`). Hours/CO may be separated by blank lines.
Method A (raw lines, `spikes/nep26_se_chem_it_mod.py`): scope starts at a `DETAILED SYLLABUS` heading or `Detailed Content` line, ends at first Text Books/References/Assessment line; a row starts at a line equal to the next expected number (`N`, `0N`, Roman) that is not followed by a CO/LO line or a dash cell. Method B: `find_tables()`, 5 columns, 4th header Hours/Hrs, 5th matches `(CO|LO)s?\s*Mappin\s*g?s?`; rows with empty first two cells merged into the previous row.
Coverage: token-sequence equality 9/12 (`nep26-se-chem-it-b_module_row.txt`, attempt 3 of 3, FINAL). Row count agreed 12/12 at attempt 2. Failures are hours cells (`01`, `06`) taken as row numbers (verbatim below). PARTIAL.

## Prerequisite row
Table row 0 in 8 of 12 module-table courses: 2343111, 2343112, 2343113, 2343114, 2344112, 2344113, 2344114, 2344411; absent in 2343115, 2344111, 2344115, 2343611 (`nep26-se-chem-it-b_prereq_row.txt`). The bare heading line `Prerequisite:` matches only in 2344411 (before its first table, page 55 line 4); the probe `Prerequisite:` finds 8 raw lines in the PDF (first hits p26 l115, p32 l103, p37 l0, `nep26-se-chem-it-b_facts.txt`), so 7 further lines carry the word with text on the same line or in another shape (shape UNKNOWN, not measured). Regexes `(?m)^0[ \t]*\n[ \t]*Prerequisites?\.?[ \t]*\n` (row) and `(?m)^Prerequisites?[ \t]*:[ \t]*$` (heading); the row regex agrees with the table oracle on 12/12. Courses with neither: 2343115, 2343116, 2344111, 2344115, 2343611. Row 0 is excluded from module counts and hours statistics.

## Self-learning markers (all spellings seen)
Regex `(?i)self[\s\-–]*(?:learning|study)[\s\-–]*(?:topics?)?\s*:?` over raw course text (`nep26-se-chem-it-b_selflearning.txt`). Spellings (whitespace collapsed): `Self-learning Topics:` (35), `Self-Learning Topics:`, `Self-learning topics:` (1), `Self-Study Topics:` (7), `Self Study Topics:` (1), `self-study topics` (7, in the Note row below the table, see below), `self- learning` / `self-learning topic` (sentence mentions). A marker can be split over two raw lines (`Self-Study ` / `Topics:`, `self- ` / `learning`). Markers start mid-cell, directly followed by the topics on the same raw line (dump `..._2343111_p16.txt` is before the first marker; see raw run listing in the evidence file).
Courses with raw hits: 9 of 13. Per-module markers (one per module) in theory courses: 2343111-2343114, 2344111, 2344112 (6 table hits each; 2344113: 4; 2343611: 6; 2344411: 5). No hits in 2343115, 2343116, 2344114, 2344115 (labs).
Note row: every IT theory course carries a table row `Note: No questions will be asked in the end-semester exam from self-study topics. However, students are encouraged to explore these topics for a better understanding of the subject.` (find_tables returns it as an extra row; 8 policy sentences in `nep26-se-chem-it-b_facts.txt`, e.g. 2343111 p18 line 3) and some courses add `A group of 4-6 students should be assigned a self-learning topic.` (2343111 p18 line 64). True number of self-learning items: UNKNOWN.

## Hours / CO tails
Hours cell `^\d{1,2}$` -> 78/78 module rows (`nep26-se-chem-it-b_hours_tail.txt`); padded `06` in all but 2344411's first table (`5`, `4`, `6`). CO/LO cell `^(?:(?:CO|LO|L0|L)?\s?\d+)(?:\s*,\s*(?:CO|LO|L0|L)?\s?\d+)*$` -> 78/78 (`nep26-se-chem-it-b_co_tail.txt`, attempt 2 of 3 shared with sub-family a). Shapes seen in the table oracle: `CO1`, `CO 1`, `CO1, CO2` (split over two raw lines `CO1,` / `CO2`), `LO1`, `LO 1`, `LO4, LO5`, and typos `L02, L03, L05`, `LO2, L03, L06` (2344114). Mapping word is `CO` for theory, `LO` for labs and mini-projects (header evidence in `nep26-se-chem-it-b_facts.txt`).

## Stop markers
First line starting with `Text Books`, `Textbooks`, `Text books`, `References`, `Reference Books`, or `Assessment`: regex `(?im)^\s*(?:Text\s*Books?|Textbooks?|References?|Reference\s+Books?|Assessment)\b.*$` -> 13/13 (`nep26-se-chem-it-b_stop_books.txt`; attempt 2: attempt 1 was case-sensitive and missed `Text books` in 2343114). Course end = next course header, or a cover page (pages 15, 35, 53, 62 per facts; 53 and 62 sit inside 2344115 and 2344411 ranges). Page 70 `Letter Grades and Grade Points`. Note: 2343114 and 2344411 use `Text books` / `Textbooks` spellings. In 2344411 a `Free Online Courses` table (`Module I` ... rows) sits between the first and second module tables (page 57).

## Watermarks / noise lines
- Draft watermark: none observed (`docs/evidence/signatures.csv` draft_watermark = 0).
- Bare page numbers: only 2 of 56 pages end with a bare number (`825` p14, `10` p59), so not a reliable footer (`nep26-se-chem-it-b_facts.txt`).
- Wingdings-style bullet U+F0B7 appears 158 times, `●` 23, U+F0A7 4, U+F0D8 7 over the PDF (`..._facts.txt`).
- Cover pages inside course ranges: 35, 53, 62.
- Whitespace-only lines are common padding; math glyphs in mathematical-italic Unicode (`𝑠𝑖𝑛(𝑎𝑡)`) yield R8 candidates.

## Numbering styles (Roman / arabic / 1.1 / 1.)
Roman `I`-`VI` in all module tables except the first table of 2344411 (arabic `1`-`6`) (`nep26-se-chem-it-b_facts.txt`). Sub-numbering `1.1`, `2.1`, ... inside content of 2344111 (R6 example `1.1 Characteristic Equation`). Lab content in 2343115 contains numbered experiment sentences inside module cells (R5 examples `Implement Merge sort and Quicksort ...` in `nep26-se-chem-it-b_topic_validity.txt`).

## Topic separators
Commas, `;`, colons after sub-headings (`Properties of Laplace Transform: Linearity, ...`, `Languages: Alphabets and Strings.`), `&`, `and`, full stops followed by a capital, bullets `●` / U+F0B7 in mini-project content, lettered items `a)`/`b)` and `(i)`...`(xi)` in lab content (2344114). Parenthetical notes `(without proof)`, `(up to 2nd order differential equation)`.

## Known oddities
1. Row 0 hours/CO cells (`01`, `--`) precede the first Roman row number and can be read as a module number (cause of module_row failures).
2. Module name can wrap onto an extra table row across a page break: 2343113 module I name `and Applications` (empty first cell).
3. `Note:` row appended to the module table in every theory course (find_tables returns it as a row).
4. Header word variants: `CO Mapping`, `CO Mappings`, `LO Mapping(s)`; `Module` vs `Name of Module`; `Suggested list of Practical` (2343115).
5. Typos: `Synchronizatio`/`n` split (2344112 module III name), `Mmultithreading`, `L02`/`L03` letter O/zero.
6. 2344411 has two module tables (CO then LO) and a `Free Online Courses` table between them; 2343611 spans pages 63-69 with many content pages (capstone guidelines).
7. 2344115 range reaches page 54 (start of 2344411): segmentation by header lines is mandatory.
8. Lab 2344114 content is procedural (commands, `Write a shell script ...`, R5 candidates); 2343115 lab content lists numbered experiments inside modules.
9. Four overview-listed courses (2993511, 2993512, 2994511, 2994512) have no detail pages.

## Exact regexes with measured coverage (each links to docs/evidence/regex_runs/<file>)
| name | regex (also in `spikes/nep26_se_chem_it_runs.py`) | matched/total | attempts | file |
|---|---|---|---|---|
| detect (4 regexes) | see Detection | 2/2 positives, 0 false positives / 25 PDFs | 1 | nep26-se-chem-it-b_detect_all_pdfs.txt |
| course_header | `(?m)^Course\s*\nCode\s*\n(?:.*\n){0,38}?[ \t]*(\d{7})[ \t]*\n` | 13/17 (4 absent courses) | 1 | nep26-se-chem-it-b_course_header.txt |
| title_end | `^\s*(?:\d{1,2}\|--\|–\|\d\*\+\d)\s*$` | 13/13 | 2 | nep26-se-chem-it-b_title_wrap.txt |
| module_row (method A vs B token sequence) | sequential number rule | 9/12 PARTIAL | 3 (limit) | nep26-se-chem-it-b_module_row.txt |
| prereq_row | `(?m)^0[ \t]*\n[ \t]*Prerequisites?\.?[ \t]*\n` | 12/12 | 1 | nep26-se-chem-it-b_prereq_row.txt |
| prereq_heading | `(?m)^Prerequisites?[ \t]*:[ \t]*$` | no oracle (only 2344411 hits) | 1 | same file |
| hours_cell | `^\d{1,2}$` | 78/78 | 1 | nep26-se-chem-it-b_hours_tail.txt |
| co_cell | `^(?:(?:CO\|LO\|L0\|L)?\s?\d+)(?:\s*,\s*(?:CO\|LO\|L0\|L)?\s?\d+)*$` | 78/78 | 2 | nep26-se-chem-it-b_co_tail.txt |
| selflearning | `(?i)self[\s\-–]*(?:learning\|study)[\s\-–]*(?:topics?)?\s*:?` | 9/13 courses have a hit; no ground truth | 1 | nep26-se-chem-it-b_selflearning.txt |
| stop_books | `(?im)^\s*(?:Text\s*Books?\|Textbooks?\|References?\|Reference\s+Books?\|Assessment)\b.*$` | 13/13 | 2 | nep26-se-chem-it-b_stop_books.txt |
(`\|` stands for the alternation bar inside table cells.)

## Failures (verbatim, per regex, per attempt 1-3)
- course_header attempt 1 (no refinement possible, the courses are absent): 
  - `code 2993511: no header match on any detail page; appears only on overview pages [11, 12, 13, 14]`
  - `code 2993512: no header match on any detail page; appears only on overview pages [11, 12, 13, 14]`
  - `code 2994511: no header match on any detail page; appears only on overview pages [11, 12, 13, 14]`
  - `code 2994512: no header match on any detail page; appears only on overview pages [11, 12, 13, 14]`
- module_row attempt 1: `2343115: sequential raw-line rows=None, table-oracle rows=6` (heading `Suggested list of Practical`); `2344411: sequential raw-line rows=6, table-oracle rows=12` (two tables) -> fixed by attempt 2 (row count 12/12).
- module_row attempt 3 (FINAL, verbatim, token check):
  - `2343112: raw-line rows=6 tokens=['01', 'II', 'III', 'IV', 'V', 'VI'] | table-oracle rows=6 tokens=['I', 'II', 'III', 'IV', 'V', 'VI']`
  - `2344112: raw-line rows=6 tokens=['I', 'II', 'III', 'IV', 'V', '06'] | table-oracle rows=6 tokens=['I', 'II', 'III', 'IV', 'V', 'VI']`
  - `2344411: raw-line rows=12 tokens=['1', '2', '3', '4', '5', '6', 'I', 'II', 'III', 'IV', 'V', '06'] | table-oracle rows=12 tokens=['1', '2', '3', '4', '5', '6', 'I', 'II', 'III', 'IV', 'V', 'VI']`
  Cause: an hours cell equal to the expected padded number, with blank lines before the CO line, is read as the row number. Not refined further (3-attempt limit).
- title_wrap attempt 1: `2344411 page 54: table1='Mini-Project - Programming Paradigm' | table2='Mini-Project'` -> fixed in attempt 2.
- stop_books attempt 1: `2343114 pages 26-28: no Text Books/Textbooks heading line` -> fixed in attempt 2 (case-insensitive and broader).
- co_cell attempt 1 had no failures on this PDF (the 6 failures were in sub-family a).
Attempt histories are appended at the end of each regex_runs file.

## Topic validity census (violations by rule id, total topics)
Naive splitter (not a parser; `spikes/nep26_se_chem_it_runs.py`) over the 12 courses with a module table; module name excluded, self-learning text cut off: total 986 candidate topics, 234 violate at least one rule. By rule: R1 116, R2 63, R3 120, R4 5, R5 20, R6 6, R7 0, R8 13 (`docs/evidence/regex_runs/nep26-se-chem-it-b_topic_validity.txt`, 3 examples per rule). Candidates per course range from 33 (2343115) to 246 (2343611); 2343611 and 2344114 dominate because their content is long procedural text. R5 (procedural) hits come from lab/mini-project cells (`Implement ...`).

## Golden courses (5, DRAFT) and how they were drafted
The 5 golden courses of the pair are split 2 (sub-family a) / 3 (this sub-family): `tests/golden/nep26-se-chem-it-b/2343114.json` (Automata Theory, normal theory, 40 topics), `tests/golden/nep26-se-chem-it-b/2344112.json` (Operating System, theory, 89 topics), `tests/golden/nep26-se-chem-it-b/2344114.json` (Unix Lab, lab with module table, 20 topics). Odd theory course of this PDF (2343113 with the wrapped module name, 2344411 with two tables) was NOT drafted.
Drafting: module table cells printed by `spikes/nep26_se_chem_it_tables.py` (method B) for these courses were read by hand and split into atomic noun phrases; sub-headings with colons (`Languages:`), generic items, `Installation of Unix Operating System` (R5), shell-script exercises and trailing hours/CO removed; self-learning topics EXCLUDED (policy UNKNOWN); the broken name `Process Synchronizatio n` was repaired to `Process Synchronization`; the lab topics name command categories rather than the individual commands. All golden topics pass `validate()` (0 violations). Every file is `DRAFT - needs human sign-off`; nothing is verified. Dump samples for this sub-family: `docs/evidence/dumps/nep26-se-chem-it-b_2344112_p41.txt` (normal theory), `..._2343111_p16.txt` (odd: row 0 tail + Roman row), `..._2344114_p48.txt` (lab).

## UNKNOWN items (also copied to docs/open_questions.md)
- Name vs content boundary from raw line order.
- Self-learning items as Topics or not; true number of self-learning items.
- Syllabus location of 2993511, 2993512, 2994511, 2994512 for IT.
- Topics for lab 2343116 (no module table); which of the two 2344411 tables defines Topics.
- Row-merge rule for the wrapped module name in 2343113 is a spike heuristic only.
- Scheme name: cover says NEP 2020; the folder says `2019-scheme`.
