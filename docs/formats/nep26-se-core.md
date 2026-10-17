# Format: nep26-se-core
Status: PARTIAL   (hypothesis from `docs/evidence/signatures.csv` CONFIRMED as one family; PARTIAL because prerequisite-row coverage is 65/77, CO/LO-tail coverage is 451/462, and Name extraction from plain `get_text()` order is heuristic. All other regexes reach full coverage, see "Exact regexes". Spike code: `spikes/nep26-se-core_*.py`, not product code.)

Sub-family note (task asked to name sub-families if the PDFs split): the six PDFs differ only in where the course header table block lands in `get_text()` line order. Names used here: `nep26-se-core-a` = A-I-AI-DS, AI-DS, AI-ML, Computer-Engineering (header block at the top of the course's first page: floating in 0/17 courses per PDF); `nep26-se-core-b` = Computer-Science-Engineering, Data-Science (header block floats inside the module table in 8/17 courses per PDF, e.g. line 121 of page 22). Evidence: `docs/evidence/regex_runs/nep26-se-core_header_block_position.txt`. One parser handles both if it removes the header block wherever it appears (done in `spikes/nep26-se-core_extract.py strip_header_blocks`), so this doc documents both together and marks differences with (a)/(b). Course contents are otherwise textually the same across the six PDFs (same self-learning counts, `docs/evidence/regex_runs/nep26-se-core_self_marker_spellings.txt`).

## PDFs in this family (path, pages, evidence file)
All under `data/raw/2019-scheme/` (folder name is a misnomer; text says "As Per NEP 2020" and "With Effect from 2025-2026", `docs/evidence/regex_runs/nep26-se-core_watermark.txt` noise list). Pages from `docs/evidence/signatures.csv`. Each PDF yields 17 courses (`docs/evidence/regex_runs/nep26-se-core_course_start_attempt2.txt`: 102/102 codes), 102 courses total.

| PDF | pages | sub-family |
|---|---|---|
| A-I-AI-DS/6.41N-A-I-AI-DS-Sem-III-IV.pdf | 72 | a |
| AI-DS/6.20N-B.E.-AI-DS.-Sem-III-IV.pdf | 82 | a |
| AI-ML/6.21-N-B.E.-AI-ML-sem-III-IV.pdf | 72 | a |
| Computer-Engineering/6.24-N-B.E.-Computer-Engineering-Sem-III-IV.pdf | 72 | a |
| Computer-Science-Engineering/6.54-N-B.E-Computer-Science-EngineeringSem-III-IV.pdf | 72 | b |
| Data-Science/6.39-N-B.E.-Data-Science-Sem-III-IV.pdf | 72 | b |

Document layout (first non-blank line of every page, `docs/evidence/regex_runs/nep26-se-core_page_first_lines.txt`): early pages are cover letter/preamble (`Copy forwarded for information...`, `AC – 20/5/2025`, `University of Mumbai`, `Preamble`), then program-structure tables (`Program Structure for Second Year of ...`, 7-digit codes repeated, `docs/evidence/regex_runs/nep26-se-core_structure_vs_detail_codes.txt`), then one course per 2-6 pages from page 16 (17 in AI-DS); the last page holds `Letter Grades and Grade Points` and belongs to the last course's page range (`nep26-se-core_misc_census.txt`).
Course kinds per PDF (17 slots): 77/102 courses have a module table; no module table: Computer Organization & Architecture Lab x6, Database Management System Lab x6, Operating System Lab x6, Mini Project x6, Analysis of Algorithm Lab x1 (AI-DS only) (`nep26-se-core_misc_census.txt`).

## Detection (regex + coverage matched/total)
PDF-level rule: count of `^\s*Self-learning\s+Topics?\s*:` >= 40 AND count of `^\s*Self-Study\s*:` >= 2 AND count of `^\d{7}\s*$` >= 60. Coverage 6/6 family PDFs, 0 false positives among the 19 other PDFs in data/raw (`docs/evidence/regex_runs/nep26-se-core_detect.txt`). Caveat: thresholds are fitted to these PDFs; "As per NEP 2020" is NOT discriminating (it appears in other PDFs too, same file).

## Course header pattern
Table in line order: `Course `, `Code `, `Course Name `, `Teaching Scheme `, `(Contact Hours) `, `Credits Assigned `, `Theory `, `Pract. `, `Tut. `, `Theory `, `Pract. `, `Tut. `, `Total `, then the 7-digit code line, then title lines, then 7 value lines (`2 `, `- `, `1 `...). Second table (examination scheme) repeats the code and title and then numeric marks (`docs/evidence/dumps/nep26-se-core_computer-engineering-2113111-normal-theory_p17.txt` is the syllabus page; the header lines are listed in `nep26-se-core_course_start_attempt1.txt` failures and in the page-22/27 samples quoted below).
Start-of-course regex: line `^\d{7}\s*$` whose previous line stripped ends with `Total` and with `Credits Assigned` within 14 lines before; 102/102. Variants that broke attempt 1 (previous line exactly `Total`): split cells such as `Theor`/`y`, `Tutorial Total `; 13 courses missed (`nep26-se-core_course_start_attempt1.txt`). Code first-seen page >= 16 (structure tables end by page 15).
Header block can be preceded by Course Objectives text (TCS, index 44-45, sub-family a) or float anywhere in the page (b) (`nep26-se-core_header_block_position.txt`). A page-level course boundary still holds (header table is on the course's first page in all 102 cases).

## Title wrapping
Title = lines after the code line joined by a space until the first line matching `^[\d\-–]+\s*$` (first credit value). Raw lines carry a trailing space, so a joined title contains double spaces (`'Mathematics for  Computer  Engineering '` etc., listed in `docs/evidence/regex_runs/nep26-se-core_titles_hours_words.txt`); strip each line or collapse whitespace. Check: the same rule applied to the examination table gives the same title in 102/102 courses (alphanumerics compared case-insensitively).

## Module row pattern
Row cells are flattened column by column, not row by row, so module number, name and content interleave (`...normal-theory_p17.txt`: the first module content items `1. Characteristic Equation, ...` appear BEFORE the `I` line, and name words `Linear / Algebra / (Theory of / Matrices)` appear after it, split by the content item `verification and reduction of higher degree`).
- Roman style: line `^\s*(I|II|III|IV|V|VI|VII|VIII)\s*$` (71/77 module-table courses). Variant: numeral shares the line with the first name word (`VI Special-purpose ` in Operating System, page 45 line 0 of the AI-DS PDF); accepted only when it is the next numeral in sequence, regex `^\s*(II|III|IV|V|VI|VII|VIII)\s+(?=[A-Z][a-z])`.
- Arabic style (Computer Organization & Architecture, 6/77 courses, header `DETAIL SYLLABUS:`, columns `Name of the Module | Topics | Hrs | CO Mapping`): `^\s*[1-9]\s*$` immediately after a CO tail/hours/header line and not followed by a pure number. Module `4` sits at page start (`...odd-theory-arabic-modules_p24.txt` for modules 1-3; page 25 line 0 is `4 `).
- Unit style (Environmental Science for Engineers, `Unit | Name | Topic Name | Topic Description | Hours | LO Mapping`, 6/77) uses roman units.
- Computational Theory: no `DETAILED SYLLABUS` line (`nep26-se-core_syllabus_header_attempt1.txt` failures, 6 courses); roman numerals `I`, `II` appear before the `Name of Module` column header; each module has numbered sub-rows (`1`, `2`) with own hours and CO (raw sample: `docs/evidence/regex_runs/nep26-se-core_tcs_sample_p33_lines104-163.txt`, Computer-Engineering PDF page 33).
Combined coverage: markers exactly I..VI (or 1..6) in 77/77 module-table courses after 3 attempts (`nep26-se-core_module_row.txt`, attempts in `nep26-se-core_module_row_attempts.txt`). "6 modules" is an observed assumption (UNKNOWN, see below).
Column header words seen (`nep26-se-core_misc_census.txt`): `Name of Module|Detailed Content|Hours|CO` x24; `Module|Detailed Content|Hours|LO` x22; `Module|Detailed Content|Hours|CO` x12; `Name of the Module|Topics|Hrs|CO` x6; `Unit|Topic Description|Hours|LO` x6; 4+2+1 courses where the column words are outside the first 40 region lines (TCS: `Name of Module`/`Hrs`/`Mapping` far down).

## Prerequisite row
Row `0` / `Prerequisite` / text, where `0 ` and `Prerequisite ` are separate lines (`...normal-theory_p17.txt` lines 11-12 region). Excluded from topics. Spellings (`nep26-se-core_misc_census.txt`): `Prerequisite ` x54 (row), `Prerequisite: <text>` x24 (header-level line, e.g. `Prerequisite: Data structure concepts`), `Pre-requisite. ` x6 (COA header), `No perquisites` x6 (Design Thinking, typo in source). Coverage over 77 module-table courses: 65/77 with attempt 3 (any Prerequisite-like line); 12 failures are Operating System x6 and Environmental Science x6 which contain no requisite-like text on any of their pages (`nep26-se-core_prereq_row_attempt3.txt`, verified with the broader regex `(?i)re-?\s?quisite|pre-?req|perquis|prior knowledge`). Attempt 1 (strict `0` then `Prerequisite`) 46/77, attempt 2 59/77 (files `..._attempt1/2.txt`).

## Self-learning markers (all spellings seen)
Anchored at line start, all six PDFs (`nep26-se-core_self_marker_spellings.txt`): `Self-learning Topics:` (48-50 per PDF), bare `Self-learning ` with `Topics:` on the next line (3-5 per PDF), `Self-Study :` / `Self-Study:` (2 per PDF, only in Computer Organization & Architecture). Regex `(?i)^\s*Self[\s\-]*(learning|study)\b`: 330 anchored lines; the 30 other lines containing the words are mid-sentence prose in course objectives/outcomes/mini-project text, listed verbatim in `nep26-se-core_self_marker.txt` (all begin with text other than the marker). The marker introduces text that runs to the end of the module cell (before hours/CO tail), and can wrap over many lines (`...p17.txt`).

## Hours / CO tail patterns
After the content of a module: line `^\s*\d{1,2}\s*$` (hours; `5`, `08`, `4`) then tail line. Tail regex `^\s*((CO|LO)\s?\.?\s?\d|L\d)(\s*[,&]\s*((CO|LO|L)\s?\.?\s?)?\d)*\s*,?\s*$` matches `CO1`, `CO 1`, `LO3`, `L2, L3,` (Bloom-style tail wrapped over lines `L4, L5`). Coverage of module blocks containing a tail: 451/462 (11 failures: Discrete Structures module II in five PDFs, Computational Theory module I in three PDFs, Analysis of Algorithm Lab modules I-III in A-I-AI-DS; verbatim in `nep26-se-core_co_lo_tail_attempt2.txt`). The hours+tail pair regex is identical in coverage (`nep26-se-core_hours_tail_pair.txt`). Column header words `Hours`/`Hrs` (counts per PDF in `nep26-se-core_titles_hours_words.txt`) and the tail column `CO Mapping`/`LO Mapping`/`Mapping`.
Attempt 1 of the tail regex (`CO|LO` only, no `L\d`) missed the Bloom-style tails in the elective courses; its output was not saved separately (stated in the evidence file).

## Stop markers
End of the module table = first following line matching `^\s*(Text\s*Books?|Reference\s*Books?|Textbooks?|Books|Online\s+References?|Suggested\s+List\s+of\s+[Ee]xperiments?|List\s+of\s+Experiments?)\s*[:.]?\s*$|^\s*(Assessment|Term\s+Work)\s*:`. 77/77 module-table courses (`nep26-se-core_stop_marker.txt`). Attempt 1 used `Assessment` as a bare prefix and cut AI-DS 2993511 at the topic line `Assessment and Management` (`nep26-se-core_stop_marker_attempts.txt`). Lab list start `Suggested List of Experiments:` (page 30 line 85 of the Computer-Engineering PDF; `...2113116-lab_p30.txt`).

## Watermarks / noise lines
No DRAFT/watermark text: regex `(?i)draft|watermark|confidential|specimen` matched 0 of 36546 lines (`nep26-se-core_watermark.txt`). Noise: `UNIVERSITY OF MUMBAI (With Effect from 2025-2026)` on program-structure pages and cover, `AC – 20/5/2025`, `Item No. – 6.xx (N)` on the cover page (same file lists pdf/page counts). No running header/footer line on detail pages was identified; recurring lines are the course header-table words (`Course`, `Code`, ... as in `nep26-se-core_course_start_attempt1.txt` context and the p17 dump). Whether other recurring noise exists on other pages: UNKNOWN (not exhaustively checked). Blank single-space lines are common between cells (`...p17.txt`).

## Numbering styles (Roman / arabic / 1.1 / 1.)
Modules: Roman (71/77) or arabic (6/77, COA). Content items inside a module: `1.  Characteristic` style prefixes occur in the p17 dump (Mathematics) and are absent in the p24 dump (COA); how many courses use them: UNKNOWN (not counted). No `1.1`-style numbering (0 hits, `nep26-se-core_misc_census.txt`; grade-point ranges excluded). Computational Theory sub-rows numbered `1`,`2` on separate lines with own hours.

## Topic separators
Topics inside module content are separated by commas, full stops, and colon-introduced lists (`Backtracking: N-queen problem, Sum of subsets`); `A and B` is not a separator (undecided, UNKNOWN). Hyphenated word breaks at line ends occur (`non- diagonalizable`); words in narrow name columns wrap one word per line (`Number / Systems: / Binary. / Octal / and ...` in `...odd-theory-arabic-modules_p24.txt`).

## Known oddities
- Column-wise flattening: module name and content interleave; first module content may precede the first numeral (see Module row).
- Floating header table block inside module rows in sub-family b (`nep26-se-core_header_block_position.txt`).
- Same course code can appear in program-structure pages (11-14) and again in details; structure-only codes xxx3311/xxx4311 exist (2 per PDF) with no detail page; CSE/DS list 2493116/2173116 and 2993512 only in details (`nep26-se-core_structure_vs_detail_codes.txt`).
- AI-DS: Analysis of Algorithm Lab (2013115) has no module table (others do), 82 pages (`nep26-se-core_misc_census.txt`).
- Header spellings `DETAIL SYLLABUS:` (COA, `...p24.txt`) and `DETAILED SYLLABUS:` (`...p17.txt`); handled by `^\s*DETAIL(ED)?\s+SYLLABUS\s*:?\s*$`.
- Typo kept verbatim in the source: `No perquisites` (`nep26-se-core_misc_census.txt`); module name `Basics Concepts and Regular Languages` in Computational Theory is as printed (`nep26-se-core_tcs_sample_p33_lines104-163.txt`).
- Computational Theory has no `DETAILED SYLLABUS` line (6/6) and sub-rows with own hours.

## Exact regexes with measured coverage (each links to docs/evidence/regex_runs/<file>)
All commands: `PYTHONIOENCODING=utf-8 python spikes/nep26-se-core_regex_runs.py` (plus `spikes/nep26-se-core_selfspell.py`, `..._hdrpos.py`, `..._misc.py` for the census files). Denominators are stated in each file.

| name | regex | matched/total | attempts | file |
|---|---|---|---|---|
| detect | see Detection (3 counts) | 6/6 PDFs, 0 false positives in 19 others | 1 | nep26-se-core_detect.txt |
| course_start | `^\d{7}\s*$` + prev line endswith `Total` + `Credits Assigned` within 14 | 102/102 | 2 (89/102 then 102/102) | nep26-se-core_course_start_attempt1.txt, _attempt2.txt |
| title_wrap | lines after code until `^[\d\-–]+\s*$` | 102/102 | 1 | nep26-se-core_title_wrap.txt |
| syllabus_header | `^\s*DETAIL(ED)?\s+SYLLABUS\s*:?\s*$` | 71/77 | 1 | nep26-se-core_syllabus_header_attempt1.txt |
| syllabus_header (+Name of Module) | `^\s*(DETAIL(ED)?\s+SYLLABUS\s*:?\|Name of Module)\s*$` | 77/77 (detection signal only; for TCS it comes after modules I and II) | 2 | nep26-se-core_syllabus_header_attempt2.txt |
| module_row | roman `^\s*(I\|II\|...\|VIII)\s*$` + `ROMAN2` + arabic rule | 77/77 | 3 (71, 73, 77) | nep26-se-core_module_row.txt, _attempts.txt |
| prereq_row | any Prerequisite-like line | 65/77 (12 verified absences) PARTIAL | 3 (46, 59, 65) | nep26-se-core_prereq_row_attempt1.txt, _2, _3 |
| self_marker | `(?i)^\s*Self[\s\-]*(learning\|study)\b` | 330/360 lines (30 prose) | 1 | nep26-se-core_self_marker.txt |
| co_lo_tail | see Hours / CO tail | 451/462 PARTIAL | 2 | nep26-se-core_co_lo_tail_attempt2.txt |
| hours_tail_pair | digits line + tail line | 451/462 PARTIAL | 1 | nep26-se-core_hours_tail_pair.txt |
| stop_marker | see Stop markers | 77/77 | 2 | nep26-se-core_stop_marker.txt, _attempts.txt |
| watermark | `(?i)draft\|watermark\|confidential\|specimen` | 0 matches (none present) | 1 | nep26-se-core_watermark.txt |

## Failures (verbatim, per regex, per attempt 1-3)
Verbatim failure lines are in the evidence files above; summary (counts identical to the files):
- course_start attempt 1: 13 failures (e.g. `A-I-AI-DS ... code 2483115 first seen page 27 not detected`); attempt 2: 0.
- syllabus_header attempt 1: 6 failures, all `Computational Theory` (2484111, 2014111, 2024111, 2114111, 2494111, 2174111): no DETAILED SYLLABUS line. Attempt 2: 0.
- module_row attempt 1: 6 failures; attempt 2: 4 failures (Operating System `VI` numeral merged with name x3 PDFs, Entrepreneurship Development AI-DS truncated by stop regex); attempt 3: 0 (verbatim in `nep26-se-core_module_row_attempts.txt`).
- prereq_row attempt 3 (final): 12 failures, Operating System and Environmental Science in all six PDFs (verbatim in `nep26-se-core_prereq_row_attempt3.txt`).
- co_lo_tail attempt 2 (final): 11 failures (see Hours / CO tail; verbatim in the file).
- self_marker: 30 non-matching lines are prose, listed verbatim.

## Topic validity census (violations by rule id, total topics)
Extractor: `spikes/nep26-se-core_extract.py extract()` (heuristic; self-learning text excluded; module names via short-line heuristic, topics split on `, ; : .` outside parentheses and on `N.` item numbers); validator `spikes/topic_validity.py`. 77 module-table courses; file `docs/evidence/regex_runs/nep26-se-core_topic_validity.txt`.
Total topics 4449; topics with >= 1 violation 252 (5.7%). By rule: R1 word count 110, R2 length 37, R3 colon/semicolon 6, R4 generic heading 108, R6 leading numbering 29; R5, R7, R8 0. Most R4/R1 hits come from splitting at `:` and `.` (heading words such as `Introduction`) and from tail words of name interleaving; the census is of the heuristic extractor, not of the golden files. Goldens: 2 violations, both R6 false positives (`8086 processor architecture`, `15 puzzle problem`; recorded in open_questions.md).

## Golden courses (5, DRAFT) and how they were drafted
`tests/golden/nep26-se-core/{2113111,2113114,2113116,2114111}.json` (Computer-Engineering PDF) and `2493113.json` (Computer-Science-Engineering PDF, sub-family b, header block floating on page 22). Drafted by reading each course's text from the PDF (printed per course, never whole PDF), applying topic validity rules, excluding the module 0 prerequisite row and self-learning/self-study text, splitting "A and B" bundles when the syllabus lists separate concepts. All `status: DRAFT - needs human sign-off`. Roles: 2113111 normal theory; 2113114 odd theory (arabic modules, `Self-Study`, `DETAIL SYLLABUS:`); 2113116 lab (`modules: []`, experiment list not modelled, UNKNOWN); 2114111 odd theory (no header, sub-rows); 2493113 floating-header-block example. Dumps (raw, <= 60 lines, unedited): `docs/evidence/dumps/nep26-se-core_computer-engineering-2113111-normal-theory_p17.txt` (60), `..._2113114-odd-theory-arabic-modules_p24.txt` (55), `..._2113116-lab_p30.txt` (31).

## UNKNOWN items (also copied to docs/open_questions.md)
Self-learning text as topics or not; whether labs yield topics; whether every course has exactly 6 modules; coordinate-based parsing allowed or not (module Name heuristic); hours values needed or not; R6 digit-leading topics; origin of structure-only codes (xxx3311/xxx4311) and CSE/DS 116 code; sub-row headings in Computational Theory as topics; splitting of "A and B" bundles; trailing grade-table pages in the last course; AI-DS differences. See lines prefixed `nep26-se-core:` in `docs/open_questions.md`.
