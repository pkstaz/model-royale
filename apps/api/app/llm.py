from __future__ import annotations

import hashlib
import json
import re

import httpx

from app.config import settings
from app.i18n import t
from app.models import Avatar


JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def mock_move(strategy: str, history: list[dict], name: str) -> dict:
    text = (strategy or "").lower()
    last_opp = history[-1]["opp"] if history else None
    if any(token in text for token in ("siempre a", "always a", "sempre a", "siempre defect", "hawk", "halcón")):
        move = "A"
        rationale = t("mock_fixed_a")
    elif any(token in text for token in ("siempre b", "always b", "sempre b", "siempre coop", "dove", "paloma")):
        move = "B"
        rationale = t("mock_fixed_b")
    elif any(token in text for token in ("tit", "talión", "ojo por ojo", "tit-for-tat")):
        move = last_opp or "B"
        rationale = t("mock_tft")
    elif any(token in text for token in ("grim", "gatillo", "nunca perdono")):
        move = "A" if any(item["opp"] == "A" for item in history) else "B"
        rationale = t("mock_grim")
    elif any(token in text for token in ("perdón", "perdon", "generos")):
        if last_opp == "A" and len(history) >= 2 and history[-2]["opp"] == "A":
            move = "A"
        else:
            move = "B"
        rationale = t("mock_forgive")
    else:
        digest = hashlib.sha256(f"{name}:{len(history)}:{text}".encode()).hexdigest()
        move = "A" if int(digest[:2], 16) % 3 == 0 else "B"
        rationale = t("mock_mix")
    return {"move": move, "rationale": rationale}


async def complete_chat(avatar: Avatar, messages: list[dict]) -> str:
    if settings.mock_inference or not avatar.base_url or not avatar.model_id:
        user = next((item["content"] for item in reversed(messages) if item["role"] == "user"), "")
        strategy = next((item["content"] for item in messages if item["role"] == "system"), "")
        history: list[dict] = []
        if "opp=" in user:
            history = [{"opp": "A" if "opp=A" in user else "B"}]
        mocked = mock_move(strategy + "\n" + user, history, avatar.name)
        return json.dumps(mocked)

    url = avatar.base_url.rstrip("/")
    if not url.endswith("/chat/completions"):
        url = url + "/chat/completions"
    headers = {"Content-Type": "application/json"}
    if avatar.api_key:
        headers["Authorization"] = f"Bearer {avatar.api_key}"
    payload = {
        "model": avatar.model_id,
        "temperature": avatar.temperature,
        "max_tokens": avatar.max_tokens,
        "messages": messages,
    }
    async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
    return data["choices"][0]["message"]["content"]


def extract_json(text: str) -> dict | None:
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = JSON_RE.search(text)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None


async def ping_avatar(avatar: Avatar) -> dict:
    if not avatar.base_url or not avatar.model_id:
        return {"ok": False, "detail": t("ping_no_endpoint")}
    try:
        content = await complete_chat(
            avatar,
            [
                {"role": "system", "content": t("ping_system")},
                {"role": "user", "content": "ping"},
            ],
        )
        return {"ok": True, "detail": content[:240]}
    except Exception as exc:  # noqa: BLE001 — surface any provider error to the admin
        return {"ok": False, "detail": str(exc)}
