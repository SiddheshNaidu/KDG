"""PDF -> courses -> one course's topics -> prerequisite edges -> the analysis payload the UI draws.

Flow for POST /api/v1/analyze (see PROJECT_STATUS.md, section "How the API is wired"):
  read_pdf()        parser (app/parser/*) on the uploaded bytes: every non-lab course with its tier (accepted/review/rejected)
  pick_course()     subject chosen by the user, or the only course; several courses -> {"needs_subject": true, "subjects": [...]}
  topics_for()      accepted/review -> parser topics; rejected or nothing found -> fallback.extract_topics
  edges_for()       nep6 model (app/ml/infer.py); exception or zero accepted edges -> fallback.prerequisite_edges
                    -> last resort: link neighbouring topics inside a module (measured F1 0.37 vs model 0.40)
  background_for()  fallback.background (assumed-but-untaught knowledge); without a key the printed 'Prerequisite' row
  build_payload()   nodes, edges (accepted / uncertain), Kahn order + levels, study flow, bottlenecks
The payload never says which component produced what; the server log does."""
from __future__ import annotations
import gc, hashlib, json, logging, os, pathlib, re, tempfile
import fitz

from app.parser.nep_tables import extract_course_tables
from app.parser.nep_topics import parse_course, split_topics
from app.parser.nep_gate import gate_course
from app.parser.nep_verify import PageText, traceability
from app.parser.nep_tier import tier
from app.services import fallback, graph_ops

log = logging.getLogger("kdg.pipeline")
MODEL_NAME = os.environ.get("KDG_MODEL", "nep6")
UNCERTAIN = 0.10                     # edges with UNCERTAIN <= p < threshold are shown dashed and never block
RUNTIME = pathlib.Path(os.environ.get("KDG_RUNTIME_DIR", pathlib.Path(__file__).resolve().parents[2] / "data" / "runtime"))
ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,80}$")


class AnalysisError(Exception):
    def __init__(self, status: int, detail):
        super().__init__(str(detail)); self.status = status; self.detail = detail


# ---------------------------------------------------------------- model loading (once per process)
_bundle = None

def bundle():
    global _bundle
    if _bundle is None:
        from app.ml.infer import Bundle
        _bundle = Bundle.get(MODEL_NAME)
    return _bundle


def warm_up():
    b = bundle(); b.embed(["warm up"])
    log.info("model %s loaded (threshold %.2f)", MODEL_NAME, b.threshold)


# ---------------------------------------------------------------- parsing
def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60] or "topic"


def pdf_text(content: bytes) -> str:
    with fitz.open(stream=content, filetype="pdf") as d:
        return "\n".join(p.get_text() for p in d)


def read_pdf(content: bytes) -> list[dict]:
    """Every non-lab course in the PDF with a module table, best tier per course code, in document order."""
    # parser objects keep the file open on Windows; collect them before the temp dir is removed
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        path = os.path.join(tmp, "upload.pdf")
        open(path, "wb").write(content)
        try:
            tables = extract_course_tables(path)
        except Exception as exc:
            log.warning("parser failed on upload: %s", exc); return []
        pt, best = None, {}
        rank = {"accepted": 0, "review": 1, "rejected": 2}
        for ct in tables:
            if not ct.has_module_table or ct.is_lab:
                continue
            c = parse_course(ct, path); g = gate_course(c)
            if any("lab_course" in r for r in g["reasons"]) or "no_module_table" in g["reasons"]:
                continue
            pt = pt or PageText(path); tr = traceability(c, pt)
            t, why = tier(c, g, tr)
            c.update(tier=t, tier_reasons=why)
            old = best.get(c["course_code"])
            if old is None or rank[t] < rank[old["tier"]]:
                best[c["course_code"]] = c
        del tables, pt; gc.collect()
        return list(best.values())


