# Format: nep26-se-civil
Status: PARTIAL   (module/course extraction regexes reach full coverage on the 17 courses of the only PDF; PARTIAL because the family has only 1 PDF (no generalisation evidence), 4 scheme-listed courses have no syllabus text, labs have no module table, and the topic-level split is not machine-solved: see Topic validity census)

Scope note: every claim below cites a file under `docs/evidence/`. Line numbers are 0-based indices into `page.get_text().split("\n")`; pages are 1-based PDF pages. Spike code: `spikes/nep26-se-civil_parse.py`, `spikes/nep26-se-civil_runs.py` (regenerates every `regex_runs/nep26-se-civil_*.txt`), `spikes/nep26-se-civil_dump.py`, `spikes/nep26-se-civil_golden.py`.

## PDFs in this family (path, pages, evidence file)
- `data/raw/2019-scheme/Civil-Engineeing/6.23-N-B.E.-Civil-Engineeing-Sem-III-IV.pdf`, 82 pages, 1 PDF only (`docs/evidence/signatures.csv` row "2019-scheme/Civil-Engineeing/..." pages=82). The folder name "2019-scheme" is a misnomer for scheme naming; the scheme-in-text check is not part of this evidence (UNKNOWN, see below).
- Content: pdf pp 1-15 are front matter and scheme tables (scheme tables with course codes on pp 10-13; other front-matter content UNKNOWN, not inspected), course syllabi pp 16-82. 17 courses with syllabus text found (Sem III: 2093111-2093116, 2993511, 2993512, 2093611; Sem IV: 2094111-2094115, 2094411, 2994511, 2994512). Evidence: `docs/evidence/regex_runs/nep26-se-civil_course_code.txt` (list "courses found (17)").
- 4 more codes appear only in the scheme tables (pp 10-13) with no syllabus page: 2093311 (Open Elective), 2094211 (Multidisciplinary minor), 2094212 (Multidisciplinary minor lab), 2094311 (Open Elective). Evidence: same file, FAIL lines and "pdf pages on which the missing code string occurs anywhere" (pp 10-11 / 12-13 only).

## Detection (regex + coverage matched/total)
- D1 `(?m)^Second Year Civil Engineering\s*$` AND D2 `(?m)^Course Module / Contents\s*$` both present in the PDF text. Coverage 1/1 family PDFs; negative control: 0 false positives over the other 24 PDFs in `signatures.csv`. Evidence: `docs/evidence/regex_runs/nep26-se-civil_detect.txt`.
- Hypothesis from `signatures.csv` ("odd layout: 0 module_detailed_content lines, 0 prerequisite lines, 0 total_hours, 115 dotted_subitem, 7 Course Outcomes") is CONFIRMED in part: the family has a Module table but no "Detailed Contents" header and no "Total Hours" line; the 7 "Course Outcomes" headers equal the 7 theory courses (2093111-4, 2094111-3) (`nep26-se-civil_outcomes.txt` plus `nep26-se-civil_module_row.txt`). The signature's `prereq_line=0` does NOT match this analysis: a prerequisite line in other spellings exists in 7 of 17 courses (see Prerequisite row). The signature regexes themselves were not reproduced here (UNKNOWN how 115 dotted sub-items was counted vs 178 accepted here; evidence: `nep26-se-civil_subitem.txt` "sub-items accepted=178").

