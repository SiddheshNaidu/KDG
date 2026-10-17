# Architecture decisions (each: options, recommendation, status)

All "Recommendation" lines are proposals. Anything marked **needs professor confirmation** is also in `open_questions.md`.
Evidence index: `docs/evidence/census.csv`, `signatures.csv`, `model_v5_facts.txt`, `reference_code_facts.txt`.

## D1 Parsing
Options:
- A. Deterministic per-family parsers + family router + confidence gate (reject 422 `low_confidence`).
- B. LLM-assisted ingestion at upload time.
- C. LLM-assisted ingestion offline only (batch, ahead of time), output reviewed by a human and stored as data, never called at inference.

Facts: 8 candidate families were hypothesised by signature clustering (`docs/evidence/signatures.csv`); per-family dumps and regex runs verified or refuted each, giving 9 format docs (`docs/formats/*.md`) with sub-families inside several; see PRD section 3. Two hypotheses from signatures.csv were wrong: there is no DRAFT watermark (hits were the word "drafting"), and `Total Hours` is not the stop marker. The old repo's guess-first approach failed (task brief). Offline-inference doctrine is a stated requirement.

Recommendation: **A as the product path**; **C allowed only as a labelling aid** (teacher labels, golden-course drafting), never in the serving path. B rejected: it violates the offline doctrine, is non-deterministic, and adds key-exposure risk (the copied `reference/app/services/supabase_client.py` contained a hardcoded Supabase service-role key; it was redacted in this repo, see `open_questions.md`). Status: **needs professor confirmation**.

Confidence gate (PROPOSED): a Course is emitted only if its header, at least one module and its stop marker are found and its topics pass topic validity (`docs/formats/topic_validity.md`) at a rate at or above a threshold fixed after the golden tests run (UNKNOWN today). Otherwise the Course is listed in the quality report as rejected with a reason; if no Course passes, respond 422 `low_confidence`.

## D2 Data contract
JSON Schemas in `docs/schemas/`: `course.json`, `module.json`, `topic.json`, `edge.json`, `mastery.json`. Every Topic carries `source_page`, `source_quote`, `parse_confidence` and a stable `topic_key` (see D5). The v5 ids `t1,t2,...` are per-course and ephemeral (`teacher_edges_v5.csv` header `course,a_id,b_id,a_name,b_name,status`; evidence `model_v5_facts.txt`). Every Edge carries `score`, `confidence`, `band` (accepted / uncertain / rejected) and `provenance` (model version, feature set, calibration id, label source).

## D3 Model
Facts (evidence `docs/evidence/model_v5_facts.txt`):
- 40 features (8 base + 32 PCA components), XGBoost depth 4, embedding model `sentence-transformers/all-MiniLM-L6-v2`.
- Course-level split: 8 train, 2 val, remaining test courses listed in the meta file. Test rows 721, test F1 0.8000, test PR-AUC 0.8577, test precision 0.7259, recall 0.8909. These come from a 3:1 negative-to-positive training table, not from the natural pair distribution.
- Labels: LLM teacher, 1653 rows over 14 courses (912 confident, 741 uncertain). Mean parents per child 1.143 (matches the hint). Confident edges where the prerequisite index is greater than the dependent index: 3 (the hint "0 backward edges" is NOT confirmed; id order vs syllabus order is itself UNKNOWN). Adjacent-only share of confident edges: 0.384.
- Two thresholds exist: meta `threshold` 0.29 and `app/ml/decision_threshold.json` `optimal_threshold` 0.2. Which one serving uses is UNKNOWN (open_questions.md).

Recommendation (all PROPOSED, each validated by ablation):
1. Calibrate probabilities (isotonic or Platt) on validation data only; publish the reliability curve.
2. Abstain band: edges whose Confidence falls inside [lo, hi] are shown as "uncertain"; lo and hi are chosen on validation to reach a target precision for accepted edges.
3. Position-bias ablation: train with and without `signed_norm_position_gap`, `signed_unit_gap`, `same_unit`, `a_earlier_unit`; compare with a position-only baseline.
4. Structural post-processing: sibling guard, in/out-degree caps, no orphan attachment, transitive reduction; each toggle ablated and reported.
5. Training data: teacher-label every parseable NEP course; build a HUMAN gold set (>= 300 pairs from courses held out by course group, stratified by band and by same-module vs cross-module); thresholds chosen on validation only; the test split is touched once.
Who labels, and the labelling budget: **needs professor confirmation**.

## D4 Performance budgets (PROPOSED; no measurement exists yet, so all values are UNKNOWN until T-perf runs)
Placeholders to measure: cold start, per-course inference latency, whole-PDF upload-to-graph time. Targets are set in `evaluation.md` after the measurement.

## D5 Authentication and saved mastery
Owner requirement: anyone can use the product; a learner's previous mastery and completed nodes are saved.

Options:
- A. No accounts, device-local only (IndexedDB) with export/import file.
- B. Anonymous-first accounts: a device-bound anonymous identity is created on first visit and can be upgraded later (email magic link or Google) without losing data.
- C. Mandatory login before any use.
- D. Faculty-only login (conflicts with "anyone can use").

Recommendation: **B**. Design, integrated with the existing stack (FastAPI backend + React/Vite frontend; the reference code already has `app/api/persistence_router.py` with `POST /persistence/user-progress` and a Supabase REST client):
1. Identity: Supabase Auth anonymous sign-in on first load. A "Save my progress" button links an email or Google identity to the same user, so data is kept. The backend never trusts a client-sent user id; FastAPI verifies the JWT (signature, `exp`, `aud`) from the `Authorization: Bearer` header.
2. Stable keys: mastery is stored against `topic_key = <course_code>:<module_no>:<slug(topic)>` plus the Course's `syllabus_hash`. If a syllabus revision changes a Topic, the old record becomes `archived` and the learner is asked to confirm, rather than silently losing it.
3. Tables: `user_topic_state(user_id, topic_key, state, mastery, source, updated_at)` with `state` in {unknown, learning, mastered, archived}; `user_goal(user_id, course_code, goal_topic_key)`; optional `edge_feedback`. Row-level security: `user_id = auth.uid()`. No service-role key in the frontend or as a code default; secrets only via environment.
4. Model-to-UI flow: the graph of a Course is precomputed once per (parse_version, model_version) and served read-only with an ETag, so it is cacheable and shared by all users. A learner's mastery set is small, so the planner runs client-side on the cached graph, or server-side via `POST /plan {course, mastered[], goal}`. Only `accepted` edges block a learner; `uncertain` edges are drawn dashed and non-blocking, behind a visible toggle.
5. Features unlocked by saved mastery: next-learnable frontier (all accepted parents mastered), goal path limited to unmastered nodes, bottleneck ranking recomputed without mastered nodes, per-course progress, and a "disagree with this edge" action that writes `edge_feedback` (a future source of human gold; needs a consent text).
6. Privacy: anonymous by default, email optional, no PII in logs, an account-deletion endpoint that removes the user's rows.
Fallback kept: option A for a demo venue without network.
Status: **needs professor confirmation** (is a login acceptable for the NBA showcase; may the institution store learner data).
