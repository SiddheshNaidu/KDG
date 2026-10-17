# Format: nep2425-fe
Status: PARTIAL (hypothesis "one family" REFUTED: 4 sub-families `nep2425-fe-a`..`-d`; module-name wrapping and missing text are not regex-solvable; see Failures)

Evidence root: `docs/evidence/`. All PDFs are under `data/raw/2024-25-scheme/FE/` and are common FE (Sem I) syllabi. Raw page text was read with PyMuPDF `page.get_text()` split on `\n`; reading spikes: `spikes/nep2425-fe_show.py`, `spikes/nep2425-fe_scan.py`, `spikes/nep2425-fe_probe.py`.

## PDFs in this family (path, pages, evidence file)
| PDF | pages | courses inside (text order) | sub-family | evidence |
|---|---|---|---|---|
| `02 Syllabus.pdf` | 5 | ESC102 theory (p1-2), ESL102 lab (p3-4), AEC101 STUB (p5, header rows + "Rationale" only, no modules) | a | `regex_runs/nep2425-fe_detailed_syllabus_header.txt`, dump `dumps/nep2425-fe_ESL102_p4.txt` |
| `Applied Chemistry syllabus 2024-25.pdf` | 6 | BSC103 theory (p1-4; p1 starts mid-course with lab rows 10-11 of BSL102 and the BSC103 tables), BSL102 lab (p4-6) | b | `dumps/nep2425-fe_BSC103_p2.txt` |
| `NEW EM SYLLABUS 2024-25.pdf` | 5 | ESC101 theory (p1-3), ESL101 lab (p3-5; experiment list absent from text) | b | `dumps/nep2425-fe_ESC101_p2.txt` |
| `Professional_Comm._Ethics_Theory_Sem_I 2024-25.pdf` | 6 | AEC101 theory (p1-5), p6 holds "Prepared by" + 5 images | c | `regex_runs/nep2425-fe_module_arabic_padded.txt` |
| `Syllabus-C Prog.pdf` | 5 | VSEC102 "C Programming" (lab-only course: Pract 2*+2, no Theory credits; has a module table with LO mapping) | d | `regex_runs/nep2425-fe_module_arabic_unpadded.txt` |

Courses with a module table: 5 (ESC102, BSC103, ESC101, AEC101, VSEC102). Lab courses with an experiment list: ESL102 (13 rows), BSL102 (11 rows), VSEC102 (12 rows, its own table); ESL101 has the label only (UNKNOWN rows). Only 5 golden courses exist, which equals the number of module-bearing courses: all of them are drafted.

Answer to "Applied Chemistry holds 2 course headers": confirmed, BSC103 (theory) + BSL102 (lab) (`regex_runs/nep2425-fe_course_code_line.txt`, 9/9 code occurrences including the stub). Same pattern in the other PDFs (theory + lab pair); `02 Syllabus.pdf` additionally contains the AEC101 stub.

## Detection (regex + coverage matched/total)
`regex_runs/nep2425-fe_detection.txt` (command and regex recorded there): FE course-code line (`ESC|ESL|BSC|BSL|AEC|VSEC|VSEL|VEC` + `1xx`) AND `IAT-I` AND page count <= 8. Coverage 5/5 family PDFs, 0 false positives over the other 20 PDFs under `data/raw`. Attempt 1 (without the page-count clause) gave 5/5 but 6 false positives (AIML, CSE-AIML, DS, EXTC, IT, Mechanical PDFs in `data/raw/2019-scheme/` that embed the same FE codes, 60 code lines each); the page-count clause is a crude proxy, a real detector should use per-course layout instead (UNKNOWN, see open questions). The folder name `2019-scheme` for those big PDFs is misleading (they contain "NEP" 15 times in DS; not studied here).
The word "NEP" occurs 0 times in all 5 FE PDFs (`docs/evidence/census.csv` and my count); scheme membership rests on the owner statement only.

## Course header pattern
The course code sits on its own raw line inside the Teaching Scheme / Examination Scheme tables, not in a header paragraph: `^[ \t]*([A-Z]{3,4})[ ]?(\d{3})[ \t]*$`, 9/9 (`regex_runs/nep2425-fe_course_code_line.txt`). Spellings seen: `ESC102`, `AEC101`, `AEC 101` (with space, Professional_Comm pdf), `VSEC102`. In `Applied Chemistry` the exam-table row is `BSC103 Applied Chemistry` (code and title on one line) while the teaching table has `BSC103` alone; in `Syllabus-C Prog.pdf` one row is `VSEC102   C Programming`. The title is on the lines after the code (see below). The word-level "Course Code" table header is itself split into raw lines (`Course `, `Code `, `Course Name `, ...).

