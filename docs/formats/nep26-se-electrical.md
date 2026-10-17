# Format: nep26-se-electrical
Status: VERIFIED-BY-DUMP (all measured regexes reached full coverage within 3 attempts; module-start needed a bbox predicate, see below). Teaching of module name vs content needs bbox (UNKNOWN policy, see open_questions.md).

Hypothesis from `docs/evidence/signatures.csv` (2 PDFs, identical signature rows) is CONFIRMED: one family, no sub-families needed. The two PDFs have identical page structure (60 pages each, same page numbers for every course); text differs only in course-code prefix and a few reference-list lines (evidence: spikes/nep26-se-electrical_probe.py output, diff run in session; pages that differ after code normalisation: 21, 29, 44, 45, 47 -- all reference/bibliography lines).

## PDFs in this family (path, pages, evidence file)
| PDF | pages | course syllabi | codes |
|---|---|---|---|
| `data/raw/2019-scheme/Electrical-Computer-Engineering/6.51N-B.E.-Electrical-Computer-EngineeringSem-III-IV.pdf` | 60 | 13 (7 theory, 4 lab, 1 mini project, 1 workshop) | 2213111..2213116, 2213611, 2214111..2214115, 2214411 |
| `data/raw/2019-scheme/Electrical-Engineering/6.29-N-B.E.-Electrical-Engineering-Sem-III-IV.pdf` | 60 | 13 (same layout) | 2223111..2223116, 2223611, 2224111..2224115, 2224411 |

Total 26 course instances (13 distinct course syllabi x 2 PDFs). Evidence: `docs/evidence/signatures.csv`, `docs/evidence/regex_runs/nep26-se-electrical_objectives.txt` and `_code.txt` (26/26). Raw samples: `docs/evidence/dumps/nep26-se-electrical_2213112_p19.txt` (normal theory), `..._2214112_p43.txt` (odd theory: arabic numbering, prerequisite with dashes, exam table bleeding into module rows), `..._2213115_p28.txt` (lab). Pages 1-15 are front matter (page 1 has no text, pp.5-6 notice/preamble, pp.8-13 credit and program-structure tables, p.14/38 semester cover pages, p.15 "Vertical - 1 / Major"); syllabi are pp.16-60 (Sem III pp.16-36, Sem IV pp.39-60).

## Detection (regex + coverage matched/total)
- `As [Pp]er NEP 2020` on a stripped line, pages 1-8: 2/2 PDFs (`docs/evidence/regex_runs/nep26-se-electrical_detect.txt`). Page 5 holds `Item No. – 6.51 (N)` / `As Per NEP 2020`; page 6 holds `(As per NEP 2020)`; programme-structure pages say `UNIVERSITY OF MUMBAI (With Effect from 2025-2026)` (observed in session, p.10).
- Folder name says `2019-scheme` but both PDFs state NEP 2020 -> scheme must be taken from text (open_questions.md).
- Family discriminators (observed): line `Syllabus for Major`, `Vertical – 1, 4 & 6`, course codes of 7 digits starting `2213/2214` (ECE) or `2223/2224` (EE).

## Course header pattern
There is no single header line. Course data comes from two tables whose text is emitted in PDF content order, which is NOT adjacent to the course start:
1. `Course | Code | Course Name | Teaching Scheme | (Contact Hours/Week) | Credits Assigned | Theory | Pract. | Tut. | ... | Total` then a bare 7-digit code line, the title (1-3 wrapped lines), then hour/credit cells (`2`, `--`, `1`, `3`, `-`).
2. A second table, `Examination Scheme`, repeating the code and title followed by marks.
Their position moves: after module I (p.16, 19, 22), after `Detailed Syllabus` header (p.22, 40), before `Detailed Syllabus` (p.25-26), after module III (p.46), or on the page before the course objectives (Mini Project p.33, Electrical Workshop p.54). Course body starts at `Course Objectives:` (theory) or `Lab Objectives:` / `Lab Objective:` / `Lab objective:` (labs, Mini Project, Workshop).
- Code regex `^\d{7}$` (bare line); assignment to a course = k-th distinct bare code on pages >= 16 for the k-th objectives marker; 26/26 on attempt 2 (attempt 1: 22/26, failed for Mini Project and Workshop because their code lies on the page before the objectives marker).
- Codes also appear on pp.10-13 (program-structure tables) for courses 2993511, 2993512, 2994511, 2994512 (Entrepreneurship Development per p.11 sample) which have NO syllabus pages; so pages < 16 must be ignored.

