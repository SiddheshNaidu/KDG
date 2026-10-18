"""Pure graph operations on one analysed course (no model, no I/O).

Edges are dicts {source, target, confidence, band}. Only band == "accepted" edges BLOCK a learner;
"uncertain" edges are display-only and never create a missing prerequisite."""
from __future__ import annotations
import heapq


def blocking(edges):
    return [(e["source"], e["target"]) for e in edges if e["band"] == "accepted"]


def kahn(node_ids, pairs):
    """Kahn's algorithm. Returns (order, level) where level = longest path from a start node.
    Among topics that are ready at the same time the one earliest in the syllabus goes first (min-heap on position),
    so the study order stays as close to the printed syllabus as the prerequisites allow."""
    pos = {n: i for i, n in enumerate(node_ids)}
    indeg = {n: 0 for n in node_ids}; out = {n: [] for n in node_ids}
    for a, b in pairs:
        out[a].append(b); indeg[b] += 1
    level = {n: 0 for n in node_ids}
    heap = [pos[n] for n in node_ids if indeg[n] == 0]; heapq.heapify(heap); order = []
    while heap:
        u = node_ids[heapq.heappop(heap)]; order.append(u)
        for v in out[u]:
            level[v] = max(level[v], level[u] + 1); indeg[v] -= 1
            if indeg[v] == 0:
                heapq.heappush(heap, pos[v])
    if len(order) != len(node_ids):
        raise ValueError("cycle in prerequisite graph")
    return order, level


def parents(pairs):
    p = {}
    for a, b in pairs:
        p.setdefault(b, []).append(a)
    return p


def ancestors(target, par):
    seen, stack = set(), [target]
    while stack:
        for a in par.get(stack.pop(), []):
            if a not in seen:
                seen.add(a); stack.append(a)
    return seen


def descendants(node, pairs):
    ch = {}
    for a, b in pairs:
        ch.setdefault(a, []).append(b)
    seen, stack = set(), [node]
    while stack:
        for b in ch.get(stack.pop(), []):
            if b not in seen:
                seen.add(b); stack.append(b)
    return seen


def node_states(node_ids, edges, mastered):
    """mastered: set of node ids the learner has marked as known.
    state: mastered | ready (every blocking parent mastered; START when it has no blocking parent) | blocked."""
    par = parents(blocking(edges)); out = {}
    for n in node_ids:
        ps = par.get(n, [])
        if n in mastered:
            st = "mastered"
        elif all(p in mastered for p in ps):
            st = "ready"
        else:
            st = "blocked"
        out[n] = dict(state=st, is_start=not ps, waiting_on=[p for p in ps if p not in mastered])
    return out


def missing_for(target, node_ids, edges, mastered):
    """Ancestors(target) minus mastered, in Kahn order (study these first, in this order)."""
    pairs = blocking(edges); par = parents(pairs)
    anc = ancestors(target, par)
    order, _ = kahn(node_ids, pairs)
    miss = [n for n in order if n in anc and n not in mastered]
    return miss, (round(100 * (len(anc) - len(miss)) / len(anc), 1) if anc else 100.0), len(anc)


def bottlenecks(node_ids, edges, top_n=5):
    pairs = blocking(edges)
    direct = {}
    for a, _ in pairs:
        direct[a] = direct.get(a, 0) + 1
    scored = [(len(descendants(n, pairs)), direct.get(n, 0), n) for n in node_ids]
    scored = [s for s in scored if s[0] > 0]
    scored.sort(key=lambda s: (-s[0], -s[1], node_ids.index(s[2])))
    return scored[:top_n]