## Title wrapping
Course titles wrap over 1-4 raw lines, e.g. `Basic Electrical and ` / `Electronics ` / `Engineering ` (ESC102, `02 Syllabus.pdf` p1 lines 34-36), `Professional ` / `Communication and ` / `Ethics ` (AEC101 stub, p5 lines 30-32). Module names wrap too and can break mid-word without a hyphen: `Introductio` / `n to ` / `Polymers ` (BSC103 p3 lines 8-10), `developmen` / `t ` (BSC103), `Fundament` / `als of   C-` / `Programmi` / `ng ` (VSEC102 p2 lines 7-10), `Paramete` / `r ` (VSEC102). Joining wrapped fragments needs a no-space join when the previous fragment is a word-fragment; no regex rule is established for this (UNKNOWN, open questions).

## Module row pattern
The detailed syllabus is a table linearised cell-by-cell. Region = line `^\s*DETAILED SYLLABUS` .. first stop marker (`regex_runs/nep2425-fe_detailed_syllabus_header.txt` 5/6, `nep2425-fe_stop_marker.txt` 5/6; the single failure in both is the AEC101 stub, which has no module table).
- Sub-family a (ESC102): raw order is `Roman`, `Sr no (01..06)`, content lines (module name is the heading before ":" inside the content, e.g. `DC Circuits: (Only independent sources) ...`), `Hours`, `CO`. No separate name lines. Sr numbers are indented with spaces on p1 (`           01 `) but not on p2 (`03 `), and hour values collide with Sr values (hours `04` for III, Sr `04` for IV), so Sr numbers are NOT usable; use Roman rows.
- Sub-family b (ESC101, BSC103): `Roman`, wrapped module-name lines, content lines, `Hours`, `CO`. No Sr number lines.
- Sub-family c (AEC101): zero-padded arabic Sr (`01`..`06`) then wrapped name lines, content, then `Hours`, `CO n` (CO with a space, `CO 1`; one row is `CO3`). Hours/CO may come before the next Sr number or (module 2) after blank lines.
- Sub-family d (VSEC102): unpadded Sr (`1`..`6`), wrapped name fragments, content, then blanks, `Hours`, `LO n`.
Regexes (all in `docs/evidence/regex_runs/`):
- Roman row `^[ \t]*(I|II|III|IV|V|VI)[ \t]*$` (re.M, region scope): 3/3 (ESC102, BSC103, ESC101), `nep2425-fe_module_roman.txt`.
- AEC101 padded Sr row, attempt 2: `^[ \t]*0([1-6])[ \t]*\n(?![ \t]*(?:\d|CO|LO||\n))`: 1/1; attempt 1 naive `^[ \t]*0([1-6])[ \t]*$` found 10 matches for 6 modules (hours 02 collide) = FAIL, kept verbatim in `nep2425-fe_module_arabic_padded.txt`.
- VSEC102 unpadded Sr row `^[ \t]*([1-6])[ \t]*$` (region scope): 1/1, `nep2425-fe_module_arabic_unpadded.txt`.
Each is measured on the courses of its sub-family only (denominators 3, 1, 1): the courses count is tiny, the measure is "exactly 6 modules found, in order".

## Prerequisite row
Two different forms (`nep2425-fe_prerequisite_label.txt` 3/5; `nep2425-fe_prerequisite_row_zero.txt` 2/2):
- Table-row form (ESC102 p1 lines 71-72, ESC101 p2 lines 14-15): raw lines `0 ` then `Prerequisite ` then content; regex `^\s*0\s*\n\s*Prerequisite` (re.M) 2/2. ESC102's row has no hours/CO tail; ESC101's row has tail `01`, `CO1`. This row appears BEFORE module I and must not be counted as a module.
- Labelled-list form (BSC103 p2 line 16 `Prerequisite:  ` followed by `1) ...` items; BSL102 p6 line 6): outside the module table.
- Absent: AEC101 and VSEC102 (no `Prerequisite` line anywhere) - observed absence, listed as failures of `^\s*Prerequisite\b`.

## Self-learning markers (all spellings seen)
None. `(?i)self[\s-]*(learning|study)`: 0 hits in all 5 PDFs (`nep2425-fe_self_learning_marker.txt`). census.csv also has self_learning=0 for all five.

## Hours / CO tail patterns
`^[ \t]*(\d{2})[ \t]*\n(?:[ \t]*\n)*[ \t]*((?:CO|LO)[ ]?\d(?:[ \t]*,[ \t]*\n?[ \t]*LO\d)*)[ \t]*$` (re.M, region scope), measured as exact tail count per course: 5/5 (`nep2425-fe_hours_co_tail.txt`). Counts: ESC102 6, BSC103 6, ESC101 7 (6 modules + prerequisite row), AEC101 6, VSEC102 6. Spellings: `CO1`, `CO 1`, `CO3` (AEC101 mixes), `LO1, ` + `LO2` on two raw lines (VSEC102 module 1). Hours are 2-digit zero-padded (`04`, `10`). No "Total hours" row exists in the text (UNKNOWN whether in the PDF render).
Order oddity: the tail is not always the last text of a module. AEC101 module 6: sub-items `Plagiarism and copyright infringement` and `Ethical-dilemma case studies` appear on the NEXT page (p5 lines 0-3) after the tail `03` / `CO 6` (p4 lines 91-92). BSC103 and ESC102 content wraps across pages before the tail (e.g. III splits p2/p3 in BSC103).

