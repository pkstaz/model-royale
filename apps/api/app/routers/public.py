from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.engine import snapshot
from app.hub import hub
from app.i18n import lang, t
from app.models import Avatar, Event
from app.serialize import avatar_out, event_out

router = APIRouter(prefix="/api/public", tags=["public"])


@router.get("/config")
def public_config():
    return {"lang": lang()}


@router.get("/events/{code}")
def get_event(code: str, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.code == code.upper()).first()
    if not event:
        raise HTTPException(status_code=404, detail=t("event_not_found"))
    avatars = db.query(Avatar).filter(Avatar.enabled.is_(True)).order_by(Avatar.name.asc()).all()
    return {
        "event": event_out(event),
        "avatars": [avatar_out(item, public=True) for item in avatars],
        "live": snapshot(db, event),
    }


@router.get("/events/{code}/stream")
async def stream(code: str, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.code == code.upper()).first()
    if not event:
        raise HTTPException(status_code=404, detail=t("event_not_found"))
    event_id = event.id
    initial = snapshot(db, event)

    async def gen():
        queue = hub.subscribe(event_id)
        try:
            yield f"data: {json.dumps(initial, default=str)}\n\n"
            while True:
                body = await queue.get()
                yield f"data: {body}\n\n"
        finally:
            hub.unsubscribe(event_id, queue)

    return StreamingResponse(gen(), media_type="text/event-stream")
