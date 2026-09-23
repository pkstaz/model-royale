from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import hash_password, hash_token, issue_player_jwt, require_player, verify_password
from app.database import get_db
from app.engine import publish_snapshot, snapshot
from app.models import Avatar, Event, Player
from app.schemas import JoinIn, PlayerLoginIn, StrategyIn
from app.serialize import event_out, player_out
from app.standings import player_is_locked

router = APIRouter(prefix="/api/play", tags=["play"])


def _session(db: Session, player: Player, event: Event) -> dict:
    return {
        "token": issue_player_jwt(player.id),
        "player": player_out(player, locked=player_is_locked(db, player.id)),
        "event": event_out(event),
    }


@router.post("/join")
async def join(body: JoinIn, db: Session = Depends(get_db)):
    code = body.code.strip().upper()
    event = db.query(Event).filter(Event.code == code).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    if event.status != "registration":
        raise HTTPException(
            status_code=409,
            detail="La inscripción no está abierta. Si ya te inscribiste, usá Entrar.",
        )
    count = db.query(Player).filter(Player.event_id == event.id).count()
    if count >= event.max_players:
        raise HTTPException(status_code=409, detail="Cupo completo")
    name = body.display_name.strip()
    existing = (
        db.query(Player).filter(Player.event_id == event.id, Player.display_name == name).first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Ese nombre ya está inscrito. Entrá con tu clave.")
    token = secrets.token_urlsafe(24)
    player = Player(
        event_id=event.id,
        display_name=name,
        token_hash=hash_token(token),
        password_hash=hash_password(body.password),
        seed=count + 1,
    )
    db.add(player)
    db.commit()
    db.refresh(player)
    await publish_snapshot(event.id)
    return _session(db, player, event)


@router.post("/login")
def login(body: PlayerLoginIn, db: Session = Depends(get_db)):
    code = body.code.strip().upper()
    event = db.query(Event).filter(Event.code == code).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    name = body.display_name.strip()
    player = (
        db.query(Player).filter(Player.event_id == event.id, Player.display_name == name).first()
    )
    if not player:
        raise HTTPException(status_code=404, detail="No hay una inscripción con ese nombre")
    if not player.password_hash:
        raise HTTPException(
            status_code=401,
            detail="Esta cuenta no tiene clave. Inscribite de nuevo o pedile un reset al admin.",
        )
    if not verify_password(body.password, player.password_hash):
        raise HTTPException(status_code=401, detail="Clave incorrecta")
    return _session(db, player, event)


@router.get("/me")
def me(player: Player = Depends(require_player), db: Session = Depends(get_db)):
    event = db.get(Event, player.event_id)
    avatars = db.query(Avatar).filter(Avatar.enabled.is_(True)).order_by(Avatar.name.asc()).all()
    live = snapshot(db, event) if event else None
    mine = []
    if live:
        mine = [
            item
            for item in live["matches"]
            if item.get("player_a_id") == player.id or item.get("player_b_id") == player.id
        ]
    standing = None
    if live:
        standing = next((row for row in live["standings"] if row["player_id"] == player.id), None)
    return {
        "player": player_out(player, locked=player_is_locked(db, player.id)),
        "event": event_out(event) if event else None,
        "history": mine,
        "standing": standing,
        "avatars": [
            {
                "id": item.id,
                "name": item.name,
                "slug": item.slug,
                "description": item.description,
                "color": item.color,
                "personality": item.personality,
                "reachable": bool(item.base_url and item.model_id),
            }
            for item in avatars
        ],
    }


@router.patch("/me")
async def update_me(
    body: StrategyIn,
    player: Player = Depends(require_player),
    db: Session = Depends(get_db),
):
    if player_is_locked(db, player.id):
        raise HTTPException(
            status_code=409,
            detail="Tu avatar está en combate. Podrás editar cuando termine.",
        )
    if body.avatar_id is not None:
        avatar = db.get(Avatar, body.avatar_id)
        if not avatar or not avatar.enabled:
            raise HTTPException(status_code=404, detail="Avatar no disponible")
        player.avatar_id = avatar.id
    if body.strategy_prompt is not None:
        player.strategy_prompt = body.strategy_prompt[:8000]
    db.commit()
    db.refresh(player)
    await publish_snapshot(player.event_id)
    return player_out(player, locked=False)
