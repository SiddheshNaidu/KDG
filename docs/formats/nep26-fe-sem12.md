# Format: nep26-fe-sem12
Status: PARTIAL   (title, module-row (IKS201 only), prerequisite-row and table_hdr rules do not cover every occurrence; see Failures. Everything below was observed by dump/regex run unless marked UNKNOWN.)

Evidence root: `docs/evidence/` (regex runs in `regex_runs/nep26-fe-sem12_<name>.txt`, dumps in `dumps/nep26-fe-sem12_*`). All numbers below come from `spikes/nep26-fe-sem12_*.py` run on PyMuPDF `page.get_text()` line order (command line of each run is the first line of its evidence file).

Verdict on the hypothesis: the six PDFs are ONE family at the line-layout level (same page structure, same 35 Course slots per PDF, same module-row styles), but they are NOT near-duplicates in content: course texts differ by branch (see "Known oddities" and `regex_runs/nep26-fe-sem12_pdf_diff.txt`). The hypothesis "DRAFT watermark seen 5x" is refuted: all 5 hits are the word "Drafting" (see Watermarks). No PDF split into separate sub-families, but ONE PDF contains several course-level layout variants (below); they are named `v-roman`, `v-arabic`, `v-trade`, `v-lab`, `v-none` and are NOT separate families. Sub-family names `nep26-fe-sem12-a` etc. are therefore not used (none needed; UNKNOWN if the lead prefers one parser per variant).

## PDFs in this family (path, pages, evidence file)
| path | pages | courses (detail) |
|---|---|---|
| data/raw/2019-scheme/AIML/6.9N-AIML.pdf | 138 | 35 |
| data/raw/2019-scheme/CSE-AIML/6.14N-CSE-AIML.pdf | 137 | 35 |
| data/raw/2019-scheme/DS/6.28N-DS.pdf | 136 | 35 |
| data/raw/2019-scheme/EXTC/6.19-N-EXTC.pdf | 138 | 35 |
| data/raw/2019-scheme/Information-Technology/6.22-NIT.pdf | 137 | 35 |
| data/raw/2019-scheme/Mechanical-Engineering/6.23-NB.E.-Mechanical-Engineering-Sem-I-II-2.pdf | 136 | 35 |

Evidence: page counts via `fitz` (`spikes/nep26-fe-sem12_probe.py`), course counts `regex_runs/nep26-fe-sem12_course_code.txt` (segmented=35 in every PDF), signature row `docs/evidence/signatures.csv`.
Totals: 6 PDFs, 210 course occurrences, 39 unique course codes (`regex_runs/nep26-fe-sem12_pdf_diff.txt`).
Folder `2019-scheme` is a misnomer: page 1 says "As Per NEP 2020", "AC - 28/6/2024", "University of Mumbai", "Semester I & II", academic year 2024-25 (`regex_runs/nep26-fe-sem12_detect.txt`; page-1 raw lines inspected in `spikes/nep26-fe-sem12_probe.py` runs).

How the PDFs differ (course code set diff, evidence `nep26-fe-sem12_pdf_diff.txt`):
- AIML, CSE-AIML, DS, Information-Technology: identical 35-code set.
- EXTC: 35 codes; has PCC2016/PCL2016 ("Elements of Telecommunication", Lab) instead of PCC2011/PCL2011 ("Data Structure", Lab).
- Mechanical-Engineering: 35 codes; has PCC2018/PCL2018 ("Elements of Mechanical Engineering", Lab) instead of PCC2011/PCL2011.
- Text of shared codes differs by branch: byte-identical (whitespace and page-number lines removed) shared-course counts: AIML vs CSE-AIML 34/35, AIML vs IT 30/35, AIML vs DS 24/35, AIML vs EXTC 13/33, AIML vs MECH 16/33. Different pages: the same course starts 1 page earlier in DS (from BSL101), 1 earlier in EXTC and Mech (from BSC101), so page numbers must not be hard-coded.