## Stop markers
`^\s*(Text Books?|Recommended Books|References?)\s*:?\s*$`: 5/6, failure = stub (`nep2425-fe_stop_marker.txt`). Spellings: `Text Books: ` (ESC102, ESC101), `Recommended Books: ` (BSC103), `References: ` (AEC101), `Text Books ` (VSEC102, no colon).

## Watermarks / noise lines
- No watermark text (`(?i)ilovepdf|draft|watermark|confidential`: 0 hits in all 5 PDFs; producers are iLovePDF / Microsoft Print To PDF but not in text).
- Page-number first line (`^\d{1,2}\s*$`) present on 21/27 pages; the 6 failures are all AEC101 (the PDF has no page numbers) (`nep2425-fe_page_number_first_line.txt`). Numbers continue the original document (28, 29, ... 47, 48).
- AEC101 uses private-use bullet U+F0B7 (65 occurrences) alone on a raw line before each bullet text.
- Lost glyphs: BSC103 p2 shows `A) cFuel: - Definition`, `Calorific value (Definition, Types,` then a blank line (text clipped), BSC103 p1 rationale lines start mid-sentence (`is the modern approach to learn...`); ESC101 p2 `Moment of forc` is clipped. Wingdings arrows replaced by nothing (`Proximate analysis, ` / `Ultimate analysis, Numerical)`).
- Table headers (`Course `, `Code `, `IAT-I`, `Hours`, ...) are emitted one cell per raw line and repeat for every course (3 table groups per course).

## Numbering styles (Roman / arabic / 1.1 / 1.)
Module numbers: Roman (a, b), `01`-`06` (c), `1`-`6` (d). Sub-items: `A) B) C) D)` (BSC103, 18 lines), `i) ii)` inline, `3.1 3.2 3.3` (ESC101, 6 lines), `1.1.`-`6.3.` with trailing dot (AEC101, 23), `1.1`-`4.3` (VSEC102, 13), none (ESC102: running prose). Objectives/outcomes lists are `1.` or `1)`.

## Topic separators
Commas and "and" inside running prose (ESC102, ESC101, VSEC102); `A)`/`B)` item labels with ` - `/`:-` heading-content joins (BSC103); `1.x` sub-headings followed by bullet lines (AEC101). Topics in the golden drafts were split by hand; no deterministic separator rule is established (UNKNOWN).

## Known oddities
1. The hypothesis of ONE family is false: four different layouts (sub-families a-d) in 5 PDFs.
2. `02 Syllabus.pdf` contains an AEC101 stub that duplicates a course whose real syllabus is in the Professional_Comm PDF; a parser must not emit it as a course (no module table).
3. ESC101 (`NEW EM SYLLABUS`): module II "Centroid" (p2 lines 47-50) and module VI "Introduction to Robot Kinematics" (p3 lines 14-19) have name + hours + CO only; module III item `3.3 Friction:` (p2 line 64) and module IV rigid-body part are empty/clipped. No images on these pages (`spikes/nep2425-fe_probe.py`: 0 images on pages 1-5), so the content is absent from the text layer; whether it is absent from the visual page is UNKNOWN.
4. VSEC102 is a lab-only course (credits Pract 2*+2, `2*+2` literal) but has a module table with LO mapping; its experiments table (p3-4) uses a separate layout (Sr, text, Hrs).
5. BSL102 experiment rows 10-11 are on page 1 of the Chemistry PDF, before BSC103 (page order scrambled); ESL101 `List of Experiments:` has no rows in the text.
6. Experiment/assignment tables use `LO n` (lab) vs `CO n` (theory); `Hrs` is absent from assignments rows after the first (ESL102 p4).
7. Module hours in BSC103 are 04/04/04/05/04/05; ESC102 total 39; module counts all = 6.
8. AEC101 code appears as `AEC 101` (space) and as split lines `AEC ` / `101 ` in the exam table (p1 lines 35-36).
9. ESL102 Lab regex attempt 1 over-matched (14 vs 13): the "List of Assignments" table has an identically shaped first row; fixed in attempt 2 by truncating at `List of\s+Assignments`.

