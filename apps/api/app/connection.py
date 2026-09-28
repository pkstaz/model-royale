from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import AppSettings, Avatar

DEFAULT_MAAS_BASE_URL = "https://maas-rhdp.apps.maas.redhatworkshops.io/v1/models"


@dataclass(frozen=True)
class InferenceConfig:
    default_base_url: str
    default_api_key: str


def normalize_openai_base(url: str) -> str:
    """Strip listing or chat suffixes so callers can append /chat/completions."""
    cleaned = (url or "").strip().rstrip("/")
    if cleaned.endswith("/chat/completions"):
        cleaned = cleaned[: -len("/chat/completions")].rstrip("/")
    if cleaned.endswith("/models"):
        cleaned = cleaned[: -len("/models")].rstrip("/")
    return cleaned


def get_app_settings(db: Session) -> AppSettings:
    row = db.get(AppSettings, "default")
    if row:
        if not row.default_base_url:
            row.default_base_url = DEFAULT_MAAS_BASE_URL
            db.commit()
            db.refresh(row)
        return row
    row = AppSettings(id="default", default_base_url=DEFAULT_MAAS_BASE_URL, default_api_key="")
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def inference_config(db: Session) -> InferenceConfig:
    row = get_app_settings(db)
    return InferenceConfig(
        default_base_url=(row.default_base_url or DEFAULT_MAAS_BASE_URL).strip(),
        default_api_key=row.default_api_key or "",
    )


def resolved_base_url(avatar: Avatar, cfg: InferenceConfig) -> str:
    if avatar.use_global_endpoint is False:
        return (avatar.base_url or "").strip()
    return cfg.default_base_url


def resolved_api_key(avatar: Avatar, cfg: InferenceConfig) -> str:
    if avatar.use_global_api_key is False:
        return avatar.api_key or ""
    return cfg.default_api_key


def load_connection(avatar: Avatar) -> tuple[str, str]:
    db = SessionLocal()
    try:
        cfg = inference_config(db)
        return resolved_base_url(avatar, cfg), resolved_api_key(avatar, cfg)
    finally:
        db.close()
