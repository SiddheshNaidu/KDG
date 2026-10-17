# Topic validity rules (PROPOSED, needs professor confirmation)

Implemented in `spikes/topic_validity.py`. A Topic is valid when it violates none of:

| id | rule | source of rule |
|---|---|---|
| R1 | 1 to 8 words | task spec |
| R2 | at most 80 characters | PROPOSED; audit_report.md section 5 flagged >100 chars as malformed |
| R3 | no ":" or ";" (these join a heading to a list, i.e. bundles) | PROPOSED from audit_report.md section 5 samples |
| R4 | not a generic heading (list in the script) | task spec |
| R5 | not procedural/setup (list in the script) | task spec |
| R6 | no leading numbering such as "1.1" | PROPOSED |
| R7 | no hours / CO tail ("08", "CO1", "Hrs") | task spec (tail leakage) |
| R8 | contains letters | PROPOSED |

Acronyms are allowed (R1/R4 do not reject them). "A and B" bundles are split only when the syllabus lists
separate concepts; this needs a human decision per case and is not machine-checkable (see open_questions.md).
Per-family violation counts are recorded in each `docs/formats/<family>.md` under "Topic validity census".
