# KDG v2 - integration guide for the frontend and backend (for Mahi)

Status: **nothing here has been wired into the frontend.** The frontend in `reference/frontend` is untouched. This file says what exists, the exact data contract, and where each piece should plug in once the correct frontend files are confirmed.

## 1. What exists now

```
NEP syllabus PDF
  -> parser   app/parser/nep_tables.py   table extraction (PyMuPDF find_tables, course header + module tables)
              app/parser/nep_topics.py   modules + topic splitting
              app/parser/nep_gate.py     accept / review / reject rules (nothing is dropped silently)
              app/parser/nep_verify.py   every topic must appear in the raw page text
              scripts/parse_corpus.py    -> data/processed/corpus_v2/{accepted.jsonl, review.jsonl+csv, rejected.csv}
  -> topics   scripts/build_topics_nep.py -> data/processed/topics_nep.json
  -> edges    app/ml/infer.py            Bundle("nep5"): XGBoost + PCA + isotonic calibrator, offline (no network, no API key)
  -> graph    nodes, edges{a,b,p,band,redundant}, Kahn order and levels   (see section 3, same as demo/graph_data.json)
  -> UI       demo/kdg_demo.html         standalone demo of graph + Kahn + mastery gating (not part of the app)
```

Where the rejected / flagged courses and their reasons are: `data/processed/corpus_v2/rejected.csv` and `review.csv` (column `why`).

Run order (all offline):
```
python scripts/parse_corpus.py          # PDFs in data/raw -> corpus + reasons
python scripts/build_topics_nep.py      # corpus -> topics_nep.json, train/val/test split by course code
python scripts/merge_labels.py && python scripts/make_adjudication.py   # then independent adjudication -> scripts/finalize_labels.py
LABEL_DIR=data/labelling/final python scripts/train_nep.py --name nep5 --features nep2
LABEL_DIR=data/labelling/final python scripts/eval_models.py v5 nep4 nep5   # frozen evaluation on the unseen test PDFs
python scripts/export_demo_graph.py && python scripts/build_demo.py   # demo/kdg_demo.html
```

## 2. Model facts you must not oversell

Full report: **`MODEL_REPORT.md`** (numbers in `data/gold/eval_test_nep5*.txt`). Headline, measured on 18 courses from PDFs/branches never used for training (Chemical and Mechanical Sem III-IV, E&TC Sem 5/6, Mechanical Sem 5/6):

- Directed edge F1 **0.37** for the current model `nep5` vs **0.22** for the old v5, but only **0.35** for the trivial "adjacent topic in the same module" rule; on Mechanical Sem III-IV the trivial rule is better (0.41 vs 0.35). The model is only slightly better than that rule.
- Confidence is **calibrated** (error 0.002): pairs scored 0.7-1.0 were in the reference labels 77% of the time, 0.5-0.7 about 46%. Treat edges below 0.5 as uncertain.
- **The reference labels are written by AI, not people** (two independent labelling passes + an independent adjudicator; 3,118 final edges over 67 courses). Every score is softer than a human-checked test would be.
- Known parser defects (hyphenated names split in two, some glued list items, a few truncated last modules) were not changed in this run; fixing them and relabelling is the next planned task.
- Edges are within one course only; backward dependencies are untested (99% of labelled edges point forward).
- Thresholds live in `app/ml/model_artifact_nep5_meta.json` (`threshold`, `margin`, `reduce`).

## 3. Data contract (what the API should return per course)

```json
{
  "course": {"code": "2074113", "title": "Heat Transfer Operations", "source_pdf": "6.40-N-...pdf"},
  "model": {"name": "nep5", "accepted_threshold": 0.25, "uncertain_threshold": 0.10, "calibrated": true},
  "nodes": [{"id": "t1", "name": "Fourier's Law", "module": 1}],
  "edges": [{"a": 3, "b": 5, "p": 0.62, "band": "accepted", "redundant": false}],
  "kahn_order": [0, 1, 2],
  "kahn_level": [0, 0, 1]
}
```
- `edges[].a -> b` means topic `a` must be known before `b` (indices into `nodes`). `p` is the calibrated confidence.
- `band: accepted` (p >= accepted_threshold) edges **block** a learner. `band: uncertain` (0.10 <= p < threshold) edges are shown dashed and **never block**.
- `redundant: true` = implied by a longer accepted path; safe to hide, still true.
- `kahn_order` / `kahn_level` are computed over the accepted edges only. See `scripts/export_demo_graph.py` for the exact producer.

## 4. Backend plug-in points (reference code in `reference/app`, frozen; copy out when promoting)

