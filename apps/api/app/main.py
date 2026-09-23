from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.engine import engine_loop
from app.routers import admin, play, public
from app.seed import seed_if_empty


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.database_url.startswith("sqlite"):
        Path("data").mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
        from app.models import Match

        interrupted = db.query(Match).filter(Match.status == "running").all()
        for match in interrupted:
            match.status = "pending"
        db.commit()
    finally:
        db.close()
    task = asyncio.create_task(engine_loop())
    yield
    task.cancel()


app = FastAPI(title="Model Royale", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins or ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(admin.router)
app.include_router(play.router)
app.include_router(public.router)


@app.get("/healthz")
def healthz():
    return {"ok": True, "service": "model-royale"}
