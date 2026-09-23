from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.i18n import t
from app.models import Player


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def hash_password(password: str) -> str:
    return hashlib.sha256(f"model-royale:{password}".encode()).hexdigest()


def verify_password(password: str, stored: str) -> bool:
    if not stored:
        return False
    return hmac.compare_digest(hash_password(password), stored)


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
        raise HTTPException(status_code=401, detail=t("missing_token"))
    token = authorization.split(" ", 1)[1]
    try:
        return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail=t("invalid_token")) from exc


def require_admin(authorization: str | None = Header(default=None)) -> None:
    payload = decode_token(authorization)
    if payload.get("typ") != "admin":
        raise HTTPException(status_code=403, detail=t("admin_required"))


def require_player(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Player:
    payload = decode_token(authorization)
    if payload.get("typ") != "player":
        raise HTTPException(status_code=403, detail=t("player_required"))
    player = db.get(Player, payload["sub"])
    if not player:
        raise HTTPException(status_code=401, detail=t("player_not_found"))
    return player
