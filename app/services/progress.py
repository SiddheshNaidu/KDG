"""Learner progress on one analysis: node states, mastery rules, missing prerequisites, saved mastery.

Mastery is keyed by (user_id, analysis_id) and stores stable topic ids ('<course>:<module>:<slug>'), so it survives
re-uploads of the same PDF. Storage is a JSON file per user and analysis under data/runtime/progress (git-ignored).
user_id is an anonymous id the frontend generates once and keeps in localStorage (decision D5 is still a proposal)."""
from __future__ import annotations
import json
from app.services import graph_ops
from app.services.pipeline import AnalysisError, ID_RE, load_analysis, _store


def _check(user_id):
    if not ID_RE.match(user_id or ""):
        raise AnalysisError(400, "invalid user_id (letters, digits, '-' and '_' only)")


def status(analysis_id: str, mastered: list[str], target: str | None = None) -> dict:
    a = load_analysis(analysis_id)
    ids = [n["id"] for n in a["nodes"]]; names = {n["id"]: n["name"] for n in a["nodes"]}
    known = {m for m in mastered if m in names}
    st = graph_ops.node_states(ids, a["edges"], known)
    order = a["kahn_order"]
    out = dict(analysis_id=analysis_id, mastered=[n for n in order if n in known],
               nodes=st,
               start_nodes=[n for n in order if st[n]["is_start"]],
               ready=[n for n in order if st[n]["state"] == "ready"],
               next_up=next((n for n in order if st[n]["state"] == "ready"), None),
               progress_percent=round(100 * len(known) / max(1, len(ids)), 1))
    if target:
        out["target"] = missing(analysis_id, target, list(known))
    return out


def missing(analysis_id: str, target: str, known: list[str]) -> dict:
    a = load_analysis(analysis_id)
    ids = [n["id"] for n in a["nodes"]]; names = {n["id"]: n["name"] for n in a["nodes"]}
    if target not in names:
        raise AnalysisError(404, "unknown topic id")
    miss, pct, total = graph_ops.missing_for(target, ids, a["edges"], set(known))
    return dict(target_id=target, target_name=names[target], total_prerequisites=total, known_percent=pct,
                missing=[dict(id=m, name=names[m]) for m in miss])


def _file(user_id, analysis_id):
    _check(user_id); load_analysis(analysis_id)
    return _store("progress") / f"{user_id}__{analysis_id}.json"


def saved(user_id: str, analysis_id: str) -> list[str]:
    f = _file(user_id, analysis_id)
    return json.loads(f.read_text(encoding="utf-8")).get("mastered", []) if f.exists() else []


def set_mastery(user_id: str, analysis_id: str, topic_id: str, mastered: bool, force: bool = False) -> dict:
    """Rules: only a READY topic can be mastered (force=True = 'I already know this and everything before it').
    Un-mastering a topic also un-masters every topic that depends on it, so no dependant stays green."""
    a = load_analysis(analysis_id)
    ids = [n["id"] for n in a["nodes"]]
    if topic_id not in ids:
        raise AnalysisError(404, "unknown topic id")
    known = set(saved(user_id, analysis_id)); acc = graph_ops.blocking(a["edges"])
    if mastered:
        st = graph_ops.node_states(ids, a["edges"], known)[topic_id]
        if st["state"] == "blocked" and not force:
            raise AnalysisError(409, dict(error="blocked", waiting_on=st["waiting_on"],
                                          missing=missing(analysis_id, topic_id, list(known))["missing"]))
        if force:
            known |= graph_ops.ancestors(topic_id, graph_ops.parents(acc))
        known.add(topic_id)
    else:
        known.discard(topic_id); known -= graph_ops.descendants(topic_id, acc)
    _file(user_id, analysis_id).write_text(json.dumps(dict(mastered=sorted(known))), encoding="utf-8")
    return status(analysis_id, sorted(known))
