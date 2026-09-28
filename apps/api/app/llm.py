from __future__ import annotations

import hashlib
import json
import re
import time
from collections.abc import Awaitable, Callable

import httpx

from app.config import settings
from app.connection import load_connection, normalize_openai_base
from app.i18n import t
from app.models import Avatar

JSON_RE = re.compile(r"\{.*\}", re.DOTALL)
MOVE_MAX_TOKENS = 96
DeltaFn = Callable[[str], Awaitable[None]]

_client: httpx.AsyncClient | None = None


def http_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            timeout=httpx.Timeout(settings.llm_timeout_seconds, connect=8.0),
            follow_redirects=True,
        )
    return _client


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


def _piece_text(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(_piece_text(item) for item in value)
    if isinstance(value, dict):
        return str(value.get("text") or value.get("content") or "")
    return ""


def _delta_text(delta: dict) -> str:
    parts = []
    for key in ("reasoning_content", "reasoning", "content"):
        piece = _piece_text(delta.get(key))
        if piece:
            parts.append(piece)
    return "".join(parts)


def _message_text(message: dict) -> str:
    if not message:
        return ""
    direct = _delta_text(message)
    if direct:
        return direct
    return _piece_text(message.get("content"))


async def complete_chat(
    avatar: Avatar,
    messages: list[dict],
    temperature: float | None = None,
    on_delta: DeltaFn | None = None,
    max_tokens: int | None = None,
) -> str:
    base_url, api_key = load_connection(avatar)
    if settings.mock_inference or not base_url or not avatar.model_id:
        user = next((item["content"] for item in reversed(messages) if item["role"] == "user"), "")
        strategy = next((item["content"] for item in messages if item["role"] == "system"), "")
        history: list[dict] = []
        if "opp=" in user:
            history = [{"opp": "A" if "opp=A" in user else "B"}]
        mocked = mock_move(strategy + "\n" + user, history, avatar.name)
        text = json.dumps(mocked)
        if on_delta:
            await on_delta(text)
        return text

    url = normalize_openai_base(base_url)
    if not url.endswith("/chat/completions"):
        url = url + "/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    token_cap = MOVE_MAX_TOKENS if max_tokens is None else max_tokens
    payload = {
        "model": avatar.model_id,
        "temperature": avatar.temperature if temperature is None else temperature,
        "max_tokens": token_cap,
        "messages": messages,
        "stream": True,
    }
    started = time.monotonic()
    try:
        text = await _stream_chat(url, headers, payload, on_delta)
    except Exception as exc:
        print(f"llm stream fail {avatar.name} {avatar.model_id}: {exc}; fallback")
        payload.pop("stream", None)
        text = await _once_chat(url, headers, payload)
        if on_delta and text:
            await on_delta(text)
    elapsed = time.monotonic() - started
    print(f"llm {avatar.name} {avatar.model_id} {elapsed:.2f}s chars={len(text)}")
    return text or ""


async def _stream_chat(url: str, headers: dict, payload: dict, on_delta: DeltaFn | None) -> str:
    pieces: list[str] = []
    async with http_client().stream("POST", url, headers=headers, json=payload) as response:
        response.raise_for_status()
        async for line in response.aiter_lines():
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if not data or data == "[DONE]":
                if data == "[DONE]":
                    break
                continue
            try:
                chunk = json.loads(data)
            except json.JSONDecodeError:
                continue
            choices = chunk.get("choices") or []
            if not choices:
                continue
            delta = choices[0].get("delta") or choices[0].get("message") or {}
            piece = _delta_text(delta)
            if not piece:
                continue
            pieces.append(piece)
            if on_delta:
                await on_delta("".join(pieces))
    return "".join(pieces)


async def _once_chat(url: str, headers: dict, payload: dict) -> str:
    response = await http_client().post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    message = ((data.get("choices") or [{}])[0]).get("message") or {}
    return _message_text(message)


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
    base_url, _api_key = load_connection(avatar)
    if not base_url or not avatar.model_id:
        return {"ok": False, "detail": t("ping_no_endpoint")}
    try:
        content = await complete_chat(
            avatar,
            [
                {"role": "system", "content": t("ping_system")},
                {"role": "user", "content": "ping"},
            ],
            max_tokens=32,
        )
        return {"ok": True, "detail": (content or "")[:240]}
    except Exception as exc:  # noqa: BLE001 — surface any provider error to the admin
        return {"ok": False, "detail": str(exc)}
