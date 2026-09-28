from __future__ import annotations

from app.i18n import t
from app.llm import complete_chat, extract_json
from app.models import Avatar


async def judge_move(
    raw: str,
    judge: Avatar | None,
    policy: str,
) -> tuple[str, str, bool, str]:
    parsed = extract_json(raw or "") or {}
    move = str(parsed.get("move", "")).upper().strip()
    rationale = str(parsed.get("rationale") or "")
    notes = ""
    snippet = (raw or "")[:180]
    if move in {"A", "B"}:
        return move, rationale, False, notes

    letter = _letter_guess(raw or "")
    if letter:
        return letter, rationale or snippet, False, t("judge_local")

    if judge:
        try:
            judged = await complete_chat(
                judge,
                [
                    {
                        "role": "system",
                        "content": t("judge_system"),
                    },
                    {"role": "user", "content": (raw or "")[:4000]},
                ],
                max_tokens=64,
            )
            payload = extract_json(judged or "") or {}
            move = str(payload.get("move") or "").upper()
            notes = str(payload.get("notes") or t("judge_notes"))
            if move in {"A", "B"}:
                return move, rationale or snippet, False, notes
        except Exception as exc:  # noqa: BLE001
            notes = t("judge_failed", exc=exc)

    fallback = "A" if policy != "default_b" else "B"
    if policy == "zero":
        return fallback, rationale or snippet, True, notes or t("invalid_zero")
    return fallback, rationale or snippet, True, notes or t("invalid_fallback", move=fallback)


def _letter_guess(raw: str) -> str | None:
    text = (raw or "").upper()
    if "MOVE" in text and '"A"' in text:
        return "A"
    if "MOVE" in text and '"B"' in text:
        return "B"
    isolated = [token for token in text.replace(".", " ").split() if token in {"A", "B"}]
    if isolated:
        return isolated[-1]
    return None