def match_subject(courses: list[dict], subject: str) -> dict | None:
    s = subject.strip().lower()
    for c in courses:
        code, title = c["course_code"].lower(), c["title"].lower()
        if s == code or code in s or s in f"{code} {title}" or (title and title in s):
            return c
    return None


def topics_from_parser(c: dict) -> tuple[list[dict], dict]:
    topics, seen, used = [], set(), set()
    for m in c["modules"]:
        for name in m["topics"]:
            k = re.sub(r"\W+", " ", name.lower()).strip()
            if not k or k in seen:
                continue
            seen.add(k)
            tid = f"{c['course_code']}:{m['number']}:{_slug(name)}"
            while tid in used:
                tid += "-2"
            used.add(tid)
            topics.append(dict(id=tid, name=name, module=int(m["number"]), module_title=m["name"]))
    ctx = dict(title=c["title"], module_names={int(m["number"]): m["name"] for m in c["modules"]})
    return topics, ctx


def topics_from_fallback(ex: dict, code_hint: str = "") -> tuple[list[dict], dict, dict]:
    code = (ex.get("course_code") or code_hint or "course").strip().replace(" ", "")
    topics, seen, used, mods = [], set(), set(), {}
    for t in ex.get("topics", []):
        name = str(t.get("name", "")).strip(); k = re.sub(r"\W+", " ", name.lower()).strip()
        if not k or k in seen:
            continue
        seen.add(k); mod = int(t.get("unit_number") or 1); mods.setdefault(mod, str(t.get("unit_title", "")).strip() or f"Module {mod}")
        tid = f"{code}:{mod}:{_slug(name)}"
        while tid in used:
            tid += "-2"
        used.add(tid)
        topics.append(dict(id=tid, name=name, module=mod, module_title=mods[mod]))
    topics.sort(key=lambda t: t["module"])            # stable: keeps order inside a module
    meta = dict(course_code=code, title=(ex.get("course_title") or "Course Syllabus").strip())
    return topics, dict(title=meta["title"], module_names=mods), meta


# ---------------------------------------------------------------- edges
def _adjacent_rule(topics):
    return [(i, i + 1) for i in range(len(topics) - 1) if topics[i]["module"] == topics[i + 1]["module"]]


def _dag_filter(pairs, n):
    import networkx as nx
    G = nx.DiGraph(); G.add_nodes_from(range(n)); keep = []
    for a, b in pairs:
        if G.has_edge(a, b) or G.in_degree(b) >= 3 or G.out_degree(a) >= 6:
            continue
        G.add_edge(a, b)
        if nx.is_directed_acyclic_graph(G):
            keep.append((a, b))
        else:
            G.remove_edge(a, b)
    return keep


def edges_for(topics, ctx, title):
    """Returns [(i, j, p, band)] with i -> j meaning topic i before topic j."""
    from app.ml.infer import score_pairs, infer_course
    n, b, S = len(topics), None, None
    if n < 2:
        return []
    try:
        b = bundle()
        S = score_pairs(topics, b, True, ctx=ctx)
        found = infer_course(topics, bundle=b, threshold=UNCERTAIN, margin=b.margin, reduce=False, scores=S, ctx=ctx)
        idx = {t["id"]: i for i, t in enumerate(topics)}
        out = [(idx[e.a], idx[e.b], float(e.confidence), "accepted" if e.confidence >= b.threshold else "uncertain") for e in found]
        if any(x[3] == "accepted" for x in out):
            log.info("edges: model (%d accepted, %d uncertain)", sum(x[3] == "accepted" for x in out), sum(x[3] == "uncertain" for x in out))
            return out
        log.warning("edges: model produced no accepted edge")
    except Exception as exc:
        log.exception("edges: model failed: %s", exc)
    thr = b.threshold if b is not None else 0.2
    score = (lambda i, j: max(S.get((i, j), 0.0), thr)) if S else (lambda i, j: thr)
    try:
        pairs = _dag_filter(fallback.prerequisite_edges(title, topics), n)
        if pairs:
            return [(i, j, round(score(i, j), 4), "accepted") for i, j in pairs]
    except fallback.FallbackUnavailable as exc:
        log.warning("edges: fallback unavailable (%s)", exc)
    log.warning("edges: neighbour rule used")
    return [(i, j, round(score(i, j), 4), "accepted") for i, j in _adjacent_rule(topics)]


