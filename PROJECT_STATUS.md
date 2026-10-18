# KDG v2 - project status (read this first)

Written for Mahi and Mahi's coding assistant. Last update: 2026-10-18, branch `feature/kdg-v2-prd`.
One sentence: upload a Mumbai University **NEP** syllabus PDF -> the backend reads every course -> the user picks a course ->
the backend returns a prerequisite graph (topics, directed edges with confidence, Kahn study order, start nodes, bottlenecks,
background knowledge) -> the learner marks topics as mastered; blocked topics unlock when all their prerequisites are mastered.

**State:** backend endpoints are built and tested (`tests/test_api.py`, plus a smoke run on 4 real PDFs). **The frontend is not
connected to the new fields yet**; that is Mahi's work (section 6). No frontend file was changed.

---

## 1. Run it

```bash
pip install -r requirements.txt
# one-time: the sentence encoder must be in the local Hugging Face cache (inference runs with HF_HUB_OFFLINE=1)
HF_HUB_OFFLINE=0 python -c "from sentence_transformers import SentenceTransformer as S; S('sentence-transformers/all-MiniLM-L6-v2')"
uvicorn app.main:app --port 8000          # from the repo root; Swagger UI at http://127.0.0.1:8000/docs
python -m pytest tests -q                 # 9 tests, offline
```
Optional: `GEMINI_API_KEY` in the environment or in a git-ignored `.env` enables the fallback service (section 3). Never commit a key.
Runtime files (saved analyses and progress) go to `data/runtime/` (git-ignored; override with `KDG_RUNTIME_DIR`).
Other env vars: `KDG_MODEL` (default `nep6`), `KDG_CORS` (comma-separated origins, default the Vite ports 5173/3000), `KDG_LOG_LEVEL`.

---

## 2. Why each part of the repo exists

| Path | Purpose |
|---|---|
| `app/main.py` | FastAPI app: CORS, loads the model once at start-up (`pipeline.warm_up`), mounts all routes under `/api/v1`, `/healthz`. |
| `app/api/routes.py` | Every HTTP endpoint (thin: validation + error mapping). |
| `app/services/pipeline.py` | PDF -> courses -> topics -> edges -> payload. Owns the fallback order. Stores each analysis in `data/runtime/analyses/`. |
| `app/services/graph_ops.py` | Pure graph rules: Kahn order/levels, node states (mastered/ready/blocked), missing prerequisites, bottlenecks. |
| `app/services/progress.py` | Mastery rules + saved progress per (user_id, analysis_id). |
| `app/services/fallback.py` | Gemini fallback, used only where the parser or model fails (section 3). |
| `app/parser/nep_tables.py` | Finds course-header and module tables in the PDF (PyMuPDF `find_tables`), stitches tables across pages. |
| `app/parser/nep_topics.py` | Turns module cells into clean topic names (splitting lists, removing hours/CO/book text). |
| `app/parser/nep_gate.py`, `nep_verify.py`, `nep_tier.py` | Quality gate: every course gets `accepted`, `review` or `rejected` with reasons; every topic must be traceable to the PDF text. |
| `app/ml/infer.py` | Loads a model bundle (`model_artifact_<name>`, `pca_artifact_<name>`, `calibrator_<name>`) and turns topic lists into edges. |
| `app/ml/features_*.py` | Pair features (embedding similarity, positions, module/title similarity, ranks). `features_batch.py` must match `features_v5.py` (`tests/test_features_batch.py`). |
| `app/ml/*nep6*` | **Served model.** Older bundles (`v5`, `nep2/4/5`) are kept only for comparison in `scripts/eval_models.py`. |
| `scripts/parse_corpus.py` -> `build_topics_nep.py` | Offline: parse every PDF in `data/raw` -> `data/processed/corpus_v2/` -> `topics_nep.json` (train/val/test split by course code). |
| `scripts/merge_labels.py`, `make_adjudication.py`, `check_*.py`, `finalize_labels.py` | Offline labelling pipeline: two independent label passes -> merge -> independent adjudication -> `data/labelling/final/`. |
| `scripts/train_nep.py`, `eval_models.py`, `eval_by_department.py` | Train a bundle; frozen evaluation on unseen PDFs; per-department table. |
| `scripts/export_demo_graph.py`, `build_demo.py`, `demo/` | Standalone HTML demo of the graph + Kahn + mastery gating (reference behaviour for the UI). |
| `data/raw/NEP_syllabus/<branch>/` | Source PDFs (frozen). `data/processed/` parsed corpus. `data/labelling/` labels. `data/gold/` evaluation outputs. |
| `MODEL_REPORT.md` | Model numbers in detail. `INTEGRATION.md` now only points here. |
| `reference/` | Frozen copy of the old app (old backend `reference/app`, frontend `reference/frontend` = remote `feature/study-planner-ui`). Do not edit; copy out of it. |
| `spikes/`, `tests/golden/` | Parser research scripts and draft golden files (need human sign-off). |
| `docs/` | Local only, never pushed (PRD, decisions). |

