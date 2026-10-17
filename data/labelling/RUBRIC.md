# Prerequisite-edge labelling rubric (pass B, independent)

You label PREREQUISITE EDGES between topics inside ONE university course syllabus, for training a model.
Inputs: `data/labelling/inputs/<course>.json` (fields: course, title, modules[{index,name}], topics[{id,name,module}] in syllabus order).
For each course in your list, write `data/labelling/pass_B/<course>.json` as
`{"edges":[{"a":"t3","b":"t7","why":"<=12 words"}, ...]}` meaning: topic `a` must be understood BEFORE topic `b` (a is a prerequisite of b).

## Independence
Do NOT open `data/labelling/claude/`, `data/labelling/pass_A/`, `data/gold/`, any `*.pyc`, or any other file that contains edges for these courses. Use only the input files and your own subject knowledge.

## Strict rules
1. **Direction is everything.** a->b means a student who has not learned a cannot properly learn b. Similarity or relatedness is symmetric and is NOT a prerequisite: never add an edge only because two topics are alike, belong to the same family, or appear next to each other. If you cannot say which one must come first, add no edge.
2. **Only direct prerequisites.** If a->b and b->c are real, do not also add a->c.
3. **Be conservative:** add an edge only when you are at least ~75% sure. Many topics are foundational or independent and legitimately have NO incoming edge; do not force attachment. Typical density is about 0.6-1.0 edges per topic, never more than 3 incoming edges for one topic.
4. Syllabus order is only a hint; real dependencies can point forward or backward in the list. Do not assume "listed earlier = prerequisite". A list of sibling items (types, examples, algorithms of the same kind) usually has NO edges between the siblings, only from the shared foundation to each sibling.
5. Use only topic ids that exist in the input. No self-loops, no duplicates, no two-way edges, no cycles.
6. Use your real knowledge of the subject to judge dependencies. Topics are short syllabus phrases (some are fragments of a longer phrase); if a topic is too vague or a fragment, give it no edges.
7. Work course by course. After writing all your files run `python scripts/check_labels.py data/labelling/pass_B <your course ids...>` and fix every ERR line.

Write only inside `data/labelling/pass_B/`. No network, no git, do not edit any other file.
Final report (max 8 lines): per course id, topics, edges; name any course you found too noisy to label well.

## Perspective
Ask: "could a capable student understand topic b at all without already knowing topic a?" If yes, no edge.
