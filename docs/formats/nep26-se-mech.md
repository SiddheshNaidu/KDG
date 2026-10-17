# Format: nep26-se-mech  (sub-families nep26-se-mech-a and nep26-se-mech-b)
Status: PARTIAL   (regex coverage target not met after 3 attempts for region_start, region_stop, module_marker, hours_tail, co_tail; every failure is listed verbatim in the evidence files. Hypothesis from signatures.csv is CONFIRMED for NEP-2020 SE Mechanical but REFUTED for "DRAFT watermark", see Watermarks.)

All counts below were produced by `PYTHONIOENCODING=utf-8 python spikes/nep26-se-mech_regex.py` (and sibling spikes `_stats`, `_draft`, `_topics`, `_dump`). Evidence dir: `docs/evidence/regex_runs/nep26-se-mech_*.txt`.
Unit of coverage: the 34 courses (17 per PDF) unless stated. Course boundaries come from `^Credits Assigned\s*$` on a page with index >= 15 (pages 1-14 do not match it: `nep26-se-mech_stats.txt`).

## PDFs in this family (path, pages, evidence file)
| sub-family | path | pages | courses | evidence |
|---|---|---|---|---|
| nep26-se-mech-a | `data/raw/2019-scheme/Mechanical-Engineering/6.35-N-B.E.-Mechanical-EngineeringSem-III-IV.pdf` (Item 6.35 (N), B.E. Mechanical Engineering) | 83 | 17 (start pages 16,20,23,27,30,35,41,45,50,55,59,63,66,68,72,76,79) | `docs/evidence/signatures.csv`, `nep26-se-mech_course_code.txt`, `nep26-se-mech_title.txt` |
| nep26-se-mech-b | `data/raw/2019-scheme/Mecanical-Automation-Engineering/6.44-N-B.E.-Mecanical-Automation-Engineering-Sem-III-IV.pdf` (Item 6.44 (N), B.E. Mechanical and Automation Engineering) | 76 | 17 (start pages 16,20,23,27,30,33,38,42,46,50,54,58,61,63,66,69,72) | same |

Folder name `2019-scheme` is a misnomer: page 1-6 of both PDFs say "As Per NEP 2020" (`nep26-se-mech_nep_banner.txt`, 2/2 PDFs). Course codes (7 digits): a = 24xxxxx / 29xxxxx, b = 23xxxxx / 29xxxxx (titles list in `nep26-se-mech_title.txt` note).

Sub-family split (measured, `nep26-se-mech_stats.txt`): every course-start page of b (17/17) has an extra 3-column block `Course Code / Course Name / Credits` (line `Credits` alone) before the "Teaching Scheme" block; a has it 0/17. Module tables are the same layouts in both. Raw dumps: `docs/evidence/dumps/nep26-se-mech_a-2403112_p21.txt` (a, module table), `nep26-se-mech_b-2393112_p20.txt` (b header with the Credits block), `nep26-se-mech_a-2403113_p24.txt` (odd Roman layout), `nep26-se-mech_a-2403115_p31.txt` (lab).

## Detection (regex + coverage matched/total)
- `As Per NEP 2020` (re.I, pages 1-6): 2/2 PDFs (`nep26-se-mech_nep_banner.txt`).
- Sub-family: b iff the course-start page has a line `^Credits\s*$` (17/17 b, 0/17 a).
- Course-start page: `^Credits Assigned\s*$`, pages >= 15: 34 starts found (17+17); pages 1-14 have 0 matches.
- Not detected: "Total Hours" (see below) and "DRAFT" (absent).

## Course header pattern
Regex `^\s*(\d{7})\s*$` : first match is on the course-start page for 34/34 courses (`nep26-se-mech_course_code.txt`). In the header the code line is followed by the title lines, then the credit columns. Header block (a, e.g. p16/p20/p23): lines `Course`, `Code`, `Course Name`, `Teaching Scheme`, `(Contact Hours)`, `Credits Assigned`, `Theory`, `Pract.`, `Tut.`, `Theory`, `Pract.`, `Tut.`, `Total`, then code, title lines, credit values; a second block (Theory/Term work/Pract/Oral/Total, Internal Assessment, End Sem Exam) repeats code and title. Header evidence: line index probes were run with `spikes/nep26-se-mech_show.py` (not saved as dumps); saved dumps cover body pages (a-2403112_p21, a-2403113_p24, a-2403115_p31) and the b header (b-2393112_p20). Header order is NOT always page order: b:2393114 puts the module table (line idx 45) before the header block (idx 92) on page 27 (`nep26-se-mech_stats.txt`, last section).