## Title wrapping
Titles wrap over 1-3 lines in table cells and wrap differently in the two tables (`Engineering Mathematics | for Electrical Circuits` vs `Engineering Mathematics for | Electrical Circuits`). Rule: join lines after the code until a line matching `^(--?|\d+|\d\*\+\d|Theory)$`. Joined title from the two tables is identical for 24/26 on attempt 2; 26/26 on attempt 3 with the extra allowance "later title is a prefix of the first" (Electrical Workshop: teaching table `Electrical Workshop (Group Project)`, exam table `Electrical Workshop`). Evidence: `..._title.txt`.

## Module row pattern
Table header (line order): `Sr. | No. | Name of Module | Detailed Content | Hours | CO | Mapping` (spellings: `Name of the Module Detail Content` on one line for 2214112; `Module | No. | Name of Module | Detail Contents | Hours | LO | Mapping` for Electrical Workshop).
Row in line order: number line (Roman `I`..`VI`, or arabic `1`..`6`), 1-5 wrapped module-name lines, content lines, then tail `hours` line + `CO#` line (see Hours / CO tail). Name and content lines are NOT separable in line order; PyMuPDF `get_text("dict")` x0 separates them (number ~60-75, name ~90-130, content ~190-210, hours ~475-485, CO ~510-530; measured per page, boundaries vary by page, observed pages 16,17,19,20,22,23,25,26,40,41,43,44,46,47,55,56,57).
Every theory course here has exactly 6 modules (14/14 theory instances, `..._module_start.txt`). A module row can break across pages, and its tail may be emitted before the continuation content (p.19 tail `08/CO1` precedes p.20 continuation).

## Prerequisite row
Two spellings (observed in dumps/pages): 
- Dashed: lines `---`, `Prerequisite`, text lines, `---`, `---` placed between the table header and module I (2213113 p.22, 2214111 p.40, 2214112 p.43).
- Plain: `Prerequisite` followed by text with no dashes, then module I (2213114 p.26).
Regex `^Prerequisite$`: 8/14 theory instances; the 6 non-matches (2213111, 2213112, 2214113 in each PDF) have no prerequisite text at all (case-insensitive search over the course segment: False). Evidence `..._prereq.txt`. Prerequisite text is not a Topic source (UNKNOWN whether it should be used as dependency hint).

## Self-learning markers (all spellings seen)
None. Regex `(?i)self[\s\-]*(learning|study)` over all 120 pages: 0 hits (attempt 1 with `\bSL\b` had 2 false hits on the URL `sl-coep.vlabs.ac.in`, p.29 of both PDFs). Spelling UNKNOWN (open_questions.md). Evidence `..._selflearn.txt`.

## Hours / CO tail patterns
After each module's content: line `^\d{1,2}$` immediately followed by `^(CO|LO)\d$`. Hours are written with or without zero padding (`08`, `4`, `04`, `5`). Theory uses `CO1`..`CO6`; Electrical Workshop and lab experiment tables use `LO1`..`LO6` (labs use `Hrs` header and `2` per experiment row). Regex with `(CO|LO)`: 16/16 module-table courses have exactly 6 tails (attempt 1, `CO` only: 14/16 -- missed the two Workshop instances). Hour sums observed (code, not regex): 26 for 2213111/2214111 (2 credits), 39 for the five 3-credit theory courses. Source oddity: 2214113 has `CO1` on both module I and II (06/CO1, 08/CO1). No `Total Hours` line exists.

## Stop markers
Back-matter lines observed in the 7 ECE theory courses (counts, session scan): `Text Books:` 5, `Textbooks:` 2 (2213113, 2214112), `Reference Books:` 1, `References:` 6, `Online References:` 7, `Term Work:` 2, `Assessment:` 5; also `Note: Numerical should be covered in Tutorials.` (2213111). `Online Resources:` appears in labs (p.29). The first of `Text Books:`/`Textbooks:` ends the module rows. Regex `^(Text ?[Bb]ooks?:|Reference Books:|References:)`: 14/14 theory instances (attempt 1 `^(Text Books:|Reference Books:)` 10/14: missed `Textbooks:`). Evidence `..._stop.txt`.

