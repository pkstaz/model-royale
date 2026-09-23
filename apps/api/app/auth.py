from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Player


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def issue_player_jwt(player_id: str) -> str:
    payload = {
        "sub": player_id,
        "typ": "player",
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.jwt_hours),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def issue_admin_jwt() -> str:
    payload = {
        "sub": "admin",
        "typ": "admin",
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.jwt_hours),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_token(authorization: str | None) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Falta token")
    token = authorization.split(" ", 1)[1]
    try:
        return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Token inválido") from exc


def require_admin(authorization: str | None = Header(default=None)) -> None:
    payload = decode_token(authorization)
    if payload.get("typ") != "admin":
        raise HTTPException(status_code=403, detail="Se requiere admin")


def require_player(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Player:
    payload = decode_token(authorization)
    if payload.get("typ") != "player":
        raise HTTPException(status_code=403, detail="Se requiere jugador")
    player = db.get(Player, payload["sub"])
    if not player:
        raise HTTPException(status_code=401, detail="Jugador no encontrado")
    return player