## Detection (regex + coverage matched/total)
`As Per NEP 2020` on pages 1-2: 6/6 PDFs (`regex_runs/nep26-fe-sem12_detect.txt`). This detects NEP and this booklet series only. It does NOT distinguish this family from other NEP families; family-level detection needs the structural test: a page containing `^\s*(Course|Lab) Objectives` plus a code line `^[A-Z]{2,5}\d{3,4}[A-Z]?` (UNKNOWN whether this already separates it from `nep26-sem56`; not checked, the other family docs are not mine).
Negative check: case-sensitive `\bDRAFT\b` = 0 lines in all 6 PDFs (`regex_runs/nep26-fe-sem12_draft_watermark.txt`).

## Course header pattern
A Course appears in TWO scheme tables on consecutive pages (teaching scheme: Course Code, Course Name, Theory/Pract./Tut., Credits; examination scheme: IAT-I, IAT-II, End Sem, Term work...). The code is a line by itself or followed by the title, e.g. raw lines `'BSC101 Applied Mathematics-I '` / `'ESL101 '` + `'Engineering '` + `'Mechanics Lab '` / `'VSEC102   C Programming '` (dumps/nep26-fe-sem12_BSL101_p24.txt holds the lab scheme row). Code shapes seen: `BSC101`, `VSEC102` (2-5 letters + 3 digits), `BSC2021`, `PCC2016`, `PCL2018` (4 digits). Codes ending in X (`BSC202X`, `PCC201X`, `PCL201X`) appear ONLY in the Sem II scheme summary tables (p13-14) and are placeholders for the numbered variants BSC2021-2023 / BSL2011-2013 / BSC2031-2033 / BSL2021-2023 / PCC2011|2016|2018 / PCL2011|2016|2018, never detail courses. Code suffix letters: `...C` theory-like, `...L` lab-like (but AEL101, ESL201, PCL20xx have module tables, see Module row).
A code may wrap across lines in the examination table: `'BSC202'` then `'2 '` (EXTC p73, Mech p72) and `'PCL201'` + `'8 '` (Mech p110). The join (bare 3-digit-code line followed by a bare one-digit line) is valid only after the first `BSC101` line; in the summary tables a bare code is followed by a bare credit digit (false joins like AEL101+1), see `course_code.txt` refinement history.
Detail-course start rule (used by all runs): first `BSC101` code line on page >= 12 starts the detail region; each code's first occurrence on a page after the first `(Course|Lab) Objectives` line starts that Course (BSC101 itself is exempt); the Course ends at the next Course's first code line. EXTC p14 interleaves the tail of the scheme table (PCL201X/PCL2016 rows) with the BSC101 course.

## Title wrapping
Title = text after the code on the same line, plus following non-blank lines until a blank, `--`, `-`, or a pure number line (max 4 lines). Blank lines can sit between code and title (VSEC102: `'VSEC102 '`, `' '`, `'C Programming '`). Footnote marks stick to the title in one table: `'Induction cum Universal Human Values 2#'` (CC101), `'Indian Knowledge System 2*'` (IKS201). Titles differ between the two tables in 15/210 occurrences (truncated 'Professional' for AEC101; 'Lab' missing and hyphen spacing for BSL2022; BSC2032 has one code occurrence only in AIML, CSE-AIML, DS and IT). Coverage 195/210 (PARTIAL); evidence `regex_runs/nep26-fe-sem12_title.txt`.

