"""KDG v2 API.  Run:  uvicorn app.main:app --port 8000   (from the repo root)."""
from __future__ import annotations
import logging, os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.services import pipeline

logging.basicConfig(level=os.environ.get("KDG_LOG_LEVEL", "INFO"), format="%(asctime)s %(name)s %(levelname)s %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        pipeline.warm_up()            # load encoder + model once, never per request
    except Exception as exc:          # the API still starts; edges_for() degrades to its fallbacks
        logging.getLogger("kdg").error("model warm-up failed: %s", exc)
    yield


app = FastAPI(title="KDG API", version="2.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("KDG_CORS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000").split(","),
    allow_methods=["*"], allow_headers=["*"],
)
app.include_router(router, prefix="/api/v1")


@app.get("/healthz")
def healthz():
    return {"status": "ok", "model_loaded": pipeline._bundle is not None}
