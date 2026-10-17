# Glossary (single source of terms; do not rename concepts in other files)

| Term | Meaning |
|---|---|
| **KDG v2** | Knowledge Dependency Graph, second version. Upload an MU syllabus PDF, get topics, predicted prerequisite edges, graph, study order, bottlenecks. |
| **Scheme** | Syllabus regime named in the PDF text. In scope: NEP only. Out of scope: REV-2019. |
| **Family** | A group of PDFs that share one PyMuPDF line layout and therefore one parser. Family ids are lowercase kebab-case, e.g. `nep26-sem56`. Family ids in this PRD are HYPOTHESES from signature clustering until a `docs/formats/<family>.md` records the verification. |
| **Course** | One subject with a course code (letters+digits or 7-8 digits), title, modules. |
| **Module** | A numbered/Roman-numbered unit of a Course. |
| **Topic** | An atomic concept node inside a Module. Validity rules: `docs/formats/topic_validity.md`. |
| **Edge** | A directed pair (prerequisite Topic -> dependent Topic) with `score`, `confidence`, `provenance`. |
| **Score** | Raw XGBoost pair probability before calibration. |
| **Confidence** | Calibrated probability that an Edge is correct (after calibration on validation data). |
| **Abstain band** | Confidence interval in which an Edge is shown as "uncertain" instead of accepted/rejected. |
| **parse_confidence** | Per-Topic and per-Course value in [0,1] from the parser's own checks (not from the model). |
| **Confidence gate** | Parser rule that rejects a Course/PDF with HTTP 422 `low_confidence` instead of emitting junk topics. |
| **Golden course** | A hand-checkable expected extraction in `tests/golden/<family>/<course>.json`. Always `status: DRAFT - needs human sign-off` until a human verifies it. |
| **Gold set** | Human-labelled Edge pairs used to evaluate/calibrate the model. Different from golden courses. |
| **Teacher labels** | Edge labels produced by an LLM (Gemini, 2 runs, agreement only). Training-time only. |
| **Offline inference** | Prediction runs with no network and no API key. |
| **Mastery state** | A user's saved per-Topic status (see decisions D5). |
| **Evidence** | A file under `docs/evidence/` holding the command output that supports a claim. |
| **UNKNOWN** | A fact not observed; always listed in `docs/open_questions.md`. |
