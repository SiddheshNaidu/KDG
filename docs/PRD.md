# KDG v2 - Product Requirements (index and summary)

Status: DRAFT for professor review. Branch `feature/kdg-v2-prd`. Terms follow [glossary](glossary.md). Every number below cites a file under `docs/evidence/` or a family doc; anything unobserved is UNKNOWN and listed in [open_questions](open_questions.md). No application code was written in this task.

## 1. Goal
Upload a Mumbai University NEP-scheme syllabus PDF -> extract clean Topics per Course/Module -> predict prerequisite Edges with per-Edge Confidence -> show an interactive graph, study order, bottlenecks, with per-user saved mastery. Target audience for the showcase: NBA accreditation. End goal stated by the owner: an AI model that handles NEP syllabi and classifies the roadmap accurately with high confidence. No accuracy figure is promised; targets are PROPOSED in [evaluation](evaluation.md).

## 2. Scope and data (Phase 0)
- Scanned 32 PDFs, 2459 pages, none scanned/text-less ([census.csv](evidence/census.csv), [command output](evidence/census_command_output.txt)).
- In scope (copied to `data/raw/`): 25 PDFs, 1933 pages = 20 PDFs whose text contains "NEP" + 5 FE 2024-25 PDFs the owner named. Folders called `2019-scheme/` hold NEP-2020 PDFs (text: "As per NEP 2020", [census.csv](evidence/census.csv)).
- Out of scope: 7 REV-2019 PDFs (`nep_word_all=0`, `rev2019_all>0`), not copied; the owner said to discard REV-2019.
- The 5 FE PDFs contain no literal "NEP" (`nep_word_all=0`); inclusion rests on the owner's statement (open question LEAD-Q08).
- Model: v5 only, by owner decision (no evidence for "v6 lags" was supplied: LEAD-Q12). `reference/` holds v5 code, backend, frontend (from `study-planner-ui`), tests, `audit_report.md` (frozen, copied).
- Security: a hardcoded Supabase service-role key existed in the old `supabase_client.py`; redacted in `reference/`, must be rotated by the owner (LEAD-Q01, SEC-013).

## 3. Layout families (Phase 1)
Hypotheses came from [signatures.csv](evidence/signatures.csv) (corrections: [signatures_NOTE](evidence/signatures_NOTE.md)); each family agent re-verified by raw dumps (3 per family in `evidence/dumps/`) and ran regexes over every course (`evidence/regex_runs/`). Only 1 of 9 docs is VERIFIED-BY-DUMP; the rest are PARTIAL, with reasons.

