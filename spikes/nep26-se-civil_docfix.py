"""Throwaway: one-off wording fixes to docs/formats/nep26-se-civil.md (line-prefix based)."""
p = "docs/formats/nep26-se-civil.md"
L = open(p, encoding="utf-8").read().split("\n")
NEW = {
 "- Content: 4 front/scheme pages": "- Content: pdf pp 1-15 are front matter and scheme tables (scheme tables with course codes on pp 10-13; other front-matter content UNKNOWN, not inspected), course syllabi pp 16-82. 17 courses with syllabus text found (Sem III: 2093111-2093116, 2993511, 2993512, 2093611; Sem IV: 2094111-2094115, 2094411, 2994511, 2994512). Evidence: `docs/evidence/regex_runs/nep26-se-civil_course_code.txt` (list \"courses found (17)\").",
 "- Module count: always 6": "- Module count: always 6 (11/11). Number of sub-items per module: 1 to 5 (per-module lists in the EXTRA block of `docs/evidence/regex_runs/nep26-se-civil_subitem.txt`).",
 "- Text fragmentation:": "- Text fragmentation: many sub-item lines come out one word per line (e.g. 2093112 page 21 lines 44-47 \"Archimedes / principle, / Buoyancy, / Meta-Centre,\"; dump `docs/evidence/dumps/nep26-se-civil_2093112_p21.txt`), and some lines end without a trailing space (dump lines 39-42), so joining raw lines with no separator would fuse words. Join lines with a single space and collapse whitespace; one-word-per-line fragments are harmless for the module row regexes but break any \"one raw line = one topic\" assumption.",
 "- Letter-spaced text inside": "- Letter-spaced text inside a sub-item (\"r e p e a t e d\", 2094111): 1 occurrence in all module sections; evidence: `docs/evidence/regex_runs/nep26-se-civil_subitem.txt` EXTRA block.",
 "2. Module name wraps over 2 lines": "2. Module name wraps over 2 lines (2093114 module 3) and sub-items 3.1-3.3 of 2093114 repeat the module title verbatim: `docs/evidence/dumps/nep26-se-civil_2093114_p29.txt` lines 34-43.",
 "4. The mini project 2093611": "4. The mini project 2093611 has a `Sr. No.` / `Stages of Project` table (p47); 2094411 has `List of Experiments` rows with `Concepts & Discussions` / `Practical` sub-blocks (p71, 30 header hits). Evidence: `docs/evidence/regex_runs/nep26-se-civil_experiment_tables.txt` (6/6 non-module courses have such a table header). Rows are not parsed; see UNKNOWN.",
 "3. Two layouts in one PDF": "3. Two layouts in one PDF: (a) module-table courses, (b) experiment-table courses (labs and the mini project/capstone) with columns `Sr No | List of Experiments | Hrs | LO Mapping` and sometimes a second table `List of Assignments / Tutorials`. Evidence: `docs/evidence/dumps/nep26-se-civil_2093115_p32.txt` lines 16-59; `docs/evidence/regex_runs/nep26-se-civil_module_row.txt` (\"other 6 courses have no module table\"); `docs/evidence/regex_runs/nep26-se-civil_experiment_tables.txt`.",
 "7. Course Outcomes header": "7. Course Outcomes header spellings: `Course Outcomes:`, `Lab Outcomes:`, bare `Outcomes:` (2093611) (`docs/evidence/regex_runs/nep26-se-civil_outcomes.txt`, 17/17 courses have a header with numbered items). The outcome count equals 6 for the 11 module courses (`nep26-se-civil_module_row.txt` outcomes_count); counts for the 6 non-module courses were not recorded (UNKNOWN).",
}
for k, l in enumerate(L):
    for pre, new in NEW.items():
        if l.startswith(pre):
            L[k] = new
            NEW[pre] = None
for pre, v in NEW.items():
    assert v is None, pre
for k, l in enumerate(L):
    if l.startswith("- The marker starts a line"):
        L[k] = l.replace(", or at the top of a page before the next module (2994511 page 76 line 4)", "")
open(p, "w", encoding="utf-8").write("\n".join(L))
print("ok")
