from __future__ import annotations

import json
import re
import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import issue_admin_jwt, require_admin
from app.database import get_db
from app.engine import publish_snapshot, snapshot
from app.llm import ping_avatar
from app.models import Avatar, Event, Player
from app.schemas import AvatarIn, EventIn, LoginIn, PAYOFF_PRESETS
from app.i18n import t
from app.serialize import avatar_out, event_out
from app.tournament import generate_opening

router = APIRouter(prefix="/api/admin", tags=["admin"])

SLUG_RE = re.compile(r"[^a-z0-9-]+")


def _slugify(value: str) -> str:
    slug = SLUG_RE.sub("-", value.lower()).strip("-")
    return slug or secrets.token_hex(3)


@router.post("/login")
def login(body: LoginIn):
    from app.config import settings

    if body.password != settings.admin_password:
        raise HTTPException(status_code=401, detail=t("bad_admin_password"))
    return {"token": issue_admin_jwt()}


@router.get("/avatars", dependencies=[Depends(require_admin)])
def list_avatars(db: Session = Depends(get_db)):
    rows = db.query(Avatar).order_by(Avatar.name.asc()).all()
    return [avatar_out(item) for item in rows]


@router.post("/avatars", dependencies=[Depends(require_admin)])
def create_avatar(body: AvatarIn, db: Session = Depends(get_db)):
    slug = _slugify(body.slug or body.name)
    if db.query(Avatar).filter(Avatar.slug == slug).first():
        raise HTTPException(status_code=409, detail=t("slug_exists"))
    avatar = Avatar(
        name=body.name,
        slug=slug,
        description=body.description,
        color=body.color,
        provider=body.provider,
        base_url=body.base_url.strip(),
        model_id=body.model_id.strip(),
        api_key=body.api_key or "",
        temperature=body.temperature,
        max_tokens=body.max_tokens,
        personality=body.personality,
        enabled=body.enabled,
    )
    db.add(avatar)
    db.commit()
    db.refresh(avatar)
    return avatar_out(avatar)


@router.patch("/avatars/{avatar_id}", dependencies=[Depends(require_admin)])
def update_avatar(avatar_id: str, body: AvatarIn, db: Session = Depends(get_db)):
    avatar = db.get(Avatar, avatar_id)
    if not avatar:
        raise HTTPException(status_code=404, detail=t("avatar_not_found"))
    avatar.name = body.name
    avatar.slug = _slugify(body.slug or body.name)
    avatar.description = body.description
    avatar.color = body.color
    avatar.provider = body.provider
    avatar.base_url = body.base_url.strip()
    avatar.model_id = body.model_id.strip()
    if body.api_key is not None:
        if body.api_key != "":
            avatar.api_key = body.api_key
        # empty string means "leave unchanged" from the form; send a space to clear
    avatar.temperature = body.temperature
    avatar.max_tokens = body.max_tokens
    avatar.personality = body.personality
    avatar.enabled = body.enabled
    db.commit()
    db.refresh(avatar)
    return avatar_out(avatar)


@router.delete("/avatars/{avatar_id}", dependencies=[Depends(require_admin)])
def delete_avatar(avatar_id: str, db: Session = Depends(get_db)):
    avatar = db.get(Avatar, avatar_id)
    if not avatar:
        raise HTTPException(status_code=404, detail=t("avatar_not_found"))
    in_use = db.query(Player).filter(Player.avatar_id == avatar_id).count()
    if in_use:
        avatar.enabled = False
        db.commit()
        return {"disabled": True}
    db.delete(avatar)
    db.commit()
    return {"ok": True}


@router.post("/avatars/{avatar_id}/ping", dependencies=[Depends(require_admin)])
async def ping(avatar_id: str, db: Session = Depends(get_db)):
    avatar = db.get(Avatar, avatar_id)
    if not avatar:
        raise HTTPException(status_code=404, detail=t("avatar_not_found"))
    return await ping_avatar(avatar)


@router.get("/events", dependencies=[Depends(require_admin)])
def list_events(db: Session = Depends(get_db)):
    rows = db.query(Event).order_by(Event.created_at.desc()).all()
    return [event_out(item) for item in rows]