## Course header pattern
- A course starts on its own PDF page (course start pages p16, 20, 24, 28, 31, 33, 37, 41, 46, 52, 55, 59, 63, 66, 70, 75, 78) with two tables whose cells come out as one line each: line `Course ` / `Code ` (or `Course Code ` on pp 63, 66), column headers, then a line that is only the 7-digit code, then the title lines, then numeric/dash cells (teaching scheme, credits). Evidence: `docs/evidence/dumps/nep26-se-civil_2093115_p32.txt` is a later page; the header table itself is evidenced in `docs/evidence/regex_runs/nep26-se-civil_course_code.txt` and `..._title.txt` (page 16 raw lines 6-30 were inspected during the spike; no dump file was kept for it, so the raw header layout is UNKNOWN as evidence beyond those two runs).
- Regex CODE `^(\d{7})\s*$` (whole line), course start = pdf page >= 16, line index < 25, with a `Code` line within the previous 16 lines. Course codes are 7 digits (e.g. 2093112, 2993511). Coverage: 17/21 scheme-table codes found; the 4 misses are the elective/minor courses with no syllabus page (Failures section). `nep26-se-civil_course_code.txt`.
- The code line occurs twice per course start page (teaching-scheme table, then exam-scheme table); the title is repeated in the second table with different line wrapping and sometimes different case ("Applied mathematics for" vs "Applied Mathematics for"), so title comparison must be case-insensitive (`nep26-se-civil_title.txt`).
- Page header lines on every page from pdf p6: line 0 `Page | N `, line 1 `University of Mumbai `, line 2 `Second Year Civil Engineering ` (`nep26-se-civil_noise.txt`, 77/77).

## Title wrapping
- Title spans 1-4 lines after the code line, ended by the first line that is only digits (optionally `*`/`#`/`+digits`), only dashes, or starts with `(`. Regex TITLE_STOP `^(\d+[*#]?(\+\d+)?|[-–—]+|\(.*)\s*$`. Join lines with a space. Verified by agreement between table 1 and table 2 titles (case/whitespace-insensitive): 17/17. Evidence: `nep26-se-civil_title.txt` (lists all 17 titles).
- Caveat: the agreement test only shows both tables yield the same string; it does not show the titles are right against an external list. UNKNOWN whether the two-line capstone title "Computer Aided Architectural Planning, and Building Design (Capstone Mini-Project)" should include the "(Capstone Mini-Project)" part (the spike title stops at "(" so it is dropped; 2094411 appears in the titles list without it).

## Module row pattern
- Detailed-syllabus table header: lines `Module`, `Course Module / Contents`, `Hours` (or `Hrs`), `CO` (or `LO`), optionally `Mapping` (or `Mappi`/`ng` split over two lines). It is repeated at the top of continuation pages. Regex COLHDR in the regex table; coverage 11/11 module courses, `nep26-se-civil_colhdr.txt`.
- Each module is a 4-part sequence of separate raw lines: (1) the module number alone (`1`, `6  `), (2) the module name, 1-3 lines (wraps, e.g. module 3 of 2093114 over 2 lines), (3) hours alone (`05` Sem III, or one digit `6` in 2094112), (4) the CO/LO tail: `CO1`, or for LO courses a comma-separated list over several lines (`LO2,` / `LO3,` / `LO4`). Regex MODROW. Coverage: 11/11 module courses; every course gave 6 modules numbered 1..6 equal to the count of numbered outcomes (`nep26-se-civil_module_row.txt`).
- Sub-items follow: `N.M` on its own line with text on the next lines, OR `N.M text...` inline on one line (both occur, even inside one module, e.g. 3.1 vs 3.2 in 2093114 page 29). Regex SUB, accepted only when N equals the current module number. Coverage 66/66 modules had sub-item numbers running 1..k with no stray `N.M` lines (`nep26-se-civil_subitem.txt`).
- Module count: always 6 (11/11). Number of sub-items per module: 1 to 5 (per-module lists in the EXTRA block of `docs/evidence/regex_runs/nep26-se-civil_subitem.txt`).
- The module table appears only for 11 courses: 2093111-2093114, 2993511, 2993512, 2094111-2094113, 2994511, 2994512. The other 6 courses (2093115, 2093116, 2093611, 2094114, 2094115, 2094411) have no module table (see Known oddities). Evidence: `nep26-se-civil_module_row.txt` header lines.

## Prerequisite row
- Spellings seen: `Pre-requisite:`, `Pre Requisite:`, `Prerequisite:` (7 of 17 courses; `nep26-se-civil_prereq.txt`, regex `(?im)^Pre[- ]?requisites?\s*:`). Value is on the same line (2094113, 2094411) or on following lines (list, with `` bullet glyph lines in 2094111). Position varies: before "Course Objectives:" (2093111 page 16), between "Detailed Syllabus" and the module header (2093112 page 21, dump `nep26-se-civil_2093112_p21.txt` lines 4-8), or right before the module table (2994511, 2993511).
- 10 courses have no match; whether absence means "none" is UNKNOWN.