## Title wrapping
Title = lines between the first 7-digit code line and the first line matching `^\s*(?:\d{1,2}\*?(?:\+\d)?|-{1,2})\s*$` (a credit/dash value). 34/34 courses give 1-3 lines (`nep26-se-mech_title.txt`; all 34 titles listed in its header). Wraps are 2 lines in most (`Strength of / Materials`, a p20), 3 lines for `Environmental / Science for / Engineers` (b:2393512). Titles differ between PDFs for the same subject: a `Materials Testing`, b `Material Testing Lab`; a `Environmental Science`, b `Environmental Science for Engineers`.

## Module row pattern
Module marker, 4 styles (`nep26-se-mech_module_marker.txt`; style chosen per course = style giving most consecutive markers 1,2,3..):
| style | line | courses (of the 29 with a region and >=1 marker) | example |
|---|---|---|---|
| roman | `^(I|II|III|IV|V|VI)(?:\s*$|\s+[A-Z][A-Za-z])` | 22 | Thermodynamics a:2403113 dump a-2403113_p24 (lines 21 and 47 are `I`,`II`; `III Metal Forming` shares a line in b:2394112) |
| dotted | `^([1-9])\.\s*$` | 3 | Strength of Materials a:2403112 dump a-2403112_p21 (lines 0 and 14 are `2.`,`3.`; `1.` is on p20) |
| zero_module | `^0([1-9])\s*$` AND next line `^Module\s*:` | 2 | Engineering Mathematics-III (a:2403111, b:2393111) |
| bare | `^([1-9]|10)\s*$` AND next line starts with a letter, not a CO/LO tail, not a roman numeral | 2 | a:2404114, b:2394114 (Manufacturing Processes Lab, modules 1-6) |
Within a dotted/zero_module module, sub-items are `^\d\.\d+\.?\s` (e.g. `1.1`, `4.1.`).
Per course: 6 markers in 28 courses; labs with experiment-tables differ (see Oddities). The module NAME may wrap over 1-4 lines, may repeat as the first body sub-heading (Thermodynamics), and its second half can appear after the CO tail (b:2394112 module 3 `and / Sheet metal / working / processes` after `C03`, module 4 `Machining / Processes`).

## Prerequisite row
Spellings of a prerequisite line (`nep26-se-mech_stats.txt`): `Prerequisite` (20 lines/20 courses, always the Sr.No `0` row: line `0` immediately followed by `Prerequisite`, 20 courses), `Prerequisite:` (12), `Pre-requisites:` (2), `Pre-requisite:` (1) plus inline `Prerequisite: <text>` (3). Two placements: (1) header text block before the syllabus table (e.g. `Pre-requisite: Applied Mathematics-I, ...` b:2393111 p16), (2) table row `0 | Prerequisite | <text>` between the table header and module I (e.g. dump a-2403113_p24 lines 9-20 (`0`, `Prerequisite`, text)). The row is not a module.

## Self-learning markers (all spellings seen)
Strict regex `^Self[- ]learning [Tt]opics?\s*:?` matches 28 lines; broad detector `(?i)self[\s\-]*(?:learning|study)` finds 38; the other 10 are prose (objective/instruction sentences: `...self-learning topic. Students should prepare`, `To inculcate the process of self-learning and research.` etc., all listed verbatim in `nep26-se-mech_self_learning.txt`; coverage 28/38 line-level, 0 real markers missed by inspection of that failure list). Spellings: `Self-learning Topics:` (26 lines) and `Self-learning topics:` (2 lines; verified by counting the strict-regex match text) -- no `Self Study` and no `Self-Learning` capitalised-L variant seen in this family. Courses with markers: a:2403111 a:2994511 a:2994512 b:2393111 b:2394511 b:2394512 (Math, Business Model Development, Design Thinking). The marker paragraph can be at a page top (b:2393111 module 4: p18 line 0) and can contain URLs (a:2994511/2).

