from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.i18n import starter_avatars, t
from app.models import Avatar, Event
from app.schemas import PAYOFF_PRESETS


def seed_if_empty(db: Session) -> None:
    if settings.database_url.startswith("sqlite"):
        Path("data").mkdir(parents=True, exist_ok=True)
    if db.query(Avatar).count() == 0:
        for item in starter_avatars():
            db.add(
                Avatar(
                    name=item["name"],
                    slug=item["slug"],
                    description=item["description"],
                    color=item["color"],
                    provider="openshift-ai",
                    personality=item["personality"],
                    enabled=True,
                )
            )
        db.commit()
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