## Watermarks / noise lines
- No watermark, DRAFT text, page number, header or footer line found (regex search `draft|watermark|page \d+` over both PDFs: no hits in session probe; most frequent repeated lines are table words `Total`, `Code`, `Course`, `Theory`, `Sem.`).
- Table-header noise inside module rows: words from the teaching/exam tables (`Course`, `Code`, `Course Name`, `Teaching Scheme`, `Examination Scheme`, `Theory Marks`, `Term`, `Work`, `Exam.`, `Duration`, `(in Hrs.)`, `Internal Assessment (IAT)`, `End`, `Sem.`, `IAT-`, `I`, `IAT-`, `II`, `IAT-I +`, `IAT-II`, `(Total)`, code, title, numbers `20 20 40 60 25 2 125`).
- Dangerous noise: `IAT-` followed by lone `I` / `II` lines (split cell `IAT-I`, `IAT-II`) look exactly like module numbers `I`/`II` (2213111 p.16, 2214111 p.40). Rule: ignore a Roman line whose previous line is `IAT-`.
- Bulleted lines use private-use glyph `` and `●` in references/guidelines (not module content).

## Numbering styles (Roman / arabic / 1.1 / 1.)
- Module numbers: Roman `I`-`VI` (12/14 theory instances) or arabic `1`-`6` (2214112 x2 and Electrical Workshop x2). Arabic number lines are indistinguishable from hour tails (`4`) by regex alone; separation needs x0 < 95 (bbox).
- Within content: `1] ... 2] ...` list markers (2213114 module IV); `-` as inline separator; no `1.1` numbering.
- Course outcomes/objectives numbered `1.` or `1)` or `1` (2214111 objectives use `1   To ...`).

## Topic separators
Within a module's content (observed in samples): comma; period then capital; ` - ` and en dash (2214112 uses ` - ` between phrases); semicolon (2213112 VI, 2213113 V); `Heading: items` colon bundles (2213113 I, II; 2213114 II-III; 2213112 `Parallel Operation: No load Operation, On load Operation: - ...`); parentheses with lists `(half, full)`. Module-name lines may end in `:` (2213112 IV, V, VI), a naive split leaves those attached.

## Known oddities
1. Folder `2019-scheme` vs NEP 2020 text.
2. Two PDFs are near-duplicates (same body, different code prefix).
3. Course header/tables are emitted mid-body (see Course header pattern); Mini Project/Workshop code precedes objectives.
4. Stray `I`/`II` after `IAT-`.
5. Arabic module numbering (2214112, Workshop).
6. Labs 2213115/2213116/2214114/2214115 say `The Syllabus is same as the Theory Course "<title> (Course Code: <code>)"` and list experiments (`Hrs`, `LO`), no module table. Mini Project 2213611 has no `Detailed Syllabus` and no modules. Workshop 2214411 has 6 modules with `Lab Activities` prose (naive topic candidates: 129 per instance).
7. Module name lost words in the spike when a name line equals a course-title line (2213114 VI `Instruments`, 2214112 5/6 `Waves`) - extraction bug in the spike, not a source property; golden names written from reading.
8. Source typos: `RSIC`, `Bio Savart`, `Stroke's`, `Maxwells`, `Analys`, `spilt`.
9. 2214113 CO1 repeated on modules I and II.
10. Program-structure pages list 4 Entrepreneurship Development codes with no syllabus pages.

## Exact regexes with measured coverage (each links to docs/evidence/regex_runs/<file>)
All measured over every course instance (26) or every course instance with the relevant table; command pattern `PYTHONIOENCODING=utf-8 python spikes/nep26-se-electrical_regex_runs.py <name>`.
| name | final regex | coverage | attempts | file |
|---|---|---|---|---|
| detect | `As [Pp]er NEP 2020` (line, pp.1-8) | 2/2 PDFs | 1 | nep26-se-electrical_detect.txt |
| code | `^\d{7}$` (bare line, pages >= 16, window = segment + previous page) | 26/26 | 2 | nep26-se-electrical_code.txt |
| objectives | `^(Course\|Lab) [Oo]bjectives?:` | 26/26 | 1 | nep26-se-electrical_objectives.txt |
| syllabus_hdr | `^Detailed Syllabus:` | 24/26 (2 Mini Project instances have no such line; genuine absence) | 1 | nep26-se-electrical_syllabus_hdr.txt |
| module_start | `^((I\|II\|III\|IV\|V\|VI)\|[1-6])$` + previous line != `IAT-` + bbox x0 < 95 | 16/16 | 3 (8/16, 12/16, 16/16) | nep26-se-electrical_module_start.txt |
| tail | `^\d{1,2}$` then `^(CO\|LO)\d$` | 16/16 (6 each) | 2 (14/16, 16/16) | nep26-se-electrical_tail.txt |
| prereq | `^Prerequisite$` | 8/14 (6 = no prerequisite row) | 1 | nep26-se-electrical_prereq.txt |
| stop | `^(Text ?[Bb]ooks?:\|Reference Books:\|References:)` | 14/14 | 2 (10/14, 14/14) | nep26-se-electrical_stop.txt |
| title | join lines after code until `^(--?\|\d+\|\d\*\+\d\|Theory)$`, accept prefix | 26/26 | 3 (16/26, 24/26, 26/26) | nep26-se-electrical_title.txt |
| selflearn | `(?i)self[\s\-]*(learning\|study)` | 0 hits (marker absent) | 2 | nep26-se-electrical_selflearn.txt |
Caveats: "matched/total" for `code` assigns the k-th code to the k-th objectives marker, so it tests presence, not independent identification; `module_start` final form is not line-order-only (needs x0).

