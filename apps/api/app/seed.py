from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.connection import DEFAULT_MAAS_BASE_URL, get_app_settings
from app.i18n import CATALOGS, lang, starter_avatars, t
from app.models import Avatar, Event, Player
from app.schemas import PAYOFF_PRESETS

OLD_STARTER_SLUGS = {"granite", "llama", "mistral", "glm", "kimi"}
SEED_EVENT_NAMES = {catalog["seed_event_name"] for catalog in CATALOGS.values()}


def _insert_starters(db: Session) -> None:
    for item in starter_avatars():
        db.add(
            Avatar(
                name=item["name"],
                slug=item["slug"],
                description=item["description"],
                color=item["color"],
                provider="maas",
                model_id=item["model_id"],
                personality=item["personality"],
                use_global_endpoint=True,
                use_global_api_key=True,
                enabled=True,
            )
        )
    db.commit()


def _sync_starter_copy(db: Session) -> None:
    by_slug = {item["slug"]: item for item in starter_avatars()}
    for avatar in db.query(Avatar).all():
        src = by_slug.get(avatar.slug)
        if not src:
            continue
        avatar.description = src["description"]
        avatar.personality = src["personality"]
    event = db.query(Event).filter(Event.code == "TALLER").first()
    if event and event.status in {"draft", "registration"} and event.name in SEED_EVENT_NAMES:
        event.name = t("seed_event_name")
        event.rules_prompt = t("default_rules")
    db.commit()


def seed_if_empty(db: Session) -> None:
    if settings.database_url.startswith("sqlite"):
        Path("data").mkdir(parents=True, exist_ok=True)
    cfg = get_app_settings(db)
    if not cfg.default_base_url:
        cfg.default_base_url = DEFAULT_MAAS_BASE_URL
        db.commit()

    rows = db.query(Avatar).all()
    slugs = {item.slug for item in rows}
    unused = db.query(Player).count() == 0
    if not rows:
        _insert_starters(db)
    elif unused and slugs <= OLD_STARTER_SLUGS:
        for event in db.query(Event).all():
            event.judge_avatar_id = None
        for item in rows:
            db.delete(item)
        db.commit()
        _insert_starters(db)

    if db.query(Event).count() == 0:
        db.add(
            Event(
                name=t("seed_event_name"),
                code="TALLER",
                status="draft",
                format="elimination",
                rounds_per_match=5,
                max_players=16,
                reveal_mode="history",
                payoff_json=json.dumps(PAYOFF_PRESETS["royale"]),
                rules_prompt=t("default_rules"),
            )
        )
        db.commit()

    current_lang = lang()
    if unused and (cfg.seed_lang or "") != current_lang:
        _sync_starter_copy(db)
    if cfg.seed_lang != current_lang:
        cfg.seed_lang = current_lang
        db.commit()