## Module row pattern
The module table starts at a line `Detailed Content` (spellings seen: `Detailed Content`, `Detailed Contents`, `DetailedContent`, `DetailedContents`; one course uses header `Details`, PCC2018) after header words `Sr. / No. / Name of / Module / Detailed Content / Hours / CO / Mapping` (`LO` instead of `CO` in VSEC courses). Table text ends at a stop marker. Module rows come in these course-level variants (census per code: `regex_runs/nep26-fe-sem12_layout_variants.txt`; module-row coverage 140/144 course occurrences that have a table, 4 failures = IKS201 in AIML, CSE-AIML, DS, IT):
- `v-roman` (76 occurrences): a line with only a Roman numeral `I`..`VI`, then the module name on 1-3 short lines (can be hyphen-broken: `'Electrodynami'`/`'cs'`, `'Fundament'`/`'als of   C-'`), then content lines, then hours (`'04 '`) and `'CO1 '` lines AFTER the content. Example: dumps/nep26-fe-sem12_BSC102_p21.txt (`'I '`, `'Lasers'`, ..., `'04 '`, `'CO1 '`). Courses: BSC102, BSC103, ESC101, ESC201, CC101, BSC2021, BSC2031-2033, ESL201, PCC2011, PCL2011, PCL2016, PCL2018, IKS201.
- `v-arabic` (56): module number as `01`..`06` (maths/communication: BSC101, BSC201, AEC101, ESC102, with `1.1.`-style dotted items; AEC101 adds `'Module 1- '` before the name) or plain `1`..`6` (BSC2022, BSC2023, AEL101, VSEC102, VSEC202, PCC2016) or `1.` (PCC2018, header `Module / Details / Hrs.`).
- `v-trade` (12): rows `Trade-1`..`Trade-5` (VSEC101, VSEC201), sometimes split `'Trade-'` + `'2 '` or written `'Trade 4 '`; 5 rows but CO-1..CO-7 mapped to them (so max CO index is not the row count).
- `v-lab` (60): 10 lab courses per PDF without a module table: BSL101, BSL102, ESL101, ESL102, BSL2011-2013, BSL2021-2023; rows are `NN / experiment title / hours / LOn` under `Sr No / List of Experiments / Hrs / LO Mapping` (dumps/nep26-fe-sem12_BSL101_p24.txt).
- `v-none` (6): CC201 has neither (activity lists with `Sr No`).
Module numbers also collide with hours digits (`'01'` hours then `'I'`): a marker is accepted only if the next non-blank line has letters, is not a tail line and is not a Roman numeral (attempt-2 rule, see Failures).
Name/content boundary: UNKNOWN from line order alone (open_questions.md); the spike takes short leading lines as the name.

## Prerequisite row
Strict regex `^\s*(?:0\s+)?(?:No\s+)?[Pp]re-?requisites?\b` inside the table region: 76/144 course occurrences have one; 68 have none. Positions (`regex_runs/nep26-fe-sem12_prereq.txt`): before module 1 in 64 (Physics/Chemistry/Mechanics style `'Prerequisite '` with hours/CO `-- --`, or ESC101 style `'0 '` then `'Prerequisite '` then hours `'01 '`/`'CO1 '`, dumps/nep26-fe-sem12_BSC102_p21.txt shows `'Prerequisite '` at line 11 and `'-- '`,`'-- '` at 21-22); inside module text only in 12 (BSC101 modules 01 and 05: `'Pre-requisite: Review of Complex Numbers...'`). Spellings: `Prerequisite`, `Prerequisite:`, `Pre-requisite:`, `No prerequisite` / `no prerequisite` (CC101). All these rows are EXCLUDED from topics (also ESC201 line `Comment (Prerequisite syllabus should not be...` and ESC101 note `(Note: There will be no questions from the prerequisite...`, which the strict regex does not match; 12 loose-only lines listed as failures in the evidence file). The `0` in `'0 '` before `Prerequisite` is the module-number slot of the prerequisite row.

## Self-learning markers (all spellings seen)
Anchored regex `^\s*(?:#\s*[Ss]elf[\s-]*[Ll]earning\s+topics?\s*:?|[Ss]elf-study activities)`: 66/72 loose references (6 failures are one prose sentence in CC201). Spellings: `# Self-learning topic:` (12), `# Self-learning topics:` (24), `# Self learning topics:` (24, BSC201, no hyphen), `Self-study activities` (6, IKS201, a section after the table, hours `10`/`02`, not a per-module marker). Markers sit at the end of a module's content (BSC101, BSC201 only). Golden courses exclude them; whether they are Topics is an open question. Evidence `regex_runs/nep26-fe-sem12_self_learning.txt`.

## Hours / CO tail patterns
Whole-line tail regex `^\s*(?:(?:CO|LO)\s?\d+(?:\s*[,&/]\s*(?:CO|LO)?\s?\d+)*\s*,?|\d{1,2}|--|-|,)\s*$`. In the table region 828/876 lines that contain `CO|LO` + digit are whole-line tails; the 48 non-tail lines are the prose notes `CO-1 is related to Trade-1` etc. in VSEC101/VSEC201 (verbatim in `regex_runs/nep26-fe-sem12_tail.txt`). Order is: hours digit line(s) (`'04 '`, or in maths `'2 '`, blank, `'1 '` where the meaning of the second number is UNKNOWN), then `CO1`; in VSEC102 `LO1`, `LO1, `; combined forms `CO1, CO2` exist; tails can precede or follow the content depending on column order (BSC101 p17: `'3 '`,`' '`,`'1 '`,...,`'CO2 '` after content). Stray numeral fragments (`II`, `I`, `V`) leak into IKS201 content.

