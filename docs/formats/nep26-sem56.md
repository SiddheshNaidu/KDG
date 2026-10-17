# Format: nep26-sem56
Status: PARTIAL   (module CO/LO tail regex 125/126 after 3 attempts; prerequisite-row regex 18/21 because 3 courses have no such row; module name vs content boundary UNKNOWN)

All run files live in `docs/evidence/regex_runs/` with prefix `nep26-sem56_`. Every regex below was run against every course by `spikes/nep26-sem56_runs.py` (command line is recorded at the top of each run file). Line numbers are 0-based indexes into `page.get_text().split("\n")`, pages are 1-based.

## PDFs in this family (path, pages, evidence file)
- `data/raw/_unclassified/SEM-V.pdf`, 128 pages. File name says "SEM-V" but the PDF covers Semesters V and VI together (evidence: `docs/evidence/regex_runs/nep26-sem56_detect.txt`, lines p1 line39 'V & VI', p2 line47 'Sem. V & VI'; course codes `2165xxx` are Sem V rows and `2166xxx` Sem VI rows, see `nep26-sem56_course_list.txt`).
- Branch: one programme only: "B.E. Computer Science and Engineering (Artificial Intelligence & Machine Learning)" (p2 lines 17-19 and p1, see `nep26-sem56_detect.txt`), from academic year 2026-27; "Major Vertical - 1, 4 & 5" and "Board of Studies in Computer Engineering" are on p1 (seen with `spikes/nep26-sem56_explore.py 1 1`, not saved as a dump). No other branch observed.
- Distinct courses holding a detailed-syllabus page: **30** = 29 numeric 7-digit codes + 1 letters+digits code (`IKS501`). Full list with codes, titles, page ranges: `docs/evidence/regex_runs/nep26-sem56_course_list.txt`. Breakdown: 15 theory courses with module table (6 Sem V + 8 Sem VI + IKS501), 6 labs that DO have a module table with "LO Mapping", 8 labs with only an experiment list, 1 mini project (`2166411`, no modules).
- Scheme tables (p6-p9) list 42 distinct 7-digit codes; 13 of them have no detail page (minor/bucket/IKS/professional skill rows and 6 typo'd `2175xxx` codes on p6): `nep26-sem56_course_header.txt`.
- Hint check: old repo said "~28 parseable courses"; observed 30 courses, 21 with a parseable module table.

## Detection (regex + coverage matched/total)
- `(?i)as\s+per\s+nep\s+2020` on lines of pages 1-3: **1/1 PDF** (p1 "As Per NEP 2020", p2 "(As per NEP 2020)"). Evidence: `nep26-sem56_detect.txt`. This only proves scheme NEP, not the family; family-level discriminators from the census (`docs/evidence/signatures.csv`, row `_unclassified/SEM-V.pdf`): 7-digit codes alone on 128 lines, "DETAILED SYLLABUS:" 21x, "Self-Learning Topics" 7x (census counts differ from line-regex counts because text is wrapped), 0 `Total Hours` lines.
- Hypothesis `nep26-sem56` from signatures.csv: CONFIRMED for the name (Sem V+VI NEP). Whether other PDFs belong to this family is UNKNOWN (only one PDF examined).

## Course header pattern
- Regex `^\s*(\d{7}|[A-Z]{3}\d{3})\s*$` (code alone on a line). The first occurrence on a page >= 10 starts the course; the course runs to the page before the next course's first occurrence. 30/30 courses start this way; 29/42 scheme-table codes have a detail header, the 13 others are listed verbatim in `nep26-sem56_course_header.txt` (not regex failures: those courses have no detail page). The code reappears 2-3 more times per course in the scheme tables (teaching scheme, examination scheme), so only the FIRST occurrence is the header.
- The "Course / Code / Course Name / Teaching Scheme..." tables are emitted by PyMuPDF in a different order from the visual order: on the course's first page they sit at the end of the page text (e.g. 2165112 p16: code at line 50, after course objectives and the DETAILED SYLLABUS line), and in 8 courses they are inserted INSIDE the module table text (see Watermarks/noise). Evidence: `nep26-sem56_noise.txt`.

## Title wrapping
- Title = lines after the first code line, joined, until a line of only digits/dashes (`^[\d\-–—]+$`) or a blank line; a line ending in `-` is joined without a space (e.g. "Mini Project-" + "II"). A title wraps over 1-4 lines (e.g. 2165111 "Statistics for / Machine Learning / and Data Science"). Cross-check against the same procedure on the p7/p9 scheme rows: **27/29** numeric-code courses agree; the 2 mismatches are caused by the scheme-table row being followed by text rather than numbers (2165116 and 2166123), recorded verbatim in `nep26-sem56_title.txt`. Titles differ between tables in "&" vs "and" and hyphen/space ("Nature- inspired" in 2166123 header vs "Nature-Inspired" elsewhere). Normalisation needed before comparing titles.
- IKS501 has a different title wrap: "Indian Knowledge / System".

## Module row pattern
- Module table starts at `(?i)^\s*detailed\s+syllabus\s*:?\s*$` (21/21 courses with module table; the other 9 courses have no such line, each shows an experiments-list or project-guidelines marker: `nep26-sem56_ds_marker.txt`). Spellings seen: "DETAILED SYLLABUS:", "Detailed Syllabus:".
- The column-header block (Sr. / No. / Name of Module / Detailed Content / Hours / CO Mapping) follows; its end is the first line matching `(?i)^\s*(C[O0]|LO)(\s+mapping)?\s*$` after the marker, plus an optional line `Mapping`. Needed because on a course's first page the DETAILED SYLLABUS line is followed by the scheme tables whose cells include a lone `I` (from "IAT-" / "I") that would otherwise be read as module I (attempt 1 of `module_roman` failed 2 courses: 2165115 and 2166111, see below).
- Module row start: a line that is exactly the next expected Roman numeral `^\s*(I|II|III|IV|V|VI|VII|VIII)\s*$`. Every course with a module table has exactly 6 modules I..VI, in order: **21/21** courses, 126 module rows (`nep26-sem56_module_roman.txt`).
- A row's text, in line order: Roman numeral, module name (wrapped over narrow lines), module content, optional self-learning text, then an Hours line and a CO/LO line. Row ends at the next Roman numeral (or stop marker).
- The module NAME and the CONTENT are not separated by any marker; the boundary is UNKNOWN. Evidence that block mode does not solve it: `page.get_text("blocks")` yields a block starting with a Roman numeral for only 4/21 courses' rows in full count (`docs/evidence/regex_runs/nep26-sem56_blocks_check.txt`).
- A row can be split by a page break: Hours + CO lines are emitted at the bottom of the first page, and the rest of the content continues at the top of the next page BEFORE the next Roman numeral (e.g. 2165111 module III: `08`, `CO3, CO6` at p12 lines 125-126, then "(overview)." ... at p13 lines 1-12; dump `docs/evidence/dumps/nep26-sem56_2165111_p12.txt` shows the end of that page). So row text = all lines between Roman N and Roman N+1 with the tail lines removed, not "lines before the tail".
- Row with no tail at all: 2166116 module VI (see oddities).

## Prerequisite row
- Row "0": first non-blank line of the module region equals `^0+$`, then optional label `(?i)^\s*pre-?\s*requisites?\s*$`, then free text (wrapped), then a hours cell such as `00`, `01`, `-`. Matched **18/21** courses (`nep26-sem56_prerequisite_row.txt`): labelled "Prerequisite" 16, labelled "Pre-Requisite" 1 (2165114, followed by the word "Topics"), unlabelled 1 (2166111, just `0` then text). 3 courses have NO such row (2165116, 2166113, IKS501), verified: the region begins directly with `I` (or table header cells for IKS501). Failures listed verbatim in the run file.
- Front-matter "Prerequisite:" line (before the module table, theory/lab pages): `(?i)^\s*pre-?\s*requisites?\s*:` found in 9/30 courses (`nep26-sem56_prerequisite_frontmatter.txt`); for 2166116 the line is "Prerequisite:" with the text on following lines.
- The module rows and the "0" row text is NOT module content; exclude it from topics.

## Self-learning markers (all spellings seen)
- Regex `(?i)\bself[\s\-–]*(learning|study)\b`: **125/126** modules contain one. The 1 miss is IKS501 module II (no marker in its text; checked: row ends "Konark Sun Temple", `10`, `CO2`). Evidence: `nep26-sem56_self_marker.txt`.
- Spellings (count of modules): "Self-learning" 109, "Self-Learning" 11, "Self- learning" 4 (space after hyphen), "Self-Study" 1 (IKS501 module I, `Self-Study:`). Continuations: "Self-learning Topics:", "Self-learning Toics:" (typo, 2165114 II), "Self-Learning :" (space before colon, 2166111), "Self-Learning:" (IKS501 III, bullets follow), "Self-Learning Topics and Activities:" (IKS501 IV-VI), the marker split over two lines ("Self-learning" / "Topics:") in 2165111.
- The self-learning text is the last part of the row content; everything from the marker line to the end of the row (except Hours/CO lines) is self-learning and must be excluded from topics (old-repo hint "Self-Learning Topics: excluded" holds). Its text can contain URLs split across lines and a stray hours number (2166116 VI: the `06` appears inside the self-learning text).

## Hours / CO tail patterns
- Theory courses (15): Hours = digit-only line `^\s*\d{1,2}\s*$` immediately before the CO line: **89/90** modules (`nep26-sem56_hours.txt`); the miss is 2166116 VI (no CO line, and its `06` is not directly followed by a CO line). Hours are 1 or 2 digits, zero-padded in some courses ("07") and not in others ("6"). IKS501 shows `10` for all 6 modules.
- CO tail: after 3 attempts `^\s*((C[O0]|L[O0])\s?\d+(\s*(,|&|-|–|to|and)\s*((C[O0]|L[O0])\s?)?\d+)*)\s*$` matches **125/126** modules (`nep26-sem56_module_tail.txt`). Spellings: "CO1", "CO 1", "CO1, CO6", "C03" (digit zero, 2166113 III), "LO 1", "LO1", "LO1,LO2", "LO2, LO3", "L06" (2166120 VI). Attempt 1 `(CO|LO)\s?\d+...` = 123/126, attempt 2 adds `C[O0]` = 124/126, attempt 3 adds `L[O0]` = 125/126. One failure remains: 2166116 module VI (p86 line 81) has no CO line in the PDF text.
- The 6 labs with module tables have LO (not CO) in the tail and NO Hours column; a digit-only line before an LO line is content (2166122 III: "OWASP Top" / "10"). Hours must only be read when the tail starts with C. Measured: 0 hours extracted from the 36 lab module rows.
- Old-repo hint "Total Hours": 0 lines match `^\s*Total Hours?\s*$` in this PDF (`nep26-sem56_stop_marker.txt`, `nep26-sem56_noise.txt`).

## Stop markers
- Module table ends at the first line matching `(?i)^\s*(text\s*(and\s+reference\s+)?books?\b|books\s*:)`: **21/21** courses with module table (`nep26-sem56_stop_marker.txt`). Attempt 1 `^\s*Text\s*Books?\b` matched 18/21, failing 2165115 ("Textbooks:"), IKS501 ("Text and Reference Books or Articles:") and 2166115 (only "Books:" on its own line, p83 line 1). Spellings seen: "Text Books:", "Text Books", "Textbooks:", "Books:", "Text and Reference Books or Articles:".
- The 9 courses without module table: only 5/9 have such a line; for these the section ends at `Assessment` / `Term Work` text or at the end of the course pages (not parsed; `stop_marker` file lists the 4 without a line: 2165121, 2165122, 2166411, 2166125).
- After the stop marker: textbooks, references, online references, "Assessment:", then a question-paper template page (14 pages: 15, 19, 23, 27, 31, 35, 65, 70, 74, 79, 84, 88, 92, 96; marker "Note for QP Setters") that must be ignored.

## Watermarks / noise lines
- No watermark, no page numbers, no running header/footer: no non-trivial line repeats >= 60 times, "draft" occurs once and is a bibliography entry ("MIT Press Draft", p41 line 14), not a watermark (`nep26-sem56_noise.txt`). The census "DRAFT 1x" is therefore a false positive.
- Inserted scheme tables: in 8 of the 21 courses with a module table, 9 blocks (2165113, 2165115 twice, IKS501, 2166112, 2166113, 2166116, 2166118, 2166122) the teaching-scheme table text ("Course / Code / Course Name / Teaching Scheme / (Contact Hours) / Credits Assigned / Theory / Pract. / Tut. ... / <code> / <title> / 3 - - 3 - - 3") appears in the middle of a module row. It must be removed: block starts at a line `Course` followed by `Code`, ends after the code line, the title lines and the following run of lines matching `^\s*([\d\-–—]+|)\s*$`. Counts per course in the noise file. After removal the topic validity census has 1 R7 hit, a genuine "Hours" word in 2165113 IV content (before the removal rule was added, R7 hits were observed in interactive runs that were not saved).
- Blank/space-only lines everywhere; near-empty pages (p53 holds only the word "IKS", see `spikes/nep26-sem56_explore.py 53 53`; p61 has 28 mostly blank lines).
- Table cells such as "Pract" / "." / "Oral" are split over lines; irrelevant inside module rows after the table removal.

## Numbering styles (Roman / arabic / 1.1 / 1.)
- Modules: Roman numerals I..VI (all 21 courses).
- Inside content: unnumbered in 14 of 21 module-table courses. Numbered in: "1.1 / 4.1" dotted arabic (IKS501, 2166111, 2166115: 48 lines), "I.1" dotted Roman (IKS501: 3 lines), "1." (2165114 3, IKS501 18, 2166111 21, 2166112 14, 2166115 16, 2166120 16), "a)" letters (IKS501 4), bullet glyph `•` alone on its own line (IKS501 43 lines). Some have no space after the number ("2.Regression Models", "3.2Dragonfly Algorithm"). Evidence: `nep26-sem56_noise.txt`.

## Topic separators
- Observed (from the dumps and `spikes/nep26-sem56_topics.py --show <code>`): comma (most common), period + space between topic groups, colon between a heading and a list ("Types of data: categorical, numerical, ordinal."), semicolon (2166116 IV, 2165114 front-matter), en dash ("Mann- Whitney U"), arrows "→" in lists, bullets `•` one per line (IKS501), numbered sub-items. Content wrapped: words split one per line when the cell is narrow ("Poisson, / Exponential, / Uniform,"), hyphenation at line end ("chi- / square", "Mann– / Whitney").
- Whether "A, B, C after a colon" are separate Topics or one bundle is a human decision (see `docs/formats/topic_validity.md` R3); the goldens split them.

## Known oddities
1. File name SEM-V.pdf but contains Sem V and VI; family id kept as `nep26-sem56`.
2. Module name and content are concatenated with no separator (name boundary UNKNOWN); block mode does not separate them reliably (4/21).
3. Row split by page break: Hours/CO emitted before the tail of the content (2165111 III p12/p13).
4. 2166116 module VI: hours `06` appears AFTER the first page of self-learning text, the final word "applications." is on the next page followed directly by "Text Books:"; no CO line exists (dump `nep26-sem56_2166116_p86.txt`, lines 55-56 of the dump).
5. Typos: "C03" (2166113 III), "L06" (2166120 VI), "Toics" (2165114 II), "IInterfacing" (2166116 IV content), "Textbooks:" / lone "Books:".
6. Labs come in 3 layouts: (a) module table with LO tail and no hours (6 labs: 2165119, 2166120, 2166121, 2166122, 2166124, 2166126), (b) only an experiment list (8 labs) in 4 sub-layouts: rows "01 / text / 02(hrs)" (2165117, 2165118, 2165121), "01 / text / LO1" (2165122, 2166125), "1. / text / 02" (2166119), "Sr.No / Experiment Title / Mapped LO" (2166123); 2165120 has "Suggested List of experiments:" with no "List of Experiments" row header, (c) mini project 2166411 with objectives/guidelines only.
7. IKS501 has letters+digits code, "Self-Study:"/"Self-Learning:" markers, bullet-per-line content, "I.1" numbering, every module 10 hours, module II name is only "Tradition" in the text (full name UNKNOWN), its code does not appear in the scheme tables (they list `2165511` "Indian Knowledge System" instead) and its tables use "Test 1 / Test 2" instead of "IAT".
8. Scheme table p6 lists Sem V elective codes as `2175114...2175122` while p7 and the detail pages use `2165114...2165122` (probable typo in the PDF; `nep26-sem56_course_header.txt`).
9. Course 2165114 uses a different table dialect: header "Module Title / Contents of the module / Hours / CO", "Pre-Requisite / Topics", hours "03", "IA-1/IA-2".
10. Course pages start where the first code occurrence is; a course can start with objectives (2165112 p16) because header tables are emitted at the end of the page.
11. The DETAILED SYLLABUS line can come before the course's scheme tables on the same page (2166111 p62), then the module table starts on the next page (p63).

## Exact regexes with measured coverage (each links to docs/evidence/regex_runs/<file>)
| name | regex | matched/total | file |
|---|---|---|---|
| detect | `(?i)as\s+per\s+nep\s+2020` | 1/1 PDF | `nep26-sem56_detect.txt` |
| course header | `^\s*(\d{7}\|[A-Z]{3}\d{3})\s*$` | 30/30 courses start; 29/42 scheme codes have detail page | `nep26-sem56_course_header.txt` |
| title (procedure) | lines after code until `^[\d\-–—]+$`/blank | 27/29 vs scheme table | `nep26-sem56_title.txt` |
| DS marker | `(?i)^\s*detailed\s+syllabus\s*:?\s*$` | 21/30 courses (9 have no module table, 9/9 explained) | `nep26-sem56_ds_marker.txt` |
| module roman | `^\s*(I\|II\|III\|IV\|V\|VI\|VII\|VIII)\s*$` with column-header-end rule | 21/21 courses, 126 rows | `nep26-sem56_module_roman.txt` |
| CO/LO tail | `^\s*((C[O0]\|L[O0])\s?\d+(\s*(,\|&\|-\|–\|to\|and)\s*((C[O0]\|L[O0])\s?)?\d+)*)\s*$` | 125/126 modules (PARTIAL) | `nep26-sem56_module_tail.txt` |
| hours | `^\s*\d{1,2}\s*$` line before CO tail | 89/90 theory modules | `nep26-sem56_hours.txt` |
| prerequisite row | first region line `^0+$` + optional label | 18/21 (3 absent) | `nep26-sem56_prerequisite_row.txt` |
| prerequisite front matter | `(?i)^\s*pre-?\s*requisites?\s*:` | 9/30 courses (optional) | `nep26-sem56_prerequisite_frontmatter.txt` |
| self marker | `(?i)\bself[\s\-–]*(learning\|study)\b` | 125/126 modules (1 absent) | `nep26-sem56_self_marker.txt` |
| stop marker | `(?i)^\s*(text\s*(and\s+reference\s+)?books?\b\|books\s*:)` | 21/21 module courses; 5/9 others | `nep26-sem56_stop_marker.txt` |
| scheme-table strip | `Course`+`Code` ... see Watermarks/noise | 8 courses / 9 blocks affected (procedure) | `nep26-sem56_noise.txt` |
| topic validity | `spikes/topic_validity.py` | see census | `nep26-sem56_topic_validity.txt` |

Course list (30, codes + titles): `docs/evidence/regex_runs/nep26-sem56_course_list.txt`.

## Failures (verbatim, per regex, per attempt 1-3)
- module_tail attempt1 (123/126): 2166113 III (p72 line32) last lines `'8'`, `'C03'`; 2166116 VI (p86 line81) last lines `'06'`, `'applications.'`; 2166120 VI (p105 line20) last lines `'Self- learning Topics: Storytelling with dashboards'`, `'L06'`.
- module_tail attempt2 (124/126): 2166116 VI (as above); 2166120 VI (`'L06'`).
- module_tail attempt3 (125/126): 2166116 VI (p86 line81): no CO/LO line in the text, last non-blank lines `'EdgeX Foundry to develop AI-enabled edge'`, `'06'`, `'applications.'`. NOT FIXABLE by regex: marked PARTIAL.
- module_roman attempt1 (region from the DETAILED SYLLABUS line): 19/21 same as final; failures 2165115 (first row start p28 line 99 vs p29 line 2) and 2166111 (p62 line 85 vs p63 line 15), where a lone `I` from a table cell ("IAT-" / "I") is picked as module I. Fixed in attempt2 by the column-header-end rule (21/21).
- stop_marker attempt1 (18/21): 2165115, IKS501, 2166115. Fixed by attempt2 (21/21).
- hours: 2166116 VI (no CO line, `06` not adjacent to one).
- prerequisite_row: 2165116 (region begins `I`), IKS501 (region begins `Course`), 2166113 (region begins `I`): rows absent, not regex errors.
- self_marker: IKS501 II absent in PDF.
- title: 2165116 and 2166123 cross-check mismatches (scheme-table layout), not title errors.
Full verbatim lists with pdf/page/line are in the run files.

## Topic validity census (violations by rule id, total topics)
Evidence: `docs/evidence/regex_runs/nep26-sem56_topic_validity.txt` (spike `spikes/nep26-sem56_topics.py`, rules from `spikes/topic_validity.py`). This census uses a NAIVE splitter (split on `; : , . –` after removing numbering/bullets), not a parser, over the 21 courses with module table (126 modules); the module NAME is included in the first topic because the boundary is UNKNOWN.
- total topics: 1931
- violations by rule: R1_word_count_1_to_8: 98, R2_len_over_80_chars: 28, R3: 0, R4_generic_heading: 17, R5_procedural: 8, R6_leading_numbering: 12, R7_hours_or_CO_leak: 1, R8_no_letters: 3 (Greek letters alpha/beta/delta in 2166115 III).
- Notes: R6 hits are "2.Regression Models"-style numbering with no space (splitter artifact); R7 hit is the legitimate word "Hours" (2165113 IV "Ideal Time, Hours"); R5 hits include rule false positives such as "Experiment tracking".
- Golden drafts: 0 violations over the 5 drafted courses (`nep26-sem56_golden.py` prints the check).

## Golden courses (5, DRAFT) and how they were drafted
All in `tests/golden/nep26-sem56/`, status "DRAFT - needs human sign-off". Drafted by reading each course's own module text (`spikes/nep26-sem56_topics.py --show <code>`), splitting lists after colons into separate atomic topics, dropping self-learning text, hours and CO, then checking each topic with `validate()`.
- `2165111` Statistics for Machine Learning and Data Science: normal theory course, 6 modules, 182 topics. Dump: `docs/evidence/dumps/nep26-sem56_2165111_p12.txt`.
- `2166116` Edge Computing: odd theory (module VI without CO line, hours inside self-learning text, "IInterfacing" typo), 6 modules, 64 topics. Dump: `docs/evidence/dumps/nep26-sem56_2166116_p86.txt` (lines 37-96 of p86).
- `IKS501` Indian Knowledge System: odd theory (Self-Study, bullets, I.1 / 4.1 numbering, letters code), 6 modules, 86 topics; module II name is only "Tradition" as extracted.
- `2165119` Agile Software Development & DevOps Lab: lab WITH module table (LO tail, no hours), 6 modules, 82 topics.
- `2165117` Statistics for ML and DS Lab: lab with only an experiment list; modeled as 2 pseudo-modules `E` (List of Experiments) and `A` (List of Assignments / Tutorials), topics derived from experiment titles (concept names, not "implement ..." sentences), 58 topics. Dump: `docs/evidence/dumps/nep26-sem56_2165117_p37.txt` (lines 33-92). Whether lab experiments should become Topics at all is UNKNOWN.
Not human verified; module names for courses where the name/content boundary is ambiguous were chosen by the drafter.

## UNKNOWN items (also copied to docs/open_questions.md)
1. Exact module name vs module content boundary (no marker; block mode separates in 4/21 only).
2. Whether the lab experiment lists (8 labs with no module table, 4 layouts) and the mini project should yield Topics.
3. Whether other PDFs belong to family nep26-sem56 (only SEM-V.pdf examined).
4. Full module II name of IKS501 (only "Tradition" extracted).
5. Which course code is authoritative where the scheme table (p6 `2175xxx`, `2165511`) disagrees with the detail pages (`2165xxx`, `IKS501`).
6. Whether the 7 courses listed in the scheme tables without a detail page (2165211, 2165212, 2165311, 2165511, 2166211, 2166212, 2166511) are intentionally absent (minor, bucket, IKS, professional skill).
