# KDG v2 - how the model worked (report for review)

Date of run: 2026-10-17. Model: `nep5` (`app/ml/model_artifact_nep5*`). All numbers come from `data/gold/eval_test_nep5.txt` and `data/gold/eval_test_nep5_groups.txt`.

## 1. Short answer
- The new model is **clearly better than the old v5** on courses neither has seen (directed F1 0.37 vs 0.22).
- It is **only slightly better than a trivial "link each topic to the next one in its module" rule** (0.37 vs 0.35 overall) and **worse than that rule on Mechanical Sem III-IV**. Do not describe it as accurate.
- Its **confidence values are trustworthy** (calibration error 0.002): when it says 0.75 about 77% of such edges are in the reference labels, when it says 0.6 about 46%.
- Adding Sem 5/6 data from IT, Computer Engineering and CSE (AI&ML) did **not** improve results on unseen branches compared with the model trained before them (nep4: 0.377). Label quality, not data volume, is the limit.
- **The reference labels are written by AI, not people**, so every number below is softer than a human-checked test.

## 2. Data used
| | |
|---|---|
| NEP PDFs in `data/raw` | 28 (24 earlier + Computer Eng, E&TC, Mechanical and CSE (AI&ML) Sem 5/6; the last was restored from the old repo) |
| Courses parsed to the strict "accepted" tier | 128 occurrences, 76 unique contents |
| Courses used for the model | 67 (6 excluded as bad or truncated after review: 24061132, PEC6024, PCC501, 2116111, 2115116, 2405511) |
| Split (by course code, so variants never leak) | train 39 courses / 2,839 topics, validation 10 / 732, test 18 / 1,230 |
| Test = branches or PDFs never used for anything | Chemical Sem III-IV (6 courses), Mechanical Sem III-IV (3), **E&TC Sem 5/6 (3)**, **Mechanical Sem 5/6 (6)** |
| Labels | 3,118 prerequisite edges: 2,541 that two independent AI labellers agreed on + 577 kept by a third independent adjudicator out of 2,172 disputed (27%) |
| Labeller agreement | overlap (Jaccard) 0.54; direction conflicts only 20 edges in about 7,900 |

## 3. What the model is
XGBoost on 63 features for every ordered topic pair inside one course: the 40 v5 features (sentence-embedding similarity, position gaps, name containment, 32 PCA components of the embeddings) plus 23 structure features (neighbourhood in the list, position in module, similarity to module and course titles, relative similarity ranks). Hyper-parameters, the threshold (0.25, calibrated confidence) and the direction margin were chosen on validation courses only; the confidence is isotonic-calibrated on validation pairs. Inference is offline (no network, no API key).

## 4. Results on courses the model never saw (directed edges, against the final labels)
| Model | Precision | Recall | F1 | PR-AUC (all pairs) |
|---|---|---|---|---|
| old v5 | 0.160 | 0.358 | 0.221 | 0.089 |
| nep4 (trained before the new PDFs) | 0.337 | 0.429 | 0.377 | 0.317 |
| **nep5 (this report)** | 0.332 | 0.419 | 0.370 | 0.310 |
| baseline: adjacent topic in module | 0.300 | 0.415 | 0.348 | n/a |

By test group (F1: v5 / nep4 / nep5 / adjacent baseline):
| Group | gold edges | v5 | nep4 | nep5 | baseline |
|---|---|---|---|---|---|
| Chemical Sem III-IV | 234 | 0.294 | 0.442 | 0.427 | 0.410 |
| **E&TC Sem 5/6 (unseen branch)** | 94 | 0.246 | 0.417 | **0.444** | 0.395 |
| Mechanical Sem III-IV | 198 | 0.243 | 0.350 | 0.349 | **0.412** |
| **Mechanical Sem 5/6 (unseen branch)** | 287 | 0.170 | 0.329 | 0.323 | 0.266 |

Confidence reliability for nep5 (pairs the model scored): 0.1-0.2 -> observed 14%; 0.2-0.3 -> 22%; 0.3-0.5 -> 33%; 0.5-0.7 -> 46% (166 pairs); 0.7-1.0 -> 77% (43 pairs). Expected calibration error 0.0019.
Direction: 98% of correctly linked pairs have the right direction, but 99% of labelled edges point forward in the syllabus, so backward dependencies are untested.

## 5. Why it is not better, and what that means
1. **Labels are chain-heavy and AI-made.** About 40% of edges join neighbouring topics, so the neighbour rule is strong, and the labellers only agreed on 54% of edges.
2. **The parse still has defects.** Reviewers found splitter bugs (a hyphenated name such as "Mann-Whitney U" splits in two, some list items glue together) and truncated last modules in a few courses. Junk is about 3-12% in the courses kept; I did not change the splitter during this run because it would renumber topics and invalidate all labels. Fixing it and relabelling is the next planned task.
3. **Branch transfer is weak.** Mechanical and E&TC Sem 5/6 are only slightly above the baseline, so one model for all branches is not yet justified.
4. **Parser coverage:** of the new PDFs, 28 courses reached the accepted tier; the rest are rejected or flagged for review with reasons in `data/processed/corpus_v2/*.csv`. No Civil, Electrical or Chemical Sem 5/6 syllabi were found online.

## 6. Recommendation and next steps (for your review)
- Use `nep5` for the integration (same quality as nep4, more branches in training). Treat edges below 0.5 as "uncertain" in the UI; they are only right about a third of the time.
- Highest-value next steps: (1) fix the splitter and truncation issues, re-parse and relabel; (2) have a person check a sample of edges (about 300) and use the frontend "wrong edge" button data as corrections; (3) obtain the official Sem 5/6 files for the remaining branches; (4) model cross-course prerequisites later.
- Reproduce: see `INTEGRATION.md` section 1.