## Self-learning markers (all spellings seen)
- `Self-learning Topics:` / `Self-learning topics:` / `Self- Learning Topics:` / `Self- learning Topics:` / `Self -learning Topics:` (OCR-like spacing; 2094111 pages 53-54). Regex SELF `Self[\s-]*learning\s+topics?\s*:` (re.I): 11/11 courses where the count of regex hits equals the count of any "self-learning" spelling in the module section (`nep26-se-civil_self_learning.txt`; attempt 1 failed 10/11, kept verbatim there).
- The marker starts a line (or a line after a sub-item) and runs to the end of the module (up to the next module number line). It may start mid-module after the last sub-item. Content may include URLs and book titles (2994511 modules 1, 3, 5, 6; 2994512). Courses with no marker in the module section: 2093112-2093114, 2993511, 2993512, 2094112, 2094113 (hit count 0 = any-spelling count 0, same file).
- There is no "Self Study" spelling observed (`signatures.csv` self_study=0).

## Hours / CO tails
- Hours: 1-2 digits alone on a line, after the module name (`05`, `6`, `11`). No "Total Hours" line (`signatures.csv` total_hours=0). Module hour sums per course observed by spike: 2093111=26, 2093112=39, 2093113=38, 2093114=39, 2993511=25, 2993512=26, 2094111=27, 2094112=39, 2094113=42, 2994511=25, 2994512=26 (derived from `nep26-se-civil_module_row.txt` hours lines). Whether this sum should be a parse check is UNKNOWN.
- Tail token: `CO\d` (theory) or `LO\d` (lab-category courses with a module table); multi-line list for LO courses; header column label can say `CO` while rows say `LO` (2993512, 2994512; `nep26-se-civil_colhdr.txt`/`module_row.txt`).

## Stop markers
- The module section ends at the first line starting with any of: `Text Books:`/`Textbooks:`, `Reference books:`/`References:`, `Online References:`/`Online Resources:`, `Assessment:`, `List of Experiments`, `List of Assignments`, `Term Work`. Regex STOP (re.I). Used across all 11 module courses, 11/11 gave 6 modules (`nep26-se-civil_module_row.txt`). Which marker is the first for each course was not recorded separately (UNKNOWN).

## Watermarks / noise lines
- No DRAFT watermark (`signatures.csv` draft_watermark=0).
- Page header triple on pages 6-82 (77/77) (`nep26-se-civil_noise.txt`). Stray lines: `Vertical – N ` (pp 15, 36, 45, 51, 69, 74) and `Semester III`/`Semester IV` (pp 16, 52), listed in the same file. `Vertical – 5` at the end of p74 follows the 2094411 text and could be mistaken for content.
- Repeated column header blocks on continuation pages (Module row pattern).
- Page 1 has 1 line only (cover image), `nep26-se-civil_noise.txt` extra line.
- Text fragmentation: many sub-item lines come out one word per line (e.g. 2093112 page 21 lines 44-47 "Archimedes / principle, / Buoyancy, / Meta-Centre,"; dump `docs/evidence/dumps/nep26-se-civil_2093112_p21.txt`), and some lines end without a trailing space (dump lines 39-42), so joining raw lines with no separator would fuse words. Join lines with a single space and collapse whitespace; one-word-per-line fragments are harmless for the module row regexes but break any "one raw line = one topic" assumption.
- Letter-spaced text inside a sub-item ("r e p e a t e d", 2094111): 1 occurrence in all module sections; evidence: `docs/evidence/regex_runs/nep26-se-civil_subitem.txt` EXTRA block.

## Numbering styles (Roman / arabic / 1.1 / 1.)
- Modules: arabic `1`..`6`, no Roman numerals (`nep26-se-civil_module_row.txt`).
- Sub-items: `N.M` (e.g. `2.3`), M from 1 (`nep26-se-civil_subitem.txt`).
- Outcomes: `1.`, `1)` (2094411 Lab Outcomes) or a bare number on its own line (2093611) (`nep26-se-civil_outcomes.txt` attempt history).
- Lab experiment tables: zero-padded `01`, `02` or `1`, `2` in a `Sr No` column (dump `nep26-se-civil_2093115_p32.txt` lines 23-31; 2994511 page 77 uses `01`).