## Stop markers
Regex `^\s*(?:Text\s?[Bb]ooks?|TEXT/REFERENCE BOOKS|References?|Online (?:References|Resources)|Assessment\s*:|Term ?[Ww]ork|List of Assignments|Sr\.? ?No\.? Website Name|Website Name)\b`: 144/144 course occurrences with a table (after 2 attempts). Spellings seen: `Text Books:`, `Text Books`, `Textbooks:`, `References:`, `Online References:`, `List of Assignments / Tutorials`, `Term Work: ...`, `Term Work in a group of 4 students.` (a Trade row sentence that matches too, VSEC201), `TEXT/REFERENCE BOOKS:-`. Note: bare `Internal Assessment` is NOT a stop (it is a table header of the following course interleaved before VSEC201's Trade rows, AIML p127:42). VSEC201's `Term Work in a group of 4 students.` (p128:49) lies INSIDE the Trade-5 row and is matched as a stop (so Trade-5 content is cut) - recorded oddity, not fixed.

## Watermarks / noise lines
- Page number: line 1 of every page is `^\d+\s*$` (e.g. `'16 '`); removed before parsing (dump lines 1 in dumps/nep26-fe-sem12_*).
- Blank lines `' '` are frequent (column padding).
- DRAFT watermark: none. The 5 `draft` hits per PDF (30 total) are `Drafting` / `drafting software` / `Basic information about the drafting software` etc. in Engineering Graphics (AIML p106:77 ...); evidence `regex_runs/nep26-fe-sem12_draft_watermark.txt` (lists all 30 lines).
- No repeated running header/footer other than table header words (`Course`, `Code`, `Course Name`, `Teaching Scheme`...) which repeat per course.
- Bullets are private-use glyphs ``, ``; `#` precedes self-learning; missing spaces in VSEC101/VSEC201 text (`Useandsettingoffittingtools...`).
- Broken syllable lines (`'Electrodynami'`/`'cs'`, `'Ter'`/`'m '`, `'Exa'`/`'m '`).

## Numbering styles (Roman / arabic / 1.1 / 1.)
Module numbers: Roman (`I`), zero-padded arabic (`01`), plain arabic (`1`), arabic with dot (`1.`), `Module 1- name`, `Trade-1`. Sub-items: `1.1.`, `1.1`, `3.1Equilibrium:` (no space), `4.1Maxima...`, `2.2.` alone on a line followed by text on the next line (BSC101 p17:10-11), none in the Roman physics style. Roman numerals can be split across two lines or even pages (IKS201, see oddities).

## Topic separators
Observed inside a module's content: comma, full stop, semicolon, colon after a heading (`Lasers: Spontaneous...`, `Online ...`), private-use bullets ``, dotted numbering `N.N`, `(i) (ii)` enumerations inside one line, `&`, ` – `. Because commas also occur inside one concept (`Cartesian, polar and exponential form of complex number`), splitting on commas over-splits. The spike splitter (`spikes/nep26-fe-sem12_extract.py` `topics_from`) splits on `[;,.:]`, ` - `, parentheses, bullets and dotted numbers and is used only for the census.

## Known oddities
1. Not duplicates: branch-specific course text and different PC (program core) courses (see PDFs section).
2. Placeholder `X` codes only in scheme tables; numbered variants (BSC2021..3, BSL2011..3, BSC2031..3, BSL2021..3) are Sem II electives, each is a full Course in every PDF.
3. IKS201 numerals: `II`+`I` (=III) and `I`+`V` (=IV) on adjacent lines; `V`+`I` (=VI) separated by a page break and content (AIML p122:147 and p123:3) -> module VI missed in 4 PDFs.
4. Lab-coded courses with module tables: AEL101 (arabic 1-6, stop `List of Assignments`), ESL201, PCL2011/2016/2018 (Roman).
5. Code wrap `BSC202`+`2`, `PCL201`+`8` (Mech p110) and one scheme row missing (BSC2032).
6. Scheme summary tables p8-14 list PCC2011/PCL2011 for EXTC and Mech while their detail courses are 2016/2018.
7. VSEC101/VSEC201 are Trade lists with missing spaces; hours sit under each trade; notes line `CO-n is related to Trade-m`.
8. CC201 has no module table.
9. Module-name hyphenation breaks (`Programmi`/`ng`).
10. Cross-check "modules found == numbered Course Outcomes" is NOT reliable (courses carry lab outcomes too) and is not used.

## Exact regexes with measured coverage (each links to docs/evidence/regex_runs/<file>)
| name | regex (abridged; exact text in the evidence file) | matched/total | status | file |
|---|---|---|---|---|
| detect | `As Per NEP 2020` (pages 1-2) | 6/6 PDFs | full | nep26-fe-sem12_detect.txt |
| draft_watermark | `\bDRAFT\b` | 0 lines (expected 0) in 6 PDFs; 30 case-insensitive 'Drafting' lines | negative check | nep26-fe-sem12_draft_watermark.txt |
| course_code | `^\s*([A-Z]{2,5}\d{3,4}[A-Z]?)(?![A-Za-z0-9])(.*)$` + join rule | 209/213 vs scheme-table expectation | PARTIAL (explained) | nep26-fe-sem12_course_code.txt |
| title | code line + following lines until blank/`--`/`-`/number | 195/210 | PARTIAL | nep26-fe-sem12_title.txt |
| table_hdr | `^\s*(?:Detailed ?Contents?\|Details)\s*$` | 126/132 non-lab-coded; 18 of 78 lab-coded also match | PARTIAL (CC201 x6) | nep26-fe-sem12_table_hdr.txt |
| module_row | Roman / `0?[1-9]\.?` / `Trade[\s-]*\d` sequence rule | 140/144 | PARTIAL (IKS201 x4) | nep26-fe-sem12_module_row.txt |
| prereq | `^\s*(?:0\s+)?(?:No\s+)?[Pp]re-?requisites?\b` | 76/144 (68 courses have none; 12 loose-only lines) | full on matched, 12 non-matching prose lines | nep26-fe-sem12_prereq.txt |
| self_learning | anchored `#\s*Self[\s-]*learning\s+topics?` or `Self-study activities` | 66/72 | 6 = prose (not markers) | nep26-fe-sem12_self_learning.txt |
| tail | `^\s*(?:(?:CO\|LO)\s?\d+(...)\|\d{1,2}\|--\|-\|,)\s*$` | 828/876 | 48 = prose notes | nep26-fe-sem12_tail.txt |
| stop | `^\s*(?:Text\s?[Bb]ooks?\|TEXT/REFERENCE BOOKS\|References?\|...)\b` | 144/144 | full | nep26-fe-sem12_stop.txt |
| lab_hdr | `^\s*List of Experiments` | 72/78 lab-coded | AEL101 x6 uses `List of Assignments` | nep26-fe-sem12_lab_hdr.txt |
| (diff) | course-set/text diff across PDFs | - | evidence | nep26-fe-sem12_pdf_diff.txt, nep26-fe-sem12_layout_variants.txt |
Important caveat: the `matched/total` of module_row, prereq, tail and stop use my own extractor as the system under test; the denominators are course occurrences with a table (144), not an independent module count. Ground truth for module content exists only for the 5 DRAFT golden courses (unsigned).

## Failures (verbatim, per regex, per attempt 1-3)
Each evidence file lists every failure verbatim (pdf | page:line | text) and a "refinement history" block. Summary:
- course_code: attempt 1 209/291 (expectation used a wrong join rule, false joins in the summary tables); attempt 2 209/213; remaining: EXTC/Mech `PCC2011`, `PCL2011` listed in scheme tables but absent as detail courses (2016/2018 instead) x4, EXTC `PCL2016` outside window x1.
- title: attempt 1 177/210; attempt 2 195/210 (blank lines skipped, footnote marks stripped); remaining 15: AEC101 truncated title x5 (all but DS), BSL2022 x6 (hyphen/Lab), BSC2032 single occurrence x4 (AIML, CSE-AIML, DS, IT); attempt 3 not made.
- table_hdr: 6 failures, all CC201 (no table), one per PDF.
- module_row: attempt 1 false accept in ESC201 (`01` hours as module 1), 0 modules for VSEC101/VSEC201/PCC2018, 2 for IKS201; attempt 2 fixed all but IKS201 (5 of 6 found in AIML, CSE-AIML, DS, IT: 4 failures, verbatim in the file); attempt 3 not made.
- prereq: 12 loose-only lines (ESC101 note x6 PDFs, ESC201 comment x6 PDFs).
- self_learning: attempt 1 72/72 but 6 false positives (CC201 prose); attempt 2 66/72 (the 6 are the prose lines).
- tail: 48 non-tail CO lines (VSEC101/VSEC201 notes).
- stop: attempt 1 143/144 (PCC2018 `TEXT/REFERENCE BOOKS:-`), attempt 2 144/144. Unfixed oddity: VSEC201 Trade-5 content contains `Term Work in a group of 4 students.` which matches the stop regex.
- lab_hdr: 6 failures, AEL101 (`List of Assignments / Tutorials`).

## Topic validity census (violations by rule id, total topics)
Evidence: `regex_runs/nep26-fe-sem12_topic_validity.txt`. Spike extractor (naive splitter, courses with module tables only; 66 occurrences (11 codes x 6 PDFs, 10 pure labs + CC201) excluded because they have no module table):
- total topics: 10267 (all PDFs x occurrences); valid 9507; with >=1 violation 760 (7.4 %).
- unique (course_code, topic) pairs 1712, 129 with violations.
- by rule id: R1_word_count_1_to_8 543; R2_len_over_80_chars 202; R3 0; R4_generic_heading 121; R5_procedural 6; R6 0; R7 0; R8_no_letters 78.
Interpretation: the low violation rate is about the splitter, not about topic quality; the splitter also emits fragments such as `with proof`, `by`, `1`, `Forward` (R8/R1 catch only part of them); a human-meaningful figure needs the golden courses. The 5 golden courses (267 topics) have 0 violations after one fix (`Expansion of sin nθ and cos nθ`).

## Golden courses (5, DRAFT) and how they were drafted
`tests/golden/nep26-fe-sem12/`: BSC101 (Applied Mathematics-I, v-arabic with dotted items and self-learning), BSC102 (Applied Physics, v-roman, comma-separated content), ESC101 (Engineering Mechanics, v-roman with `0`/Prerequisite row, `3.1` sub-items), VSEC102 (C Programming, v-arabic plain with LO tails and hyphen-broken names), IKS201 (Indian Knowledge System, odd: split numerals, bullets, from the EXTC PDF where K=6). Drafted by reading each course's module text via `spikes/nep26-fe-sem12_rawmods.py` (never the whole PDF) and typing atomic topics (1-8 words) by hand with `spikes/nep26-fe-sem12_write_golden.py`; excluded: prerequisite rows/text, self-learning topics, tail numbers, text-book lists, truncated trailing words (BSC102 module II ends in `numerical` cut by the source). Names of modules were typed from the raw name lines and are unverified. Status in every file: `DRAFT - needs human sign-off`. No lab golden course (no lab has modules; see UNKNOWN). Three dumps: BSC102 p21 (normal theory), IKS201 p122 (odd), BSL101 p24 lines 61-102 (lab), all from the AIML PDF, unedited.

## UNKNOWN items (also copied to docs/open_questions.md)
1. Hidden watermark layer not seen by `get_text()` (DRAFT hypothesis refuted for text).
2. Whether `nep26` in the family id is right (text says NEP 2020, AY 2024-25).
3. Whether self-learning topics and inline `Pre-requisite:` text are Topics (golden excludes).
4. Module name vs content boundary without bbox/font data.
5. Treatment of lab courses (experiment lists), CC201, and lab-coded courses with module tables.
6. Which PDF is authoritative for the same code with different content.
7. IKS201 module VI numeral detection; meaning of the two hour numbers in maths modules.
8. Authoritative table for the title (teaching vs examination scheme).
9. Whether the family-level detection separates this family from other NEP families.