## Exact regexes with measured coverage (each links to docs/evidence/regex_runs/<file>)
| name | matched/total | file |
|---|---|---|
| detection (code + IAT-I + pages<=8) | 5/5 PDFs, 0 FP over 20 | nep2425-fe_detection.txt |
| course_code_line | 9/9 | nep2425-fe_course_code_line.txt |
| detailed_syllabus_header | 5/6 | nep2425-fe_detailed_syllabus_header.txt |
| stop_marker | 5/6 | nep2425-fe_stop_marker.txt |
| module_roman (a,b) | 3/3 | nep2425-fe_module_roman.txt |
| module_arabic_padded (c) attempt 2 | 1/1 (attempt 1 failed) | nep2425-fe_module_arabic_padded.txt |
| module_arabic_unpadded (d) | 1/1 | nep2425-fe_module_arabic_unpadded.txt |
| hours_co_tail | 5/5 | nep2425-fe_hours_co_tail.txt |
| prerequisite_row_zero | 2/2 | nep2425-fe_prerequisite_row_zero.txt |
| prerequisite_label | 3/5 | nep2425-fe_prerequisite_label.txt |
| self_learning_marker | 0 hits | nep2425-fe_self_learning_marker.txt |
| page_number_first_line | 21/27 | nep2425-fe_page_number_first_line.txt |
| lab_list_label | 4/4 | nep2425-fe_lab_list_label.txt |
| lab_row_hours_lo attempt 2 | 2/2 (attempt 1 failed for ESL102) | nep2425-fe_lab_row_hours_lo.txt |
Regex source: `spikes/nep2425-fe_regex.py` and `spikes/nep2425-fe_detect.py`. Module-name and topic extraction regexes were NOT written (not established), so no coverage is claimed for them.

## Failures (verbatim, per regex, per attempt 1-3)
- detailed_syllabus_header and stop_marker: `AEC101-stub in 02 Syllabus.pdf: no match (page 5 ... no module table)`.
- prerequisite_label: `AEC101 in Professional_Comm._Ethics_Theory_Sem_I 2024-25.pdf: no line matched`; `VSEC102 in Syllabus-C Prog.pdf: no line matched` (absence of the label, not a defect).
- page_number_first_line: 6 failures, all AEC101 pages 1-6 (e.g. `page 4 line 0: ' '`), verbatim in the file.
- module_arabic_padded attempt 1: 10 matches for 6 modules (listed in file); attempt 2 accepted. 1 of 3 attempts used.
- lab_row_hours_lo attempt 1: ESL102 expected 13 got 14; attempt 2 fixed. 1 of 3 attempts used.
- detection attempt 1: 6 false positives; attempt 2 adds page-count clause (0 FP).
No regex has used all 3 attempts. Family is PARTIAL because module-name wrapping (mid-word breaks), sub-item splitting and ESC101 missing content have no deterministic rule yet, and the number of courses per sub-family is 1-2, so coverage numbers are not evidence of generalisation.

## Topic validity census (violations by rule id, total topics)
From `regex_runs/nep2425-fe_topic_validity.txt` (spike `spikes/nep2425-fe_golden.py`, rules from `spikes/topic_validity.py`): total 200 topics (ESC102 41, BSC103 37, ESC101 30, AEC101 29, VSEC102 63). R1 0, R2 0, R3 0, R4 0, R5 1, R6 0, R7 0, R8 0. The one violation is `Practical and Ideal Transformer` (ESC102 module 3) caught by R5 because it starts with "practical": a false positive of R5 on a legitimate topic, kept unmodified (also in open_questions). Note these are hand-drafted golden topics, not parser output, so the census shows the drafting satisfied the rules, not that a parser would.

## Golden courses (5, DRAFT) and how they were drafted
`tests/golden/nep2425-fe/{ESC102,BSC103,ESC101,AEC101,VSEC102}.json`, all `status: DRAFT - needs human sign-off`. Drafted by reading the raw lines of the module region of each course (page lists in each JSON); topics = atomic concepts from item headings/lists, split "A and B" only where the syllabus lists separate concepts; module names taken as printed (wrapped fragments joined by me). ESC101 modules II and VI contain a single topic equal to the name because the syllabus text gives nothing else. AEC101 module 6 includes the 2 bullets found on the next page. No lab/experiment rows are in the golden courses (they are not modules).

## UNKNOWN items (also copied to docs/open_questions.md)
- Whether the visual PDF page shows content for ESC101 "Centroid", "Friction", rigid-body kinematics and "Robot Kinematics" (text layer is empty there).
- ESL101 experiment list rows (label present, no rows in text).
- Rule for joining mid-word wrapped module names and titles.
- Deterministic topic separators for ESC102/ESC101/VSEC102 prose.
- Real per-course detector replacing the page-count clause.
- Whether the AEC101 stub should be merged with the full AEC101 or dropped.
- Whether R5 should exempt "Practical and Ideal Transformer".