| Family doc | PDFs / courses | Key regex coverage (matched/total) | Status and why |
|---|---|---|---|
| [nep26-sem56](formats/nep26-sem56.md) | 1 PDF (128 pp), 30 courses, 21 with module table | module rows 21/21 (126 rows); stop marker 21/21; hours 89/90; prerequisite 18/21; CO/LO tail 125/126 | PARTIAL: 2166116 module VI has no CO line in text; 3 courses lack prerequisite row |
| [nep26-se-core](formats/nep26-se-core.md) | 6 PDFs, 102 courses, 77 with module table | course start 102/102; module rows 77/77; stop 77/77; prerequisite 65/77; CO/LO tail 451/462 | PARTIAL: prerequisite absent in OS and Environmental Science; tail misses in 3 course types; module name from heuristic |
| [nep26-fe-sem12](formats/nep26-fe-sem12.md) | 6 PDFs, 210 course occurrences, 39 unique codes | detect 6/6; course code 209/213; title 195/210; module row 140/144; tail 828/876; stop 144/144 | PARTIAL: titles, IKS201 numeral split over page break, code mismatches between PDFs (measured against the agent's own extractor) |
| [nep26-se-electrical](formats/nep26-se-electrical.md) | 2 PDFs, 26 course instances (16 with modules) | module start 16/16 (needs bbox x0); tail 16/16; stop 14/14; title 26/26 | VERIFIED-BY-DUMP, caveat: needs coordinates, not line order alone |
| [nep26-se-chem-it-a](formats/nep26-se-chem-it-a.md) / [-b](formats/nep26-se-chem-it-b.md) | 2 PDFs (Chem 17 courses, IT 13) | hours/CO cells 71/71 (a), 78/78 (b); prerequisite 12/12 each; module_row 9/12 each | PARTIAL: raw-line method reads an hours cell as row number in 6 courses; 4 IT courses have no detail page |
| [nep26-se-mech](formats/nep26-se-mech.md) (sub-families a, b) | 2 PDFs, 34 courses | course code 34/34; title 34/34; region start/stop 31/34; module marker 29/34; CO tail 28/34 | PARTIAL: 5 courses have no module table; layout varies per course (4 numbering styles) |
| [nep26-se-civil](formats/nep26-se-civil.md) | 1 PDF, 17 courses, 11 with modules | module row 11/11; sub-item 66/66; course code 17/21 | PARTIAL: one PDF only; 6 experiment courses unparsed; 4 codes only in scheme tables |
| [nep2425-fe](formats/nep2425-fe.md) (sub-families fe-a..fe-d) | 5 PDFs, 5 module courses + 3 labs | detection 5/5, 0 false positives; hours/CO tail 5/5; header 5/6 | PARTIAL: module names wrap mid-word with no join rule found |

Hypotheses refuted by evidence: one layout for FE (4 sub-families); "DRAFT" watermark (hits are the word "drafting": fe-sem12, se-core, se-mech, sem56 docs); `Total Hours` as universal stop marker (0 hits in sem56; real markers are Text Books variants); "near-duplicate" FE Sem I-II booklets (shared-course text identical in only 13/33 to 34/35 courses across PDFs, `evidence/regex_runs/nep26-fe-sem12_pdf_diff.txt`).

Cross-family findings: PyMuPDF raw order interleaves module name and module content in 5 families (name/content boundary needs bbox or table detection: open question LEAD-Q14); self-learning markers appear in many spellings (listed per family doc); labs and mini projects often have no module table.

Topic validity ([rules](formats/topic_validity.md)): naive-splitter censuses over module-table courses give, per family, the violation counts in each family doc and `evidence/regex_runs/*_topic_validity.txt` (examples: fe-sem12 760 of 10267; se-core 252 of 4449; se-mech 445 of 1688; sem56 167 rule hits over 1931 topics (rule hits, not distinct topics)). The 40 draft golden courses show near-zero violations but were drafted with the rules in mind, so that figure is circular and is not evidence of parser quality.

Golden courses: 40 JSON files in `tests/golden/<family>/`, all `status: DRAFT - needs human sign-off`. None is verified.

## 4. Model facts that shape the plan (evidence: [model_v5_facts.txt](evidence/model_v5_facts.txt))
40 features; XGBoost depth 4; course-held-out split; test PR-AUC 0.8577, F1 0.8000 on 721 rows from a 3:1 negative table (not natural distribution); labels from LLM teacher (1653 rows, 14 courses); mean parents per child 1.143; 3 backward confident edges (hint "0 backward" not confirmed); 38.4% of confident edges adjacent-only; two thresholds exist (0.29 meta vs 0.2 file). No human gold set exists.

## 5. Decisions ([decisions.md](decisions.md))
D1 deterministic per-family parsers + confidence gate; LLM only offline as labelling aid. D2 JSON contracts in [schemas](schemas/). D3 calibrated probabilities, abstain band, position-bias ablation, structural rules, human gold set. D4 performance budgets measured later. D5 anonymous-first accounts with saved mastery keyed by `topic_key` + `syllabus_hash` (design in decisions.md). Each marked "needs professor confirmation" where applicable.

## 6. Requirements ([requirements.md](requirements.md))
FR-001..FR-009 parsing/data, FR-020..FR-024 model/graph, FR-040..FR-047 pages (Upload+picker, Graph navigator, Study planner, Bottlenecks, Quality report, Model card, Evidence/NBA, About), FR-060..FR-066 accounts and mastery, NFR-001..004, SEC-001..SEC-013. Each has a runnable acceptance test shape and priority.

## 7. Evaluation ([evaluation.md](evaluation.md))
Parser P/R/F1 vs golden and junk rate; edges P/R/PR-AUC and calibration on a human gold set of at least 300 held-out pairs against position-only, v4 and v5 baselines; graph sanity (DAG, degrees, adjacent-only share); Playwright end-to-end; security checks; performance. Targets PROPOSED; marked "to be confirmed after census and first golden run".

## 8. Tasks ([tasks.md](tasks.md))
T001 scaffold -> T002 secrets -> T003-T004 contract and router -> T005..T013 one parser per family, each gated by golden tests -> T013a validity/gate -> T014 isolation -> T015 corpus -> T020..T024 training (teacher labels, human gold, ablations, calibration, graph rules) -> T030/T031 API and auth -> T040..T042 pages -> T050..T052 security/CI/perf -> T060/T061 report and NBA pack. Each lists stop-and-ask conditions.

## 9. Top open questions for the professor (full list: [open_questions.md](open_questions.md))
1. Rotate the leaked Supabase key (LEAD-Q01).
2. Is anonymous-first login with saved mastery acceptable, and may learner data be stored (LEAD-Q02)?
3. Which NBA artefacts are required (LEAD-Q06)? Nothing was invented.
4. Who labels the human gold set and signs off golden courses (LEAD-Q05)?
5. Are self-learning items Topics? Are lab experiments Topics? (LEAD-Q14, repeated in 6 family docs)
6. May parsers use PyMuPDF coordinates to separate module name from content (LEAD-Q14)?
7. Confirm D1: LLM only offline for labelling (LEAD-Q04).
8. Which serving threshold is correct, 0.29 or 0.2 (LEAD-Q03)?
9. Confirm the FE 2024-25 PDFs are NEP-scheme and the proposed page list (LEAD-Q07, Q08).
10. Policy for duplicate courses across PDFs with differing text (LEAD-Q11).

## 10. Needs human sign-off
40 draft golden courses; topic validity rules R1-R8; confidence-gate threshold; family list and sub-family boundaries; D1, D3, D5; every PROPOSED target in evaluation.md.