## Topic separators
- Inside a sub-item: commas separate concepts; `Heading: list` (colon or ` : ` with a space before it) joins a heading and a list (e.g. `2.2 Hydrostatic force on surfaces:` then text; dump `nep26-se-civil_2093112_p21.txt`); sentence periods end phrases ("Pressure scale, Absolute, ..."); `&` and `and` join items; parentheses hold qualifiers ("(without proof)"). Sub-items are often long sentences, not atomic topics: see census.
- A deterministic parser can only get sub-item level units reliably; atomic Topic splitting is UNKNOWN (open_questions.md).

## Known oddities
1. No "Detailed Contents" header and no "Module N: name" prefix: the module is a 4-line cell sequence (number / name / hours / CO). Evidence: `docs/evidence/dumps/nep26-se-civil_2093112_p21.txt` lines 15-18.
2. Module name wraps over 2 lines (2093114 module 3) and sub-items 3.1-3.3 of 2093114 repeat the module title verbatim: `docs/evidence/dumps/nep26-se-civil_2093114_p29.txt` lines 34-43.
3. Two layouts in one PDF: (a) module-table courses, (b) experiment-table courses (labs and the mini project/capstone) with columns `Sr No | List of Experiments | Hrs | LO Mapping` and sometimes a second table `List of Assignments / Tutorials`. Evidence: `docs/evidence/dumps/nep26-se-civil_2093115_p32.txt` lines 16-59; `docs/evidence/regex_runs/nep26-se-civil_module_row.txt` ("other 6 courses have no module table"); `docs/evidence/regex_runs/nep26-se-civil_experiment_tables.txt`.
4. The mini project 2093611 has a `Sr. No.` / `Stages of Project` table (p47); 2094411 has `List of Experiments` rows with `Concepts & Discussions` / `Practical` sub-blocks (p71, 30 header hits). Evidence: `docs/evidence/regex_runs/nep26-se-civil_experiment_tables.txt` (6/6 non-module courses have such a table header). Rows are not parsed; see UNKNOWN.
5. Lab-category courses 2993511, 2993512, 2994511, 2994512 (contact hours `2*+2`, "Lab Objectives/Outcomes") DO have a module table with `LO` tails; the header column says `CO` in 2993512 and 2994512 although the rows say `LO`.
6. Folder name `2019-scheme` vs. text: UNKNOWN (scheme text not checked in this run).
7. Course Outcomes header spellings: `Course Outcomes:`, `Lab Outcomes:`, bare `Outcomes:` (2093611) (`docs/evidence/regex_runs/nep26-se-civil_outcomes.txt`, 17/17 courses have a header with numbered items). The outcome count equals 6 for the 11 module courses (`nep26-se-civil_module_row.txt` outcomes_count); counts for the 6 non-module courses were not recorded (UNKNOWN).
8. The first syllabus page of a theory course (e.g. 2093111 page 16) contains "Semester III" as the last line; page text is not ordered by visual position but by table cell.
9. `signatures.csv` Dotted sub-item 115 vs 178 sub-items found here: counting rule of the signature spike differs (UNKNOWN).

## Exact regexes with measured coverage (each links to docs/evidence/regex_runs/<file>)
All regexes were run against EVERY course in the family (the one PDF) with `PYTHONIOENCODING=utf-8 python spikes/nep26-se-civil_runs.py`.

