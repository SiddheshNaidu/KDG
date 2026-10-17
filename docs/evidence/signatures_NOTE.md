# Correction note for signatures.csv (written by lead after family agents reported)
- Column `draft_watermark` used a case-insensitive "DRAFT" search over lines and matched the word "drafting" / bibliography entries. Family agents found no DRAFT watermark token in nep26-fe-sem12, nep26-se-core, nep26-se-mech or nep26-sem56 (see each docs/evidence/regex_runs/*draft* file).
- Columns `module_detailed_content`, `prereq_line`, `dotted_subitem` undercount for nep26-se-civil (agent found 7 prerequisite lines and 178 sub-items vs 0 and 115 here).
- Column `total_hours` is not the stop marker in nep26-sem56 (0 hits); stop markers are Text Books variants.
