"""Fallback language service (Gemini), used ONLY where the parser or the edge model fails.

Where it is called (app/services/pipeline.py):
  1. no course could be read by the parser            -> list_subjects / extract_topics
  2. the selected course was rejected by the parser   -> extract_topics
  3. the edge model raised or produced no edges       -> prerequisite_edges
  4. background knowledge the syllabus assumes        -> background (otherwise the printed 'Prerequisite' row is used)

Rules: the key is read from the GEMINI_API_KEY environment variable (or a git-ignored .env); without a key every function
raises FallbackUnavailable and the caller degrades silently. The API response never says which component produced a
result; the source is written to the server log only."""
from __future__ import annotations
import json, logging, os, pathlib, time
import httpx

log = logging.getLogger("kdg.fallback")
ENV_PATH = pathlib.Path(__file__).resolve().parents[2] / ".env"
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
MODELS = ["gemini-2.5-flash", "gemini-flash-latest"]
MAX_TEXT = 600_000


class FallbackUnavailable(Exception):
    """No key, network error, or unusable response."""


def _key() -> str:
    k = os.environ.get("GEMINI_API_KEY", "").strip()
    if not k and ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            if line.startswith("GEMINI_API_KEY="):
                k = line.split("=", 1)[1].strip().strip("'\"")
    if not k:
        raise FallbackUnavailable("no key")
    return k


def available() -> bool:
    try:
        _key(); return True
    except FallbackUnavailable:
        return False


def _call(prompt: str, schema: dict) -> dict:
    key = _key()
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json", "responseSchema": schema}}
    last = "unknown"
    for model in MODELS:
        for attempt in range(3):
            try:
                r = httpx.post(API_URL.format(model=model), params={"key": key}, json=body, timeout=180)
            except httpx.HTTPError as exc:
                last = type(exc).__name__; time.sleep(2 * (attempt + 1)); continue
            if r.status_code == 200:
                try:
                    return json.loads(r.json()["candidates"][0]["content"]["parts"][0]["text"])
                except (KeyError, IndexError, ValueError):
                    last = "unreadable response"; break
            last = f"HTTP {r.status_code}"
            if r.status_code in (429, 500, 503):
                time.sleep(3 * (attempt + 1)); continue
            break
    raise FallbackUnavailable(last)


S, A, O, I = {"type": "STRING"}, "ARRAY", "OBJECT", {"type": "INTEGER"}
_SUBJECTS = {"type": O, "properties": {"subjects": {"type": A, "items": {"type": O, "properties": {"course_code": S, "course_title": S},
                                                                          "required": ["course_code", "course_title"]}}}, "required": ["subjects"]}
_BACKGROUND = {"type": A, "items": {"type": O, "properties": {"name": S, "reason": S, "needed_for": {"type": A, "items": S}},
                                     "required": ["name", "reason", "needed_for"]}}
_TOPICS = {"type": O, "properties": {
    "course_title": S, "course_code": S,
    "topics": {"type": A, "items": {"type": O, "properties": {"name": S, "unit_number": I, "unit_title": S}, "required": ["name", "unit_number", "unit_title"]}},
    "missing_prerequisites": _BACKGROUND}, "required": ["course_title", "course_code", "topics", "missing_prerequisites"]}
_EDGES = {"type": O, "properties": {"edges": {"type": A, "items": {"type": O, "properties": {"before": I, "after": I}, "required": ["before", "after"]}}},
          "required": ["edges"]}
_BG_ONLY = {"type": O, "properties": {"missing_prerequisites": _BACKGROUND}, "required": ["missing_prerequisites"]}


def list_subjects(text: str) -> list[dict]:
    p = ("The text below is a university syllabus document. List every distinct subject that has its own syllabus content "
         "(course code and title). Ignore lab, practical, mini-project, workshop and capstone subjects. Do not invent subjects.\n\n"
         f"SYLLABUS TEXT:\n{text[:MAX_TEXT]}")
    out = _call(p, _SUBJECTS).get("subjects", [])
    log.info("fallback used: list_subjects (%d)", len(out))
    return out


def extract_topics(text: str, subject: str | None) -> dict:
    focus = f"Analyse ONLY the subject '{subject}'. Ignore every other subject.\n" if subject else "The text is one subject's syllabus.\n"
    p = ("You are building a prerequisite map from a university syllabus.\n" + focus +
         "1. topics: the teachable topics in syllabus order; each a short concept (2-6 words); split comma lists; 20-45 topics; "
         "unit_number follows the syllabus modules starting at 1. Exclude exam schemes, marks, hours, outcomes, references, books, labs.\n"
         "2. missing_prerequisites: 3-8 foundational concepts the student must already know but the syllabus does NOT teach; "
         "one-sentence reason; needed_for = exact topic names from your list.\n"
         "3. course_title and course_code as printed (empty string if absent).\n\n"
         f"SYLLABUS TEXT:\n{text[:MAX_TEXT]}")
    out = _call(p, _TOPICS)
    log.info("fallback used: extract_topics (%d topics)", len(out.get("topics", [])))
    return out


def background(title: str, topics: list[dict]) -> list[dict]:
    names = "\n".join(f"- {t['name']}" for t in topics)
    p = (f"Course: {title}\nTopics taught (in order):\n{names}\n\n"
         "List 3-8 foundational concepts a student must already know to follow this course but that the list above does NOT teach. "
         "For each give a one-sentence reason and needed_for = exact topic names copied from the list.")
    out = _call(p, _BG_ONLY).get("missing_prerequisites", [])
    log.info("fallback used: background (%d)", len(out))
    return out


def prerequisite_edges(title: str, topics: list[dict]) -> list[tuple[int, int]]:
    """Directed edges (before -> after) between topic indices. Prerequisites are one-way: A must be learned before B."""
    listing = "\n".join(f"{i}. [module {t['module']}] {t['name']}" for i, t in enumerate(topics))
    p = (f"Course: {title}\nTopics (index. [module] name):\n{listing}\n\n"
         "Return the direct prerequisite edges inside this course: before -> after means a student must understand topic 'before' "
         "to learn topic 'after'. Only clear, direct dependencies; no cycles; at most 3 prerequisites per topic. Use the indices.")
    raw = _call(p, _EDGES).get("edges", [])
    n = len(topics)
    out = [(int(e["before"]), int(e["after"])) for e in raw
           if 0 <= int(e["before"]) < n and 0 <= int(e["after"]) < n and int(e["before"]) != int(e["after"])]
    log.info("fallback used: prerequisite_edges (%d)", len(out))
    return out