# ---------------------------------------------------------------- background knowledge
def background_for(title, topics, printed, given=None):
    by_name = {re.sub(r"\W+", " ", t["name"].lower()).strip(): t for t in topics}

    def resolve(names):
        out = []
        for nm in names or []:
            k = re.sub(r"\W+", " ", str(nm).lower()).strip()
            t = by_name.get(k) or next((v for kk, v in by_name.items() if k and (k in kk or kk in k)), None)
            if t and t["id"] not in [o["id"] for o in out]:
                out.append(dict(id=t["id"], name=t["name"]))
        return out

    items = given
    if items is None:
        try:
            items = fallback.background(title, topics)
        except fallback.FallbackUnavailable:
            items = None
    if items:
        return [dict(name=m["name"].strip(), reason=str(m.get("reason", "")).strip(), needed_for=resolve(m.get("needed_for")))
                for m in items if str(m.get("name", "")).strip()]
    out = []
    for p in printed or []:
        if re.fullmatch(r"\s*(none|nil|na|n/a|-)?\s*\.?\s*", p, re.I):
            continue
        names, _, _ = split_topics(p)
        for nm in names:
            nm = re.sub(r"^[A-Za-z ]{3,30}:\s*", "", nm).strip()
            if len(nm) > 2:
                out.append(dict(name=nm, reason="Listed as a prerequisite in the syllabus.", needed_for=[]))
    return out[:10]


# ---------------------------------------------------------------- payload
def build_payload(analysis_id, code, title, topics, edges, background):
    import networkx as nx
    b = bundle()
    ids = [t["id"] for t in topics]
    E = [dict(source=ids[i], target=ids[j], confidence=round(p, 3), band=band) for i, j, p, band in edges]
    acc = graph_ops.blocking(E)
    red = {tuple(e) for e in nx.transitive_reduction(nx.DiGraph(acc)).edges()} if acc else set()
    for e in E:
        e["redundant"] = e["band"] == "accepted" and (e["source"], e["target"]) not in red
    order, level = graph_ops.kahn(ids, acc)
    par = graph_ops.parents(acc); by_id = {t["id"]: t for t in topics}
    nodes = [dict(id=t["id"], name=t["name"], unit=t["module"], unit_title=t["module_title"], depth=level[t["id"]],
                  kahn_index=order.index(t["id"]), is_start=not par.get(t["id"])) for t in topics]
    flow = [dict(step=k + 1, id=n, name=by_id[n]["name"], unit=by_id[n]["module"], level=level[n],
                 prerequisites=[by_id[p]["name"] for p in par.get(n, [])], prerequisite_ids=par.get(n, [])) for k, n in enumerate(order)]
    bots = [dict(id=n, name=by_id[n]["name"], unlocks=down, direct=direct) for down, direct, n in graph_ops.bottlenecks(ids, E)]
    return dict(needs_subject=False, analysis_id=analysis_id, course_code=code, course_title=title,
                thresholds=dict(accepted=round(b.threshold, 3), uncertain=UNCERTAIN),
                nodes=nodes, edges=E, kahn_order=order, study_flow=flow, bottlenecks=bots,
                start_nodes=[n for n in order if not par.get(n)], missing_prerequisites=background)


# ---------------------------------------------------------------- storage of analyses (so progress endpoints work after a restart)
def _store(kind):
    p = RUNTIME / kind; p.mkdir(parents=True, exist_ok=True); return p


