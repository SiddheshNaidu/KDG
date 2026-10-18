"""Accepted / review / rejected tier for one parsed course (shared by scripts/parse_corpus.py and the API)."""

TYPICAL_HOURS = set(range(24, 28)) | set(range(36, 41))   # PROPOSED from the observed distribution (docs/evidence/baseline/gate_stats_output.txt)

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