## Failures (verbatim, per regex, per attempt 1-3)
Full verbatim lists (pdf, page, extracted value) are in the regex_runs files; summary of the attempts that did not cover everything (each fixed by a later attempt):
- code attempt 1: 22/26; failures 2213611 p34 `Lab Objective:`, 2214411 p55 `Lab objective:` (and the same two codes in the EE PDF, 2223611, 2224411): code line on the previous page.
- module_start attempt 1: 8/16; 2213111 -> `['I','I','II','II','III','IV','V','VI']`, 2214111 -> `['I','II','I','II','III','IV','V','VI']` (stray after `IAT-`), 2214112 and 2214411 -> `[]` (arabic), x2 PDFs. Attempt 2 (`IAT-` rule): 12/16, arabic still `[]`. Attempt 3: 16/16.
- tail attempt 1 (`CO` only): 14/16; 2214411 p55 `0 tails []` (Workshop uses `LO`), x2.
- stop attempt 1: 10/14; 2213113 p22 and 2214112 p43 `none` (`Textbooks:`), x2.
- title attempt 1: 16/26 (Mini Project and Workshop have no code in segment; 2214112/2214114/2214115 have one code occurrence in segment); attempt 2: 24/26 (Workshop: `['Electrical Workshop (Group Project)', 'Electrical Workshop']` x2); attempt 3: 26/26.
- syllabus_hdr: 24/26, residual = Mini Project 2213611 p34 and 2223611 p34 (no line; not a regex bug).
- prereq: 6 non-matches are courses without a prerequisite row.
- No regex is PARTIAL.

## Topic validity census (violations by rule id, total topics)
Evidence `docs/evidence/regex_runs/nep26-se-electrical_topic_validity.txt` (`spikes/nep26-se-electrical_census.py`, rules `spikes/topic_validity.py`).
- A. 5 DRAFT golden courses: 343 topics, 0 violations (R1-R8 all 0). Caveat: circular, I wrote them with the rules in mind; three rewrites were needed to pass (a topic starting `Practical issues ...` hits R5, `120 degree ...` and `8051 ...` hit R6 as false positives for real numbers -> reworded).
- B. Naive split (comma/semicolon/period/dash, headings left attached) of module content of all 16 module-table courses x 2 PDFs: 1068 candidates, 196 with a violation: R1 98, R2 42, R3 100, R4 8, R5 4, R6 24, R8 6 (R7 0). Naive splitting is therefore not a valid topic extractor; colon bundles and dash chains drive R1/R2/R3.

## Golden courses (5, DRAFT) and how they were drafted
`tests/golden/nep26-se-electrical/{2213112,2213113,2213114,2214112,2214113}.json`, all status `DRAFT - needs human sign-off`, source PDF 6.51N (the EE PDF carries the same text with codes 2223112 etc.). Drafted by reading each course's module text (x0 column extraction printed in-session) and splitting into atomic concepts per `docs/formats/topic_validity.md`; headings before `:` kept as topics only when they are concepts; items under colon bundles listed individually. Chosen: normal theory 2213112, bundle-heavy 2213113, prerequisite-without-dashes 2213114, arabic-numbered 2214112, cross-page 2214113. Family has 7 distinct theory courses with real topic lists (not 5 only); labs and Mini Project have no module topics and are not included. Counts: 63, 62, 73, 73, 72 topics. Generator: `spikes/nep26-se-electrical_golden.py`. Not human verified.

## UNKNOWN items (also copied to docs/open_questions.md)
Self-learning marker spelling; whether v2 parser may use bbox; syllabus source for Entrepreneurship Development; scheme from folder vs text; dedup of the two PDFs; lab experiments as Topics; Workshop/Mini Project handling; typo policy; use of hour sums as parse_confidence. See `docs/open_questions.md` lines prefixed `nep26-se-electrical`.
