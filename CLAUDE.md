# CLAUDE.md - rules for every AI session on KDG v2

Project: upload an NEP-scheme Mumbai University syllabus PDF, extract Topics, predict prerequisite Edges with Confidence, show graph, plan, bottlenecks. Read `docs/PRD.md` first, `docs/glossary.md` for exact terms.

## Frozen paths (never edit)
- `reference/` (copied old code; copy out of it, do not change it)
- `data/raw/` (source PDFs)
- `docs/evidence/dumps/` and `docs/evidence/regex_runs/` (raw evidence; add files, never rewrite)

## Never guess a layout: dump first
Before writing or changing any parser or regex: dump at most 60 raw PyMuPDF lines of a real sample into `docs/evidence/dumps/`, then run the regex against EVERY course of that family and save coverage (matched/total) and every failure in `docs/evidence/regex_runs/`. Max 3 refinement attempts per regex; then record failures and mark the family PARTIAL. PyMuPDF puts each table cell on its own line, so web-converted text is not a valid source.

## Evidence rule
Every factual claim cites a file path plus command output under `docs/evidence/`. Not observed means write UNKNOWN and add it to `docs/open_questions.md`. Do not rename glossary terms.

## Hard prohibitions
- No git push, no force operations, no commits to `main`. Work on feature branches; the owner pushes or approves pushing.
- No LLM or network calls during parsing or inference. LLM use is allowed only in the offline labelling task T021, with keys from environment variables, and only after the owner approves the run.
- No secrets in code, docs, or logs. A hardcoded Supabase service-role key was found in the old repo and redacted here; never reintroduce one. Run `python scripts/scan_secrets.py .` before committing once it exists.
- Golden files stay `status: DRAFT - needs human sign-off` until a human changes it.

## Commands (PROPOSED until the scaffold task T001 lands; update this list then)
- Parser/golden tests: `pytest tests/parsers -q`
- All tests: `pytest -q`
- Frontend e2e: `npx playwright test`
- Spikes (throwaway): `spikes/*.py`, run with `PYTHONIOENCODING=utf-8 python spikes/<file>.py`

## How to report
End each task with: what changed (paths), the acceptance command and its real output, failures verbatim, new UNKNOWNs. Do not claim "works" without the output. If a stop-and-ask condition in `docs/tasks.md` is met, stop and ask.

## Token discipline
Never print whole PDFs or whole CSVs. Use counts, `head`, and code that measures. Prefer one script that prints a small table over many exploratory prints. Do not re-read files you just wrote.
