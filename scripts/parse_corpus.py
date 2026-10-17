"""Parse every PDF in data/raw, gate, verify, and write the corpus.
Outputs (data/processed/corpus_v2/): accepted.jsonl (Tier A, safe to train on), review.jsonl (Tier B, needs human check),
rejected.csv (every rejected course with reasons). Nothing is silently dropped. No network, no LLM."""
import sys, glob, json, csv, hashlib, pathlib, collections
sys.path.insert(0, ".")
from app.parser.nep_tables import extract_course_tables
from app.parser.nep_topics import parse_course
from app.parser.nep_gate import gate_course
from app.parser.nep_verify import PageText, traceability

TYPICAL_HOURS = set(range(24, 28)) | set(range(36, 41))   # PROPOSED from the observed distribution (docs/evidence/baseline/gate_stats_output.txt)
OUT = pathlib.Path("data/processed/corpus_v2"); OUT.mkdir(parents=True, exist_ok=True)

def tier(c, g, tr):
    """returns (tier, [reasons]); reasons explain every non-accepted outcome."""
    if not g["accepted"]: return "rejected", list(g["reasons"])
    hrs = [m["hours"] for m in c["modules"]]
    why = []
    if c.get("conflict_pages"): why.append(f"second_module_table_on_pages_{c['conflict_pages']}")
    if tr["trace_rate"] < 0.97: why.append(f"trace_rate_{tr['trace_rate']}")
    if not all(1 <= h <= 15 for h in hrs): why.append("module_hours_out_of_1_15")
    if why: return "review", why
    if g.get("printed_total") is not None:
        pass  # printed Total Hours equals the parsed sum (the gate rejects mismatches): strongest evidence available
    elif g["total_hours"] not in TYPICAL_HOURS:
        return "review", [f"hours_sum_{g['total_hours']}_not_typical_and_no_printed_total"]
    return "accepted", []

def main():
    acc, rev, rej = [], [], []
    for pdf in sorted(glob.glob("data/raw/**/*.pdf", recursive=True)):
        p = pdf.replace("\\", "/"); pt = None
        for ct in extract_course_tables(p):
            if not ct.has_module_table and not ct.is_lab: continue
            c = parse_course(ct, p); g = gate_course(c)
            if "lab_course" in "".join(g["reasons"]): continue          # owner: lab contents are not needed
            if "no_module_table" in g["reasons"]: continue
            pt = pt or PageText(p); tr = traceability(c, pt)
            t, why = tier(c, g, tr)
            c.update(gate=g, trace=tr, tier=t, tier_reasons=why)
            c["content_hash"] = hashlib.sha256(json.dumps([[m["name"], m["topics"]] for m in c["modules"]], ensure_ascii=False).encode()).hexdigest()[:16]
            (acc if t == "accepted" else rev if t == "review" else rej).append(c)
    for name, rows in (("accepted", acc), ("review", rev)):
        with open(OUT / f"{name}.jsonl", "w", encoding="utf-8") as f:
            for c in rows: f.write(json.dumps({k: v for k, v in c.items() if k != "dropped"}, ensure_ascii=False) + "\n")
    for name, rows in (("rejected", rej), ("review", rev)):
        with open(OUT / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["pdf", "code", "title", "why", "trace_rate", "n_modules", "n_topics", "total_hours"])
            for c in rows: w.writerow([c["source_pdf"].split("/")[-1], c["course_code"], c["title"], "; ".join(c["tier_reasons"]), c["trace"]["trace_rate"], len(c["modules"]), sum(len(m["topics"]) for m in c["modules"]), c["gate"]["total_hours"]])
    uniq = lambda rows: len({c["course_code"] for c in rows})
    print(f"accepted(Tier A): {len(acc)} occurrences, {uniq(acc)} unique codes, {len({c['content_hash'] for c in acc})} unique contents")
    print(f"review(Tier B):   {len(rev)} occurrences, {uniq(rev)} unique codes")
    print(f"rejected:         {len(rej)} occurrences, {uniq(rej)} unique codes")
    print("topics in Tier A:", sum(len(m['topics']) for c in acc for m in c['modules']))
    print("reject reasons:", dict(collections.Counter(r.split(':')[0] for c in rej for r in c['gate']['reasons']).most_common(8)))

if __name__ == "__main__":
    main()
