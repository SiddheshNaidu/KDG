# Requirements

Format: ID | description | acceptance test | priority | depends-on.
Acceptance commands are PROPOSED shapes; the exact script names are created by the tasks in `tasks.md`. Numeric targets are in `evaluation.md` (PROPOSED). "Page" names are PROPOSED and listed in `open_questions.md` for professor confirmation.

## Functional: parsing and data
| ID | Description | Acceptance test | Pri | Depends |
|---|---|---|---|---|
| FR-001 | Family router detects the layout Family of an uploaded PDF using the detection regexes in `docs/formats/<family>.md`. | `pytest tests/test_family_router.py` over every PDF in `data/raw` expects the family id in `tests/golden/router_expected.json` | P0 | T004 |
| FR-002 | One deterministic parser per Family, gated by that Family's golden courses. | `pytest tests/parsers/test_<family>.py` | P0 | FR-001 |
| FR-003 | Confidence gate: a Course below the gate is returned as `status: rejected` with a reason; if no Course passes the upload returns HTTP 422 `low_confidence`. | `pytest tests/test_gate.py::test_low_confidence_422` | P0 | FR-002 |
| FR-004 | Each Topic has `source_page`, `source_quote`, `parse_confidence`, `topic_key` per `docs/schemas/topic.json`. | `python -m jsonschema -i out.json docs/schemas/course.json` on every parsed course | P0 | FR-002 |
| FR-005 | Topics violating validity rules R1-R8 are dropped or flagged, never silently emitted. | `pytest tests/test_topic_validity.py` | P0 | FR-002 |
| FR-006 | Prerequisite rows ("0 Prerequisite") and self-learning/self-study blocks never appear as Topics (spellings per family doc). | covered by golden tests per family | P0 | FR-002 |
| FR-007 | Parsing a PDF needs no network and no API key. | `pytest tests/test_offline.py` with sockets blocked | P0 | FR-002 |
| FR-008 | Syllabus quality report lists accepted Courses, rejected Courses with reason, and dropped lines by rule id. | `curl /api/v2/uploads/{id}/quality` returns the report matching `tests/golden/quality_*.json` | P1 | FR-003 |
| FR-009 | CO mapping view (OPTIONAL): only if CO mapping is parsed from syllabus tables (UNKNOWN per family). | feature flag test | P2 | FR-002 |

## Functional: model and graph
| ID | Description | Acceptance test | Pri | Depends |
|---|---|---|---|---|
| FR-020 | Predict Edges offline with calibrated Confidence and a band (accepted / uncertain / rejected). | `pytest tests/test_edges_schema.py` + `scripts/eval_edges.py --check-calibration` | P0 | T020 |
| FR-021 | Serving uses ONE documented threshold set, read from the model artifact meta, not from a second file. | `pytest tests/test_threshold_single_source.py` | P0 | T020 |
| FR-022 | Graph post-processing: sibling guard, degree caps, no orphan attachment, transitive reduction, DAG guarantee. | `pytest tests/test_graph_rules.py` (asserts DAG, caps) | P0 | FR-020 |
| FR-023 | Feature parity between training and serving. | `pytest tests/test_features_parity.py` (exists in reference/) | P0 | T020 |
| FR-024 | Model card JSON generated from training run (data hash, label source, metrics, limits). | `python scripts/make_model_card.py --check` | P1 | T023 |

## Functional: pages (PROPOSED set)
| ID | Page | Acceptance test (Playwright unless noted) | Pri | Depends |
|---|---|---|---|---|
| FR-040 | Upload + subject picker: drag PDF, see each Course with `parse_confidence`, pick one. | `npx playwright test upload.spec.ts` | P0 | FR-003 |
| FR-041 | Graph navigator: Edges coloured by band, slider filters by Confidence, node detail shows `source_quote` and page. | `npx playwright test graph.spec.ts` | P0 | FR-020 |
| FR-042 | Study planner / goal path: choose goal Topic, get ordered path; honours saved Mastery state. | `npx playwright test planner.spec.ts` | P0 | FR-041, FR-060 |
| FR-043 | Bottlenecks: ranked by direct dependents AND by transitive reach, both labelled. | `npx playwright test bottlenecks.spec.ts` | P1 | FR-041 |
| FR-044 | Syllabus quality report page (FR-008 data). | `npx playwright test quality.spec.ts` | P1 | FR-008 |
| FR-045 | Model card page (data, label source = LLM teacher + human gold, metrics, limits). | `npx playwright test modelcard.spec.ts` | P1 | FR-024 |
| FR-046 | Evidence / NBA page. Content UNKNOWN: which NBA artefacts are required (open question). Do not invent. | none until the question is answered | P2 | open Q |
| FR-047 | About / limits page (states that uncertain edges are not claims, supported families, known failures). | `npx playwright test about.spec.ts` | P1 | - |

