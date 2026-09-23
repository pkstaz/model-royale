from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Avatar, Event
from app.schemas import DEFAULT_RULES, PAYOFF_PRESETS


STARTER_AVATARS = [
    {
        "name": "Granite",
        "slug": "granite",
        "description": "Avatar Red Hat / IBM Granite. Pega aquí el endpoint de OpenShift AI.",
        "color": "#EE0000",
        "personality": "Eres Granite: directo, sobrio, priorizas consistencia sobre faroleo.",
    },
    {
        "name": "Llama",
        "slug": "llama",
        "description": "Meta Llama servido en el cluster. Completa URL y model id.",
        "color": "#F0AB00",
        "personality": "Eres Llama: exploras, adaptas y no te cascas en una sola táctica.",
    },
    {
        "name": "Mistral",
        "slug": "mistral",
        "description": "Mistral / Mixtral en OpenShift AI.",
        "color": "#73C5C5",
        "personality": "Eres Mistral: compacto, táctico, buscas el pago esperado.",
    },
    {
        "name": "GLM",
        "slug": "glm",
        "description": "GLM. El modelo vive fuera de este juego.",
        "color": "#7CC674",
        "personality": "Eres GLM: analítico, explicas poco y juegas con disciplina.",
    },
    {
        "name": "Kimi",
        "slug": "kimi",
        "description": "Kimi. Configura el predictor cuando exista.",
        "color": "#A18FFF",
        "personality": "Eres Kimi: observas el historial y ajustas ronda a ronda.",
    },
]


def seed_if_empty(db: Session) -> None:
    if settings.database_url.startswith("sqlite"):
        Path("data").mkdir(parents=True, exist_ok=True)
    if db.query(Avatar).count() == 0:
        for item in STARTER_AVATARS:
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
                name="Taller Model Royale",
                code="TALLER",
                status="draft",
                format="elimination",
                rounds_per_match=5,
                max_players=16,
                reveal_mode="history",
                payoff_json=json.dumps(PAYOFF_PRESETS["royale"]),
                rules_prompt=DEFAULT_RULES,
            )
        )
        db.commit()