## Hours / CO tail patterns
- Hours: whole-line `^\d{1,2}\.?\s*$|^-\s*$` e.g. `05`, `6`, `04.` (Math module 6), `-` (industrial visit). Hours-like lines >= module count in 29/34 courses (`nep26-se-mech_hours_tail.txt`; failures = 3 no-region courses + 2 labs with no module table).
- CO/LO tail: `CON` 50 lines, `LON` 70, `LN` / `LN, LN(, LN)` 28 (Business Model/Design Thinking: `L1, L2`, `L2, L3,` wrapping), and typo `C0N` (zero) 4 lines (`C02`,`C03` in a:2404112 and b:2394112). Regex `^(?:C[O0]|LO|L)\s?[1-9]\b|^L\d(?:,\s*L?\d)*,?\s*$` OR a bare digit directly after a `^0\d$` line matches 28/34 (3 attempts, `nep26-se-mech_co_tail.txt`). Bare digits as CO column (a:2403114, a:2404113, b:2393114, b:2394113 use `1`..`6` after the hours value) are only matched by the third attempt.
- Table header spellings for the hours/CO columns: `Hrs`(31) `Hours`(23) `Hour`+`s`(2, split) `Hrs.`(1) `CO`(12) `LO`(12) `Mapping`(19) `Mapp`+`ing`(4). Math tails precede the next module header (UNKNOWN assignment rule, open_questions).
- `Total Hours` : regex `^Total Hours?\b` matches 4/34 courses (Math and Strength of Materials in both PDFs), as `Total Hours` + value on the next line (Math, a p18 line 33-34) or `Total Hours 39` on one line (SOM). 30 failures listed in `nep26-se-mech_total_hours.txt`: the line is simply absent (UNKNOWN whether totals exist elsewhere).

## Stop markers
Region = from START to first STOP. START (attempt 2): `^(?:Module\s+)?Detailed Contents?\s*$|^DETAIL(?:ED)? SYLLABUS|^Sr\.\s*$|^Part \(A\)\s*$` matches 31/34 (attempt 1 without `Part (A)`: 29/34). STOP: `^(?:Text ?Books?:?|Reference Books|References:?|Total Hours.*|Online (?:References|Resources):?|Links:|Assessment\s*:?|List of Experiments\.?|Part \(B\))\s*$` matches 31/34. First STOP line seen: `Text Books:` 16, `Online Resources:` 4, `Total Hours`/`Total Hours 39` 4, `Reference Books` 2, `List of Experiments` 2, `References:` 2, `References` 1 (`nep26-se-mech_stats.txt`). Failures (3): mini projects a:2403611 and b:2393611 (no syllabus table) and b:2393115 (lab with `Expt. No. | Description` table, no DETAILED SYLLABUS header). Note a lab region ends early at `List of Experiments` for 2 courses (a:2404115, b:2394115): these report 0 module markers (module_marker 29/34).

## Watermarks / noise lines
- DRAFT watermark: NOT present. `(?i)DRAFT` matches 6 lines, all the word "drafting" in running text (a p36, p39, p73; b p34, p37, p67); `DRAFT` case-sensitive 0, `^\s*DRAFT\s*$` 0 (`nep26-se-mech_draft_watermark.txt`). The signatures.csv count of 3 is a false positive of `re.I` substring search.
- Blank or space-only lines: 1265 of 10667 raw lines (both PDFs). Bullet glyphs: U+F0B7 25, U+25CF 75 (`nep26-se-mech_stats.txt`). No repeated page header/footer text: no non-numeric line occurs on >=25 pages (only lone `2`, 38/34 pages, a table value).
- Tail/column header fragments appear as lines: `Mo / dule`, `H / rs / .`, `Mapp / ing`, `Hour / s`, `Mappin / g`.
- Text damage: letter-spaced `e ve n` (b:2393111 p17), glued words `Introductionandclassificationofmetalworkingproces / ses` (b:2394112 p55, a:2404112), `Highgradeandlow- / gradeenergy,...` (a:2403113 p24), Unicode math glyphs (a:2403111 p17) which fail rule R8.

## Numbering styles (Roman / arabic / 1.1 / 1.)
Modules: Roman 22, `N.` 3, `0N` + `Module:` 2, bare arabic 2 (table above); no regex-detected region for 3 courses (mini projects x2, b:2393115) and 2 labs report 0 (a:2404115, b:2394115, experiment-only). Sub-items: `N.N` / `N.N.`. Labs: experiments as `N.` / `0N` / bare `N` with the 10th as bare `10` (a:2403115 finds 9 dotted markers). Experiments (`experiment_marker`, 3 attempts): 18/18 courses with an experiment-table heading (attempt 1 14/18, attempt 2 16/18, attempt 3 18/18).

