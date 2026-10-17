# Parse verification rubric

Read-only. Context: a table-based NEP syllabus parser produced accepted courses in `docs/evidence/baseline/tierA_snapshot_v4.jsonl` (one JSON per line: course_code, title, source_pdf, modules[{number,name,hours,pages,topics,content_raw}], content_hash). Your batch is the list at index <N> of `docs/evidence/baseline/tierA_v4_batches.json` (a list of lists of content_hash values; use ONLY your index; take the first JSON line having each hash).
For each course open `source_pdf` (if the stored path is missing, find the same file name under `data/raw/NEP_syllabus/*/`) with PyMuPDF and print ONLY the text of that course's module pages (the pages listed in `modules[].pages`, plus the next page if the last module may continue). Never print whole PDFs.
Judge the parsed topics against the raw text:
1. All 6 modules present and in order; final module not truncated; nothing important missing (list missing concepts).
2. JUNK topics: dangling fragments, two distinct items glued into one topic, half of a parenthetical, a hyphenated name cut in two, stray symbols. Count them.
3. Verdict: OK (junk <= 5% and nothing important missing), FIXABLE (junk 5-12%), BAD (junk > 12% or content missing/truncated).
Write `{"verdicts": {"<course_code>|<content_hash>": {"verdict": "OK|FIXABLE|BAD", "topics": N, "junk": N, "note": "one line naming the junk pattern or missing content"}}}` to `data/labelling/verify_v4_<N>.json`.
No network, no git, no other writes. Final report (max 8 lines): counts of OK/FIXABLE/BAD and the 3 most common junk patterns with 2 quoted examples each.