## Functional: accounts and saved mastery (decision D5, PROPOSED)
| ID | Description | Acceptance test | Pri | Depends |
|---|---|---|---|---|
| FR-060 | First visit creates an anonymous identity; no form needed. | Playwright: fresh context, mark a node mastered, reload, still mastered | P0 | D5 |
| FR-061 | "Save my progress" links email/Google to the same user without losing data. | Playwright against Supabase test project (UNKNOWN: project availability) | P1 | FR-060 |
| FR-062 | Backend verifies JWT on every user route and ignores any client-sent user id. | `pytest tests/test_auth.py` (forged/expired token returns 401) | P0 | FR-060 |
| FR-063 | Mastery is keyed by `topic_key` + `syllabus_hash`; changed Topics become `archived` and are shown for confirmation. | `pytest tests/test_mastery_migration.py` | P1 | FR-004 |
| FR-064 | Row-level security: a user can read/write only their rows. | SQL test with two users | P0 | FR-060 |
| FR-065 | Delete my data endpoint removes all user rows. | `pytest tests/test_delete_account.py` | P1 | FR-060 |
| FR-066 | Graph payload is user-independent and cacheable (ETag); mastery is merged client-side or via `POST /plan`. | `curl -I` shows ETag; second request returns 304 | P1 | FR-020 |

## Non-functional
| ID | Description | Acceptance test | Pri | Depends |
|---|---|---|---|---|
| NFR-001 | Cold start and per-course latency within the budgets fixed after measurement (D4). | `python scripts/bench.py --assert` | P1 | T-perf |
| NFR-002 | Every claim in docs cites evidence or is UNKNOWN. | `python scripts/check_evidence.py docs/` | P1 | - |
| NFR-003 | Reproducible training: data hash and git commit recorded in the artifact meta. | `python scripts/check_artifact_meta.py` | P0 | T020 |
| NFR-004 | Accessibility: keyboard-navigable graph alternative (list view) and contrast checks. | `npx playwright test a11y.spec.ts` (axe) | P2 | FR-041 |

## Security (each testable)
| ID | Requirement | Acceptance test | Pri | Depends |
|---|---|---|---|---|
| SEC-001 | Upload accepts only PDFs: extension, MIME, and magic bytes `%PDF-`; size limit; page-count limit. Limits are PROPOSED and set in config. | `pytest tests/security/test_upload_limits.py` (exe renamed .pdf rejected, oversize rejected) | P0 | - |
| SEC-002 | PDF parsing runs in an isolated subprocess with a wall-clock timeout and memory limit. | `pytest tests/security/test_parse_timeout.py` (crafted slow PDF is killed) | P0 | FR-002 |
| SEC-003 | Rate limiting per client on upload and plan routes. | `pytest tests/security/test_rate_limit.py` returns 429 | P0 | - |
| SEC-004 | Strict CORS allow-list from env; no wildcard with credentials. | `pytest tests/security/test_cors.py` (evil origin gets no ACAO header) | P0 | - |
| SEC-005 | Security headers: CSP, X-Content-Type-Options: nosniff, frame-ancestors (via CSP). | `pytest tests/security/test_headers.py` | P0 | - |
| SEC-006 | No secrets in the frontend bundle; secrets only via environment. | `python scripts/scan_secrets.py dist/ reference/ app/` (fails on JWT-shaped strings) | P0 | - |
| SEC-007 | Dependency audit in CI: `pip-audit` and `npm audit`. | CI job exit code | P1 | - |
| SEC-008 | Uploaded files are deleted after parsing. | `pytest tests/security/test_upload_cleanup.py` | P0 | FR-002 |
| SEC-009 | All Topic text rendered in the UI is escaped; `dangerouslySetInnerHTML` is forbidden. | `grep -rn dangerouslySetInnerHTML frontend/src` must be empty (it was empty in reference/, see `reference_code_facts.txt`) + XSS Playwright test with `<img onerror>` topic | P0 | - |
| SEC-010 | Error responses carry no stack traces or file paths. | `pytest tests/security/test_error_shape.py` | P0 | - |
| SEC-011 | Logs contain no PII (no email, no user JWT). | `pytest tests/security/test_log_scrub.py` | P1 | FR-060 |
| SEC-012 | Authentication follows D5. Open question: confirm option B. | see FR-060..FR-065 | P0 | D5 |
| SEC-013 | Compromised-key follow-up: the hardcoded Supabase service-role key found in the old repo is treated as leaked; owner rotates it. Evidence: `docs/evidence/reference_code_facts.txt`, `open_questions.md`. | owner confirms rotation (manual) | P0 | - |
