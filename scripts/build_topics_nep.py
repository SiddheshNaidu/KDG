"""Build the course/topic dataset for labelling and training from the Tier A corpus (data/processed/corpus_v2/accepted.jsonl).
- dedupe identical courses across PDFs by content_hash
- topic ids t1..tn in syllabus order (module order, then list order); consecutive/repeated duplicate names within a course dropped
- deterministic split by course: TEST = two PDFs the model never sees (unknown-PDF evaluation), VAL = every 5th remaining course, TRAIN = rest"""
import json, re, pathlib, collections
ACC = pathlib.Path("data/processed/corpus_v2/accepted.jsonl")
TEST_PDFS = {"6.40-N-Chemical-Engineering-Sem-III-IV.pdf": "test_chem", "6.35-N-B.E.-Mechanical-EngineeringSem-III-IV.pdf": "test_mech"}
EXCLUDE = {"BSC2022", "BSC2023", "2394113", "2404113"}   # reviewed as BAD: source text has no separators / lost items (tierA_review_r2)
rows = [json.loads(l) for l in ACC.open(encoding="utf-8") if json.loads(l)["course_code"] not in EXCLUDE]
by_hash = collections.OrderedDict()
for r in rows: by_hash.setdefault(r["content_hash"], []).append(r)
test_hashes = {h for h, rs in by_hash.items() if any(x["source_pdf"].split("/")[-1] in TEST_PDFS for x in rs)}
courses, used_ids = {}, set()
for h, rs in by_hash.items():
    r = rs[0]
    cid = r["course_code"] if r["course_code"] not in used_ids else f"{r['course_code']}_{h[:6]}"
    used_ids.add(cid)
    topics, mods, seen = [], [], set()
    for m in r["modules"]:
        names = []
        for t in m["topics"]:
            k = re.sub(r"\W+", " ", t.lower()).strip()
            if k in seen: continue
            seen.add(k); names.append(t)
            topics.append(dict(id=f"t{len(topics)+1}", name=t, module_idx=m["number"], position=len(topics) + 1))
        mods.append(dict(index=m["number"], name=m["name"], topics=names))
    courses[cid] = dict(course_code=r["course_code"], course_title=r["title"], content_hash=h, n_topics=len(topics),
                        source_pdfs=sorted({x["source_pdf"].split("/")[-1] for x in rs}), modules=mods, topics=topics)
# Split by COURSE CODE (variants of the same course in different PDFs must share a split: no leakage)
test_codes = {v["course_code"] for v in courses.values() if v["content_hash"] in test_hashes}
test = [c for c, v in courses.items() if v["course_code"] in test_codes]
rest_codes = sorted({v["course_code"] for c, v in courses.items() if c not in test})
val_codes = set(rest_codes[::5])
val = [c for c, v in courses.items() if c not in test and v["course_code"] in val_codes]
train = [c for c in courses if c not in test and c not in val]
for c in courses:
    courses[c]["split"] = "test" if c in test else "val" if c in val else "train"
json.dump(courses, open("data/processed/topics_nep.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
inp = pathlib.Path("data/labelling/inputs"); inp.mkdir(parents=True, exist_ok=True)
for c, v in courses.items():
    json.dump(dict(course=c, title=v["course_title"], modules=[dict(index=m["index"], name=m["name"]) for m in v["modules"]],
                   topics=[dict(id=t["id"], name=t["name"], module=t["module_idx"]) for t in v["topics"]]),
              open(inp / f"{c}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("courses", len(courses), "train", len(train), "val", len(val), "test", len(test))
print("topics train/val/test:", [sum(courses[c]["n_topics"] for c in grp) for grp in (train, val, test)])
print("test courses:", [(c, courses[c]["course_title"][:28]) for c in test])