| Need | Existing reference code | What to do |
|---|---|---|
| Upload + parse | `reference/app/api/builder_router.py` (`/pipeline/upload-and-parse`), old parser `reference/app/parser/nep_syllabus_parser.py` | Replace the parser call with `app/parser/*` (table-first). Return, per course: tier (accepted / review / rejected) and `why`. Keep returning HTTP 422 `low_confidence` if nothing passes. |
| Edge inference | `reference/app/services/relationship_inferencer.py` + `classifier_inference_service.py` (v5, forward pairs only, direction by list order) | Use `app.ml.infer.infer_course(topics, bundle=Bundle.get("nep5"), ctx={"title":..., "module_names":{idx:name}})`. It scores both directions, applies threshold/margin, caps (in <= 3, out <= 6), DAG guard. `reduce` is False for decisions; apply transitive reduction only for display. |
| Kahn ordering | `reference/app/services/sequence_engine.py` `SequenceEngine.get_topological_sequence` (in-degree BFS, raises on cycle) and `/sequence/topological` | Keep. Feed it accepted edges only. The response already needs `kahn_level` for column layout (depth = longest path from a start node). |
| Missing prerequisites | `reference/app/services/analytics_engine.py` `get_missing_prerequisites` = `Ancestors(T) \ Known`, ordered by the topological sequence, with percentage | Keep. Restrict to accepted edges so uncertain edges never create a "missing" item. |
| Ready now / next to study | `reference/app/services/recommendation_engine.py` | Keep; a topic is ready when all its accepted parents are known. |
| Saved mastery | `reference/app/api/persistence_router.py` `POST /persistence/user-progress` | Key mastery by stable topic key `<course_code>:<module>:<slug>` + syllabus hash, not by `t1,t2,...` (ids restart per course). Auth design: decision D5 in the local PRD (anonymous-first accounts) is a proposal, not decided. |

Model loading: `Bundle.get("nep5")` loads `app/ml/model_artifact_nep5.joblib`, `pca_artifact_nep5.joblib`, `calibrator_nep5.joblib`. The sentence encoder `all-MiniLM-L6-v2` must already be in the local Hugging Face cache; `infer.py` sets `HF_HUB_OFFLINE=1`, so inference never touches the network.

## 5. Frontend plug-in points (to be confirmed against the files you verify)

From `reference/frontend/src` (copied from branch `study-planner-ui`; unverified):
- `App.jsx` already keeps `knownConceptIds`, calls recommendations, topological sequence and missing prerequisites (see `services/api.js`: `getRecommendations`, `getMissingPrerequisites`, topological sequence).
- `gemini/FlowGraph.jsx` lays nodes out with `col * COL_WIDTH`, `row * ROW_HEIGHT` and highlights the selected path (`onPath`). Feed `col = kahn_level[i]`, `row = rank inside the level`.
- `gemini/GeminiApp.jsx` / `landing/Results.jsx` consume the pipeline response; they need the new fields (`p`, `band`, `redundant`, `kahn_level`).

Behaviour to implement (reference implementation: `demo/kdg_demo.template.html`, function names in brackets):
1. **Start nodes:** nodes with no blocking parent are `ready` and labelled START [`stateOf`, `render`].
2. **Mastery click:** a `ready` node becomes `mastered` on click; a `blocked` node does not change but opens its missing-prerequisite list; un-mastering a node also un-masters everything above it so no dependant stays green [`onNode`].
3. **Blocked:** a node is blocked until **every** accepted parent is mastered [`stateOf`].
4. **Missing prerequisites:** `Ancestors(T) \ Known`, in Kahn order, with percentage, plus "I already know all of these" [`renderSide`].
5. **Kahn on screen:** columns = `kahn_level`; an optional stepper shows the in-degree table and queue [`kahn`, `stepKahn`].
6. **Confidence:** edge width scales with `p`; uncertain edges dashed; a slider changes the blocking threshold.
7. **Feedback loop:** add a "wrong edge / wrong direction" button writing `edge_feedback` rows. This is the cheapest way to replace the provisional gold with real corrections.

## 6. Parser status

Table-first extraction with strict tiers. Latest run over the 24 PDFs in `data/raw`: 102 course occurrences auto-accepted (47 unique contents once identical courses across PDFs are merged), 33 occurrences (23 unique codes) flagged for review, 48 occurrences (18 unique codes) rejected; reasons are in the two CSVs. Labs are excluded by design. Known rejection causes: courses with no module table, last module not stitched across a page, PDFs whose text has no spaces between words, unattributed second module tables. Two independent AI review passes found the structure reliable and topic splitting the weak spot; the fixes from the second pass are in. Human verification of parsed topics is still outstanding.

## 7. Open items for the owner

- Confirm the correct frontend files (this guide is written against the reference copy).
- Rotate the Supabase service-role key that was hard-coded in the old repo (redacted in `reference/`; still in the old repo's git history).
- Decide authentication / mastery storage (anonymous-first is the recommendation, not a decision).
- Replace the provisional gold with human-checked edges; use the feedback button data.
- Add Sem 5/6 PDFs for the other branches, then re-run `parse_corpus.py` and retrain.