---

## 3. How the API is wired

```
POST /api/v1/analyze  (alias POST /api/v1/gemini/analyze = what the current frontend calls)
  form-data: file=<pdf>, subject=<course code or title, optional>
  │
  ├─ parser on the PDF (cached per PDF hash) ── several usable courses and no subject ─▶ {"needs_subject": true, "subjects": [{course_code, course_title}]}
  │
  ├─ topics:  course accepted/review ─▶ parser topics
  │           course rejected, or no course found ─▶ fallback.extract_topics   (no key ─▶ 422 {"error": "low_confidence"|"not_a_syllabus"})
  ├─ edges:   nep6 model ─ exception or 0 accepted edges ─▶ fallback.prerequisite_edges ─ unavailable ─▶ neighbouring topics in a module
  ├─ background knowledge: fallback.background ─ unavailable ─▶ the syllabus' printed "Prerequisite" row
  └─ payload (below), saved as data/runtime/analyses/<analysis_id>.json
```
**The payload never says which component produced a result** (no "AI", "Gemini", model names). Which path ran is written to the
server log only (`kdg.pipeline` / `kdg.fallback` loggers). `tests/test_api.py::test_payload_never_names_generator` guards this.
Fallback edges get the model's own score for that pair (at least the threshold) so they look like every other accepted edge.

### Analyze response (superset of the old `/gemini/analyze` contract, so the existing pages still render)
```json
{
  "needs_subject": false,
  "analysis_id": "3fa2c1d09b7e-2073112",
  "course_code": "2073112", "course_title": "Fluid Flow Operations",
  "thresholds": {"accepted": 0.2, "uncertain": 0.1},
  "nodes": [{"id": "2073112:1:bernoulli-s-equation", "name": "Bernoulli's equation", "unit": 1, "unit_title": "...",
             "depth": 2, "kahn_index": 14, "is_start": false}],
  "edges": [{"source": "<node id>", "target": "<node id>", "confidence": 0.47, "band": "accepted", "redundant": false}],
  "kahn_order": ["<node id>", "..."],
  "start_nodes": ["<node id>", "..."],
  "study_flow": [{"step": 1, "id": "...", "name": "...", "unit": 1, "level": 0, "prerequisites": ["names"], "prerequisite_ids": ["ids"]}],
  "bottlenecks": [{"id": "...", "name": "...", "unlocks": 4, "direct": 2}],
  "missing_prerequisites": [{"name": "Basic calculus", "reason": "...", "needed_for": [{"id": "...", "name": "..."}]}]
}
```
- `source -> target` = learn source before target. `confidence` is calibrated: about 59% of edges at 0.5-0.7 and 80% above 0.7 were right on unseen courses.
- `band: "accepted"` edges **block**; `band: "uncertain"` (0.10-0.20) edges are display-only (draw dashed), never block, never count as missing.
- `redundant: true` = implied by a longer accepted path; may be hidden in the drawing, still blocks.
- `depth` = Kahn level (column for a left-to-right layout). `kahn_order` prefers syllabus order among topics that are ready at the same time.
- Node ids are stable (`<course>:<module>:<slug>`), so saved mastery survives a re-upload of the same PDF.
- `missing_prerequisites` here = **background knowledge the syllabus assumes but does not teach**. Missing prerequisites of a
  *topic* for a learner come from the progress endpoints below.

### Progress endpoints
| Endpoint | Body | Returns |
|---|---|---|
| `POST /api/v1/progress/status` | `{analysis_id, mastered: [ids], target_id?}` | `nodes: {id: {state: mastered/ready/blocked, is_start, waiting_on}}`, `start_nodes`, `ready`, `next_up`, `progress_percent`, optional `target` (as below). Stateless. |
| `POST /api/v1/analytics/missing-prerequisites` | `{analysis_id, target_concept_id, known_concept_ids}` | `missing: [{id,name}]` in study order = Ancestors(target) minus known, `known_percent`, `total_prerequisites`. |
| `POST /api/v1/progress/mastery` | `{user_id, analysis_id, topic_id, mastered: true/false, force?}` | Saves and returns the status. Mastering a **blocked** topic -> HTTP 409 `{error: "blocked", waiting_on, missing}`; `force: true` = "I already know this and everything before it" (marks all ancestors). Un-mastering also un-masters every dependant. |
| `GET /api/v1/progress/{user_id}/{analysis_id}` | - | Saved mastery + status (restore a returning learner). |
| `GET /api/v1/analysis/{analysis_id}` | - | The stored analyze payload. |
| `GET /healthz` | - | `{status, model_loaded}` |
`user_id`: an anonymous id the frontend creates once (e.g. `crypto.randomUUID()`) and keeps in `localStorage`; letters, digits, `-`, `_`.
Accounts are not decided (decision D5 in the local PRD is a proposal); swapping the JSON files in `progress.py` for a database is a local change.