@router.post("/events", dependencies=[Depends(require_admin)])
def create_event(body: EventIn, db: Session = Depends(get_db)):
    code = (body.code or body.name[:6] or "ROYALE").upper().replace(" ", "")
    code = re.sub(r"[^A-Z0-9]", "", code)[:12] or "ROYALE"
    if db.query(Event).filter(Event.code == code).first():
        code = f"{code}{secrets.token_hex(2).upper()}"[:12]
    payoff = body.payoff or PAYOFF_PRESETS.get(body.payoff_preset or "royale", PAYOFF_PRESETS["royale"])
    event = Event(
        name=body.name,
        code=code,
        format=body.format,
        rounds_per_match=body.rounds_per_match,
        max_players=body.max_players,
        min_players=body.min_players,
        group_size=body.group_size,
        advance_per_group=body.advance_per_group,
        reveal_mode=body.reveal_mode,
        payoff_json=json.dumps(payoff),
        rules_prompt=body.rules_prompt or t("default_rules"),
        judge_avatar_id=body.judge_avatar_id,
        invalid_move_policy=body.invalid_move_policy,
        auto_advance=body.auto_advance,
        status="draft",
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event_out(event)


@router.patch("/events/{event_id}", dependencies=[Depends(require_admin)])
def update_event(event_id: str, body: EventIn, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail=t("event_not_found"))
    if event.status == "running":
        raise HTTPException(status_code=409, detail=t("event_locked"))
    payoff = body.payoff or PAYOFF_PRESETS.get(body.payoff_preset or "royale", PAYOFF_PRESETS["royale"])
    event.name = body.name
    event.format = body.format
    event.rounds_per_match = body.rounds_per_match
    event.max_players = body.max_players
    event.min_players = body.min_players
    event.group_size = body.group_size
    event.advance_per_group = body.advance_per_group
    event.reveal_mode = body.reveal_mode
    event.payoff_json = json.dumps(payoff)
    event.rules_prompt = body.rules_prompt or event.rules_prompt
    event.judge_avatar_id = body.judge_avatar_id
    event.invalid_move_policy = body.invalid_move_policy
    event.auto_advance = body.auto_advance
    db.commit()
    db.refresh(event)
    return event_out(event)


@router.post("/events/{event_id}/open", dependencies=[Depends(require_admin)])
async def open_registration(event_id: str, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail=t("event_not_found"))
    if event.status not in {"draft", "registration"}:
        raise HTTPException(status_code=409, detail=t("cannot_open_reg"))
    event.status = "registration"
    db.commit()
    await publish_snapshot(event.id)
    return event_out(event)


@router.post("/events/{event_id}/start", dependencies=[Depends(require_admin)])
async def start_event(event_id: str, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail=t("event_not_found"))
    players = db.query(Player).filter(Player.event_id == event.id).all()
    if len(players) < event.min_players:
        raise HTTPException(status_code=409, detail=t("not_enough_players"))
    unset = [item for item in players if not item.avatar_id]
    if unset:
        raise HTTPException(status_code=409, detail=t("players_without_avatar"))
    event.status = "running"
    for index, player in enumerate(players, start=1):
        player.seed = index
        player.eliminated = False
    db.commit()
    generate_opening(db, event)
    await publish_snapshot(event.id)
    return event_out(event)


@router.post("/events/{event_id}/reset", dependencies=[Depends(require_admin)])
async def reset_event(event_id: str, db: Session = Depends(get_db)):
    from app.models import Match, Round

    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail=t("event_not_found"))
    matches = db.query(Match).filter(Match.event_id == event.id).all()
    for match in matches:
        db.query(Round).filter(Round.match_id == match.id).delete()
        db.delete(match)
    for player in db.query(Player).filter(Player.event_id == event.id):
        player.eliminated = False
        player.group_label = None
    event.status = "registration"
    db.commit()
    await publish_snapshot(event.id)
    return event_out(event)


@router.get("/events/{event_id}/live", dependencies=[Depends(require_admin)])
def live(event_id: str, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail=t("event_not_found"))
    return snapshot(db, event)