def save_analysis(payload):
    (_store("analyses") / f"{payload['analysis_id']}.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


_mem: dict = {}
_parsed: dict = {}   # pdf digest -> parsed courses (small FIFO cache)

def load_analysis(analysis_id: str) -> dict:
    if not ID_RE.match(analysis_id or ""):
        raise AnalysisError(400, "invalid analysis_id")
    if analysis_id in _mem:
        return _mem[analysis_id]
    f = _store("analyses") / f"{analysis_id}.json"
    if not f.exists():
        raise AnalysisError(404, "analysis not found; upload the syllabus again")
    _mem[analysis_id] = json.loads(f.read_text(encoding="utf-8"))
    return _mem[analysis_id]


# ---------------------------------------------------------------- entry point
def analyze(content: bytes, subject: str | None) -> dict:
    digest = hashlib.sha256(content).hexdigest()[:12]
    if digest not in _parsed:                       # the subject list and the chosen subject are two requests on the same PDF
        if len(_parsed) >= 32:
            _parsed.pop(next(iter(_parsed)))
        _parsed[digest] = read_pdf(content)
    courses = _parsed[digest]
    usable = [c for c in courses if c["tier"] != "rejected"]
    log.info("parser: %d courses (%d usable)", len(courses), len(usable))
    text = None

    if not courses:
        text = pdf_text(content)
        if len(text.strip()) < 200:
            raise AnalysisError(422, {"error": "not_a_syllabus"})
        try:
            if not subject:
                subs = fallback.list_subjects(text)
                if len(subs) > 1:
                    return dict(needs_subject=True, subjects=subs)
            ex = fallback.extract_topics(text, subject)
        except fallback.FallbackUnavailable as exc:
            log.warning("no course found and fallback unavailable: %s", exc)
            raise AnalysisError(422, {"error": "low_confidence"})
        topics, ctx, meta = topics_from_fallback(ex)
        if len(topics) < 2:
            raise AnalysisError(422, {"error": "low_confidence"})
        return _finish(digest, meta["course_code"], meta["title"], topics, ctx, printed=[], given=ex.get("missing_prerequisites"))

    listable = courses if fallback.available() else usable
    if subject:
        sel = match_subject(courses, subject)
        if sel is None:
            raise AnalysisError(422, {"error": "subject_not_found"})
    elif len(listable) == 1:
        sel = listable[0]
    elif not listable:
        raise AnalysisError(422, {"error": "low_confidence", "reasons": sorted({r for c in courses for r in c["tier_reasons"]})[:6]})
    else:
        return dict(needs_subject=True, subjects=[dict(course_code=c["course_code"], course_title=c["title"]) for c in listable])

    if sel["tier"] != "rejected":
        log.info("course %s: parser topics (%s)", sel["course_code"], sel["tier"])
        topics, ctx = topics_from_parser(sel)
        return _finish(digest, sel["course_code"], sel["title"], topics, ctx, printed=sel.get("prerequisite"))
    try:
        text = text or pdf_text(content)
        ex = fallback.extract_topics(text, f"{sel['course_code']} {sel['title']}")
        topics, ctx, _ = topics_from_fallback(ex, sel["course_code"])
        log.info("course %s: fallback topics (parser rejected: %s)", sel["course_code"], sel["tier_reasons"])
    except fallback.FallbackUnavailable:
        raise AnalysisError(422, {"error": "low_confidence", "reasons": sel["tier_reasons"]})
    if len(topics) < 2:
        raise AnalysisError(422, {"error": "low_confidence"})
    return _finish(digest, sel["course_code"], sel["title"], topics, ctx, printed=sel.get("prerequisite"), given=ex.get("missing_prerequisites"))


def _finish(digest, code, title, topics, ctx, printed, given=None):
    analysis_id = f"{digest}-{re.sub(r'[^A-Za-z0-9]', '', code)[:20] or 'course'}"
    if analysis_id in _mem:
        return _mem[analysis_id]
    edges = edges_for(topics, ctx, title)
    payload = build_payload(analysis_id, code, title, topics, edges, background_for(title, topics, printed, given))
    _mem[analysis_id] = payload; save_analysis(payload)
    return payload
