# Adjudication rubric

Two independent labellers disagreed about some prerequisite edges inside one course syllabus. You decide each disputed edge.
Input: `data/labelling/adjudicate/<course>.json` -> `topics` (syllabus order) and `candidates` [{i, a, b, a_name, b_name}], meaning candidate edge "a must be understood before b". The order of candidates is random and carries no information.
Write `data/labelling/adjudicated/<course>.json` as `{"keep":[<candidate i>, ...]}` listing ONLY the candidates you accept.

Accept a candidate only if ALL hold:
1. **Direction:** a student who has not learned `a` cannot properly learn `b` (b depends on a). Similarity, siblings, "same family" and "appears next to it" are NOT reasons. If the reverse direction is the real dependency, reject.
2. **Direct:** `a` is an immediate prerequisite, not just a distant ancestor of `b` (reject if some other topic obviously sits between them).
3. **Sure:** you are at least ~75% confident using your own subject knowledge.
4. If both directions of the same pair appear, keep at most one (or none).
Fragments (partial phrases, list heads like "Types", "Introduction") get no edges.
You are expected to REJECT many candidates; do not rubber-stamp.
Do not open any other file under data/labelling or data/gold. No network, no git. After writing, run `python scripts/check_adjudication.py <your course ids>` and fix errors.
Final report (max 6 lines): per course, candidates, kept.