## Topic separators
Free text in the Roman and dotted layouts: topics are separated by commas, periods, `;`, bullets (U+25CF `●` seen in b:2394112 modules 3, 5, 6 on p55-56) and `N.N` sub-item boundaries; sub-headings end with `:` (`Entropy:`, `Basic Concepts :`). Words are sometimes joined across lines by missing spaces. The parser must strip `N.N` (R6). Not measured: real boundary accuracy.

## Known oddities
1. Hypotheses corrected: no DRAFT watermark; "Total Hours" in 4 courses, not 1; '87-92 seven-digit codes alone' are the code repeated in header/exam tables (not module codes).
2. Per-course layouts differ inside one PDF (author variance): Math (zero_module), SOM (dotted), Thermodynamics/FEA/etc (roman with `Sr. No. | Name of Module | Detailed Content | Hours | CO Mapping`), labs (`Sr. No. | Module | Detailed Content | Hours | LO Mapping` with module numbers `I..VI` or `1..6`), Entrepreneurship/Environmental (`Unit | Name | Topic Name | Topic Description | Hours | LO Mapping`, p46 a).
3. Lab courses have no modules (a:2403115 has 10 experiments with paragraph descriptions p31-32, short titles p33 `List of Experiments.`) -- all 10 listed in golden a_2403115.json.
4. Mini Project a:2403611 / b:2393611: no syllabus table.
5. Module name tail after CO tail (b:2394112, a:2404112); `C02/C03` typos; `III Metal Forming` same line.
6. b:2393114 raw order: module table before course header block.
7. Page break inside a module (b:2393111 module 4: Self-learning paragraph at p18 line 0).
8. Hours label `Hour`+`s` split; `Mapp`+`ing`; header cell `H/rs/.`.
9. `Sr. No.` column carries a `0` row (Prerequisite) in 20 courses.
10. Lab list items include `Group A/Group B/Group C` separators and `Part (A)/(B)/(C)` in a:2404115 (dump not taken; `nep26-se-mech_stats.txt` has the STOP counts).

## Exact regexes with measured coverage (each links to docs/evidence/regex_runs/<file>)
| name | regex | matched/total (unit) | attempts | verdict | file |
|---|---|---|---|---|---|
| nep_banner | `As Per NEP 2020` (re.I, p1-6) | 2/2 PDFs | 1 | FULL | nep26-se-mech_nep_banner.txt |
| course_code | `^\s*(\d{7})\s*$` first match on start page | 34/34 | 1 | FULL | nep26-se-mech_course_code.txt |
| title | lines until `^\s*(?:\d{1,2}\*?(?:\+\d)?\|-{1,2})\s*$` | 34/34 | 1 | FULL | nep26-se-mech_title.txt |
| region_start | see Stop markers | 31/34 | 2 | PARTIAL | nep26-se-mech_region_start.txt |
| region_stop | see Stop markers | 31/34 | 1 | PARTIAL | nep26-se-mech_region_stop.txt |
| module_marker | 4 styles above, predicate >=6 consecutive markers | 29/34 | 2 | PARTIAL | nep26-se-mech_module_marker.txt |
| experiment_marker | heading `^(?:Part \(A\)\|A\. List of Experiments.*\|List of Experiments\.?\|Expt\.)\s*$` then `^(0[1-9]\|1\d\|[1-9]\.?)\s*$` with next line `^(?!\d{1,2}\.?\s*$)\S` | 18/18 (courses with heading) | 3 | FULL | nep26-se-mech_experiment_marker.txt |
| hours_tail | `^\d{1,2}\.?\s*$\|^-\s*$` | 29/34 | 1 | PARTIAL | nep26-se-mech_hours_tail.txt |
| co_tail | `^(?:C[O0]\|LO\|L)\s?[1-9]\b\|^L\d(?:,\s*L?\d)*,?\s*$` or bare digit after `^0\d$` | 28/34 | 3 | PARTIAL | nep26-se-mech_co_tail.txt |
| self_learning | `^Self[- ]learning [Tt]opics?\s*:?` | 28/38 lines (10 = prose, see Self-learning) | 1 | marker lines all matched; PARTIAL by the literal count | nep26-se-mech_self_learning.txt |
| total_hours | `^Total Hours?\b` | 4/34 | 1 | PARTIAL (30 courses have no such line) | nep26-se-mech_total_hours.txt |
Predicate definitions are in each evidence file next to the regex. `module_marker`, `hours_tail`, `co_tail` also count courses whose module table does not exist (5 courses); that is why they cannot reach 34/34.

