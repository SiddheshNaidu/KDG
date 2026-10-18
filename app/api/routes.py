"""All HTTP endpoints (prefix /api/v1). Thin layer: validation + error mapping; logic lives in app/services."""
from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from app.services import pipeline, progress
from app.services.pipeline import AnalysisError

router = APIRouter()
MAX_BYTES = 30 * 1024 * 1024


def _call(fn, *a, **k):
    try:
        return fn(*a, **k)
    except AnalysisError as e:
        raise HTTPException(status_code=e.status, detail=e.detail)


async def _analyze(file: UploadFile, subject: Optional[str]):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")
    content = await file.read()
    if len(content) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="PDF is larger than 30 MB.")
    if not content.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="This file is not a readable PDF.")
    try:
        return await run_in_threadpool(pipeline.analyze, content, subject)
    except AnalysisError as e:
        raise HTTPException(status_code=e.status, detail=e.detail)


@router.post("/analyze", tags=["analysis"])
async def analyze(file: UploadFile = File(...), subject: Optional[str] = Form(default=None)):
    """Upload a syllabus PDF. Several courses and no subject -> {needs_subject, subjects}; otherwise the course graph."""
    return await _analyze(file, subject)


# Existing frontend pages (landing + study planner) post here; same handler, same payload.
@router.post("/gemini/analyze", tags=["analysis"], include_in_schema=False)
async def analyze_alias(file: UploadFile = File(...), subject: Optional[str] = Form(default=None)):
    return await _analyze(file, subject)


@router.get("/analysis/{analysis_id}", tags=["analysis"])
def get_analysis(analysis_id: str):
    return _call(pipeline.load_analysis, analysis_id)


class StatusReq(BaseModel):
    analysis_id: str
    mastered: List[str] = Field(default_factory=list)
    target_id: Optional[str] = None


@router.post("/progress/status", tags=["progress"])
def progress_status(req: StatusReq):
    """Node states (mastered / ready / blocked), start nodes, next topic; optional missing prerequisites of target_id."""
    return _call(progress.status, req.analysis_id, req.mastered, req.target_id)


class MissingReq(BaseModel):
    analysis_id: str
    target_concept_id: str
    known_concept_ids: List[str] = Field(default_factory=list)


@router.post("/analytics/missing-prerequisites", tags=["progress"])
def missing_prerequisites(req: MissingReq):
    """Ancestors(target) minus known, in Kahn order, with the percentage already known."""
    return _call(progress.missing, req.analysis_id, req.target_concept_id, req.known_concept_ids)


class MasteryReq(BaseModel):
    user_id: str
    analysis_id: str
    topic_id: str
    mastered: bool = True
    force: bool = False


@router.post("/progress/mastery", tags=["progress"])
def set_mastery(req: MasteryReq):
    """Mark / unmark a topic. Blocked topic -> 409 with the missing list unless force=true. Saved per user and analysis."""
    return _call(progress.set_mastery, req.user_id, req.analysis_id, req.topic_id, req.mastered, req.force)


@router.get("/progress/{user_id}/{analysis_id}", tags=["progress"])
def get_progress(user_id: str, analysis_id: str):
    """Saved mastery + current node states (call after loading an analysis to restore a returning learner)."""
    return _call(lambda: progress.status(analysis_id, progress.saved(user_id, analysis_id)))