| name | regex (python `re`) | coverage | evidence |
|---|---|---|---|
| detect D1/D2 | `(?m)^Second Year Civil Engineering\s*$`, `(?m)^Course Module / Contents\s*$` | 1/1 PDFs, 0 false positives on 24 other PDFs | `regex_runs/nep26-se-civil_detect.txt` |
| CODE | `^(\d{7})\s*$` (+ position rule) | 17/21 (4 codes have no syllabus page, see Failures) | `regex_runs/nep26-se-civil_course_code.txt` |
| TITLE_STOP | `^(\d+[*#]?(\+\d+)?\|[-–—]+\|\(.*)\s*$` | 17/17 (table1 vs table2) | `regex_runs/nep26-se-civil_title.txt` |
| COLHDR | `^Module[ ]*\nCourse Module / Contents[ ]*\n(?:Hours\|Hrs)[ ]*\n(?:CO\|LO)[ ]*\n(?:Mapping[ ]*\n\|Mappi[ ]*\nng[ ]*\n)?` (re.M) | 11/11 module courses (attempt 2) | `regex_runs/nep26-se-civil_colhdr.txt` |
| MODROW | `^(\d{1,2})[ ]*\n((?:[^\n]*\n){1,3}?)(\d{1,2})[ ]*\n((?:(?:CO\|LO)\d+,?[ ]*\n)+)` (re.M, applied to rstripped lines joined by `\n`) | 11/11 courses (6 modules each) | `regex_runs/nep26-se-civil_module_row.txt` |
| SUB | `^(\d{1,2})\.(\d{1,2})(?:[ ]+(\S.*?))?[ ]*$` (+ N == module) | 66/66 modules | `regex_runs/nep26-se-civil_subitem.txt` |
| SELF | `Self[\s-]*learning\s+topics?\s*:` (re.I) | 11/11 (attempt 2) | `regex_runs/nep26-se-civil_self_learning.txt` |
| STOP | `^(?:Text ?books?\|Reference books?\|References\|Online (?:References\|Resources)\|Assessment\|List of Experiments\|List of Assignments\|Term Work)\b` (re.I\|re.M) | 11/11 (indirect, via MODROW) | `regex_runs/nep26-se-civil_module_row.txt` |
| OUT_HDR/OUT_ITEM/OUT_END | `^(?:(?:Course\|Lab) )?Outcomes:` / `^\d+(?:[.)]\|[ ]*$)` / `^(?:Semester\|Detailed\|DETAILED\|Prerequisite\|Pre[- ]?[Rr]equisite\|Module\|Sr\. ?No)` | 17/17 (attempt 2) | `regex_runs/nep26-se-civil_outcomes.txt` |
| PRE | `(?im)^Pre[- ]?requisites?\s*:` | 7/17 (informational) | `regex_runs/nep26-se-civil_prereq.txt` |
| header noise | three whole-line page-header regexes | 77/77 | `regex_runs/nep26-se-civil_noise.txt` |

Denominator rule for MODROW: a course matches only if module count equals numbered items under its outcomes header and numbers run 1..n. This is a check against an independent count, but both use the same text, so "11/11" does not prove each module's name/hours are right; it was spot-read for 2093112, 2093114, 2094111, 2994511 only.

## Failures (verbatim, per regex, per attempt 1-3)
- CODE (4, not parser errors; syllabus pages absent): `2093311 | pdf page 10`, `2094211 | pdf page 12`, `2094311 | pdf page 12`, `2094212 | pdf page 12`: code listed in scheme table but no course-start page found (the code string occurs only on pp 10-11 / 12-13). `nep26-se-civil_course_code.txt`.
- SELF attempt 1 (`Self[- ]?learning\s+[Tt]opics?\s*:`): 10/11. Failing lines verbatim: p53 line 23 `'Self- Learning Topics: '`; p53 line 66 `'Self- learning Topics: Conditional probability, Total Probability '`; p54 line 16 `'Self -learning Topics: Test of significance of large samples, '`; p54 line 28 `'Self- learning Topics: ANOVA: One way classification, Two- '`. Fixed in attempt 2 (11/11). `nep26-se-civil_self_learning.txt`.
- OUTCOMES attempt 1: 15/17: 2093611 (header is `Outcomes: ` p46 line 80, items are bare numbers) and 2094411 (items `1) ...` p70 line 82). Fixed in attempt 2 (17/17). `nep26-se-civil_outcomes.txt`.
- COLHDR attempt 1 (Hours only, no Mappi/ng): left `Module / Course Module / Contents / Hrs / CO` (2094111 pdf p54 lines 4-7) inside the body of sub-item 5.2; also `Hrs` first header p53 lines 4-7 and `Mappi`/`ng` p78 lines 80-85 (2994512). Fixed in attempt 2 (11/11). `nep26-se-civil_colhdr.txt`.
- PRE: 10 courses with no prerequisite line (2093113, 2093114, 2093115, 2093116, 2993512, 2093611, 2094112, 2094114, 2094115, 2994512); informational. `nep26-se-civil_prereq.txt`.
- Not covered by any regex (UNKNOWN, see below): the 6 experiment-table courses have no parser for rows; `module_row` marks them "no module table".
- No regex needed a third attempt. No regex is below target after attempts except CODE (explained: missing courses), PRE (informational).