## Failures (verbatim, per regex, per attempt 1-3)
Verbatim lists (courses, pdf/page/line, samples) are in the evidence files; summary:
- region_start attempt 1 (29/34): a:2403611, a:2404115, b:2393115, b:2393611, b:2394115. Attempt 2 (adds `Part (A)`): 31/34, remaining a:2403611, b:2393115, b:2393611.
- region_stop (31/34): same 3 courses, no stop marker/no region.
- module_marker attempt 1 (28/34): a:2403611, a:2404115, b:2393115, b:2393611, b:2394112 (found [1, 2], roman marker `III Metal Forming` on one line), b:2394115. Attempt 2 fixed b:2394112 -> 29/34; remaining: a:2403611, a:2404115, b:2393115, b:2393611, b:2394115.
- hours_tail (29/34): a:2403611, a:2404115, b:2393115, b:2393611, b:2394115 (no markers).
- co_tail attempt 1/2 (24/34) -> attempt 3 28/34; remaining: a:2403611, a:2404115, b:2393112 (Strength of Materials, b, has no CO column: markers=6, co-like=0), b:2393115, b:2393611, b:2394115.
- experiment_marker: attempt 1 failures a:2403116, a:2404411, b:2393116, b:2394411; attempt 2 failures a:2404411, b:2394411 (exercise text starts with a digit); attempt 3 0 failures.
- self_learning: 10 prose lines (listed verbatim in the file).
- total_hours: 30 courses, listed in file.

## Topic validity census (violations by rule id, total topics)
Spike `spikes/nep26-se-mech_topics.py` -> `docs/evidence/regex_runs/nep26-se-mech_topic_validity.txt`.
(1) NAIVE splitter (commas, periods, bullets, `N.N` boundaries; numbering NOT stripped; self-learning content kept) over the 29 courses with a module region: 1688 candidate topics, 445 violating at least one rule. Counts: R1_word_count_1_to_8 271, R2_len_over_80_chars 137, R3_contains_colon_or_semicolon 214, R4_generic_heading 9, R5_procedural 0, R6_leading_numbering 105, R7_hours_or_CO_leak 3, R8_no_letters 10 (Unicode math glyphs). This measures the rules on a naive splitter, not parser quality; R7 examples are `CO2 and shell molding` (false positive) and header text leaked into b:2393114 by its raw-order oddity.
(2) Golden drafts (5 courses): 273 topics, 1 violation: R7 on `CO2 molding` (false positive, b_2394112.json, module I).

## Golden courses (5, DRAFT) and how they were drafted
Files in `tests/golden/nep26-se-mech/`: `a_2403112.json` (Strength of Materials, normal dotted layout, 51 topics), `a_2403113.json` (Thermodynamics, odd roman layout with sub-headings, 91), `a_2403115.json` (Materials Testing, lab, 10 experiments as one pseudo-module `LAB`), `b_2393111.json` (Engineering Mathematics-III, zero_module layout with self-learning excluded, 46), `b_2394112.json` (Manufacturing Processes, odd name/tail layout, 75). All `status: DRAFT - needs human sign-off`. Drafted by reading each course's text (pages in `source_pages`) and applying `docs/formats/topic_validity.md`; bundles split where the text lists separate concepts (e.g. `Tension stress / Compression stress / Shear stress`), headings in the source treated as module names, hours/CO dropped. Assumptions needing review are in each file's `notes` and in `docs/open_questions.md`.

## UNKNOWN items (also copied to docs/open_questions.md)
Self-learning as Topics; unnamed modules 1-2 of Strength of Materials; experiments as Topics; Mini Project policy; hours/CO/name-tail assignment rules; where totals live for 30 courses; Roman-body sub-headings as Topics; the `2019-scheme` folder name vs NEP 2020; need for separate parsers a/b; raw-order oddity in b:2393114; R7 false positive on `CO2`; bundle policy behind the 445 naive violations; math-glyph handling; bare `10` experiment marker.
