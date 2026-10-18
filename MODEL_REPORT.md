# KDG v2 - how the model worked (report for review, round 2)

Date: 2026-10-17. Model: `nep6` (`app/ml/model_artifact_nep6*`). Numbers: `data/gold/eval_test_nep6.txt`.

## What changed in this round
- Splitter and truncation defects fixed, all PDFs re-parsed, strict gate re-applied: **58 courses** kept (3 of them, 2115116, PCC501 and 24061132, were not relabelled and are left out of training and testing).
- Relabelled from scratch: two independent AI passes (agreement: overlap 0.62), then an independent adjudicator on the 1,277 disputed edges (27% kept). Final: **2,447 edges over 55 courses**. Labels are AI-made, not human-checked.
- Test set: 18 courses from PDFs/branches never used for training (Chemical III-IV, Mechanical III-IV, E&TC and Mechanical Sem 5/6, CS electives).

## Results on unseen courses (directed edges, final labels)
| Model | Precision | Recall | F1 | PR-AUC | Calibration error |
|---|---|---|---|---|---|
| old v5 | 0.185 | 0.378 | 0.248 | 0.111 | 0.216 |
| nep5 (trained on old topics/labels) | 0.353 | 0.447 | 0.394 | 0.340 | 0.002 |
| **nep6 (this round)** | 0.336 | 0.495 | **0.400** | 0.335 | 0.001 |
| baseline: adjacent topic in module | 0.322 | 0.428 | 0.368 | n/a | n/a |

Honest reading: nep6 is clearly better than v5 (0.40 vs 0.25) and well calibrated, but only **about 3 points above the trivial adjacent-topic rule** and level with nep5 (difference is within noise). Relabelling did not raise accuracy; the ceiling is label quality and the chain-like nature of the labels. In 4 of 18 courses nep6 is below 0.37 F1 (e.g. 24051143 0.19, PEC6022 0.33). Confidence: 0.5-0.7 -> 59% observed, 0.7+ -> 80% (only 49 pairs). Treat edges below 0.5 as uncertain. Direction is right for 99% of linked pairs, but 99% of labelled edges point forward, so backward dependencies are untested.

## By department (`data/gold/eval_by_department_nep6.txt`)
Training courses are almost all Computer / IT / CSE (AI&ML); every test department below is unseen.
| Test department | courses | P | R | F1 | next-topic rule F1 |
|---|---|---|---|---|---|
| Chemical Sem 3/4 | 6 | 0.396 | 0.527 | 0.452 | 0.429 |
| E&TC Sem 5/6 (DSA, Algorithms, Robotics electives) | 3 | 0.325 | 0.604 | 0.423 | 0.377 |
| Mechanical Sem 3/4 | 4 | 0.323 | 0.411 | 0.362 | 0.362 |
| Mechanical Sem 5/6 | 5 | 0.311 | 0.498 | 0.383 | 0.326 |
The gain over the trivial rule is largest on Mechanical Sem 5/6 and zero on Mechanical Sem 3/4.

## Next steps
Human check of about 300 sampled edges (and the frontend "wrong edge" data), Sem 5/6 PDFs for Civil/Electrical/Chemical, adjudicate the 3 left-out courses, then cross-course prerequisites.