Errors: 400 bad file / id, 404 unknown analysis or topic, 409 blocked, 413 > 30 MB, 422 `{"error": "not_a_syllabus" | "low_confidence" | "subject_not_found", "reasons"?}`.
Timing (this laptop, CPU): first request on a PDF 10-20 s (whole PDF parsed once, then cached); each course from the same PDF afterwards under 1 s.

Old endpoints from `reference/app` (`/pipeline/upload-and-parse`, `/graph/*`, `/sequence/topological`, `/recommendations/generate`, a global
in-memory graph, Neo4j/Postgres/Supabase) are **not** ported: the new endpoints are stateless per analysis and cover the same needs.
`reference/frontend/src/App.jsx` (the old `index.html` page) still calls them and will not work; the landing and study-planner pages do.

---

## 4. How the model performs (nep6, unseen PDFs, details in `MODEL_REPORT.md` and `data/gold/eval_by_department_nep6.txt`)

Training data is **29 courses, almost all Computer / IT / CSE (AI&ML)** plus 3 first-year and 1 Electrical course. Test courses come from
PDFs and branches never used for training. Directed-edge F1 against AI-made reference labels (two passes + adjudicator, not human-checked):

| Test department | courses | model F1 | "next topic in module" rule | gain |
|---|---|---|---|---|
| Chemical Sem 3/4 | 6 | 0.452 | 0.429 | +0.02 |
| E&TC Sem 5/6 (electives: DSA, Algorithms, Robotics) | 3 | 0.423 | 0.377 | +0.05 |
| Mechanical Sem 3/4 | 4 | 0.362 | 0.362 | 0.00 |
| Mechanical Sem 5/6 | 5 | 0.383 | 0.326 | +0.06 |
| **All** | 18 | **0.400** | 0.368 | +0.03 |
Old v5 model on the same courses: 0.248. Calibration error 0.001. Per course F1 ranges 0.19 (Machinery Diagnostics) to 0.60.
IT / Computer courses are training and validation data, so there is no independent number for them (validation F1 0.40 was used to pick the threshold).

What the output looks like (Fluid Flow Operations, 88 topics): the strongest edges are right (Newton's law of viscosity -> kinematic
viscosity; Bernoulli -> modified Bernoulli -> practical applications). Weak edges near the threshold are often "next item in the same list"
(globe valve -> return valve) and some are wrong in direction (Bernoulli -> Euler's equation). The highest confidence on that course is
0.62, about 14 of 88 topics get no accepted edge, and about a third of topics are start nodes. So the graph is **useful as a guided
order, not as an authority**; keep the uncertain styling and the "I already know this" (force) option.

---

## 5. Known gaps (owner / model side)
- Parser: Civil Sem 3/4 and some other PDFs produce no usable course (text layer without spaces / no module tables) -> 422 without a fallback key. Typos in source PDFs leave some glued topics.
- Labels are AI-made; a human check of ~300 edges is the most valuable next step for the model.
- No Sem 5/6 PDFs for Civil, Electrical, Chemical were found.
- The 3 courses 2115116, PCC501, 24061132 are parsed but not labelled.
- Supabase service-role key from the old repo must be rotated by the owner (it is redacted in `reference/`).

---

## 6. Mahi's work (do it on a separate branch, e.g. `feature/frontend-kdg-v2`, branched from `feature/kdg-v2-prd`)
1. Copy `reference/frontend` to a top-level `frontend/` (do not edit `reference/`). Point `API_BASE_URL` / `VITE_GEMINI_API_URL` to `http://127.0.0.1:8000/api/v1` and `/api/v1/analyze`.
2. Graph view (`gemini/FlowGraph.jsx`, `landing/FlowMap.jsx`): column = `node.depth`, row = rank in that column; draw `band: "uncertain"` edges dashed; edge width from `confidence`; optionally hide `redundant` edges.
3. Mastery: on load call `GET /progress/{user_id}/{analysis_id}`; colour nodes by `nodes[id].state`; label `start_nodes` as START; on click call `POST /progress/mastery`; on 409 show `detail.missing` with an "I already know these" button (`force: true`).
4. Side panel for a selected topic: `POST /analytics/missing-prerequisites` (ordered list + percentage).
5. Remove generator wording from the UI: `landing/LandingApp.jsx` FAQ lines ~199-200 ("An AI reads the syllabus...", "sent to an AI service") and `landing/ScrollSections.jsx` ~196 ("An AI pulls out the real topics"). Owner rule: the UI never says who or what produced a result.
6. Animations: the CSS keyframes exist (`landing.css`, `gemini/theme.css`) but are switched off when the OS reports reduced motion (Windows: Settings > Accessibility > Visual effects > Animation effects). Check that first before changing code.
7. Retire `App.jsx` / `index.html` (old endpoints) or port it to the endpoints above.
8. Add a "wrong edge / wrong direction" button; storing those reports gives the owner real labels (endpoint not built yet; ask the owner).
Reference behaviour for 2-4: `demo/kdg_demo.template.html` (functions `stateOf`, `onNode`, `renderSide`).