## Topic validity census (violations by rule id, total topics)
Evidence: `docs/evidence/regex_runs/nep26-se-civil_topic_validity.txt` (script `spikes/nep26-se-civil_runs.py`, rules from `spikes/topic_validity.py`). Candidates were produced two naive ways from the 66 modules / 178 sub-items of the 11 module courses; 6 experiment-table courses are not included (no module table).
- S1 whole sub-item text as one topic: 178 candidates, 138 with at least one violation. By rule: R1 132, R2 111, R3 57, R6 1; R4/R5/R7/R8 0.
- S2 split at `: ; , .` outside parentheses: 640 candidates, 67 with at least one violation. By rule: R1 46, R2 22, R4 14, R5 1, R6 2, R8 5; R3 and R7 0 (R3 is 0 by construction because `:` and `;` are split points).
- Reading: sub-items are almost never valid topics as a unit (78% violate); comma splitting yields ~90% valid-by-rule fragments but many are not real concepts (rules R1-R8 cannot detect that), so S2 counts say nothing about correctness.
- Golden drafts (hand-split by me): 2093112 73 topics, 2093114 46, 2094111 49, 2994511 44, 2093115 0: 0 violations in all (`topic_validity.txt` golden lines). One topic was reworded to avoid R5 ("Practical applications of ..." renamed "Applications of ..."): that rename itself shows R5 is a heuristic on the leading word.

## Golden courses (5, DRAFT) and how they were drafted
Files: `tests/golden/nep26-se-civil/{2093112,2093114,2094111,2994511,2093115}.json`, all `status: DRAFT - needs human sign-off`, never verified. I read each course's sub-item text via the spike (never the whole PDF) and hand-split each sub-item into concept phrases applying `docs/formats/topic_validity.md`.
- 2093112 Fluid Mechanics: normal theory.
- 2093114 Mechanics of Structures: odd (module 3 sub-items repeat the module title; module 3 topics come from the title only and are UNKNOWN against the real syllabus).
- 2094111 Applied Mathematics for Civil Engineering-II: self-learning in all modules, 4 spacing variants; self-learning items excluded (status UNKNOWN).
- 2994511 Business Model Development: LO tails over multiple lines; self-learning items with URLs/books excluded.
- 2093115 Fluid Mechanics lab: no Module table; `modules` is `[]`; experiments/assignments not drafted (UNKNOWN how to model).
- Added key `draft_notes` (string) to each JSON beyond the requested schema; every other key follows the schema.
- Raw dumps (first 60 raw lines of one page each, unedited): `docs/evidence/dumps/nep26-se-civil_2093112_p21.txt` (normal theory), `nep26-se-civil_2093114_p29.txt` (odd theory), `nep26-se-civil_2093115_p32.txt` (lab).

## UNKNOWN items (also copied to docs/open_questions.md)
1. Whether the 6 experiment-table courses (labs 2093115, 2093116, 2094114, 2094115, mini project 2093611, 2094411) yield Modules/Topics, or are excluded.
2. Whether self-learning items count as Topics.
3. Syllabus text for 2093311, 2094211, 2094212, 2094311 (absent from this PDF).
4. Scheme text check (NEP 2020 wording) for the "2019-scheme" folder was not run here.
5. Whether the "(Capstone Mini-Project)" part belongs to the title of 2094411.
6. Sub-items 3.1-3.3 of 2093114 duplicate the module title: true syllabus content unknown.
7. Topic-level splitting rule (sub-item vs comma-separated concept) needs a professor/human decision.
8. Generalisation: only 1 PDF in this family, so layout stability across other Civil/Sem III-IV PDFs is UNKNOWN.
9. Whether absent prerequisite means none.
