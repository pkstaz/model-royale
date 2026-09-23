from __future__ import annotations

from app.llm import complete_chat, extract_json
from app.models import Avatar


async def judge_move(
    raw: str,
    judge: Avatar | None,
    policy: str,
) -> tuple[str, str, bool, str]:
    parsed = extract_json(raw) or {}
    move = str(parsed.get("move", "")).upper().strip()
    rationale = str(parsed.get("rationale") or "")
    notes = ""
    if move in {"A", "B"}:
        return move, rationale, False, notes

    letter = _letter_guess(raw)
    if letter:
        return letter, rationale or raw[:180], False, "parser local"

    if judge:
        try:
            judged = await complete_chat(
                judge,
                [
                    {
                        "role": "system",
                        "content": (
                            "Eres el juez de Model Royale. Extrae la acción A o B. "
                            'Responde JSON {"move":"A"|"B"|null,"notes":"..."}.'
                        ),
                    },
                    {"role": "user", "content": raw[:4000]},
                ],
            )
            payload = extract_json(judged) or {}
            move = str(payload.get("move") or "").upper()
            notes = str(payload.get("notes") or "juez")
            if move in {"A", "B"}:
                return move, rationale or raw[:180], False, notes
        except Exception as exc:  # noqa: BLE001
            notes = f"juez falló: {exc}"

    fallback = "A" if policy != "default_b" else "B"
    if policy == "zero":
        return fallback, rationale or raw[:180], True, notes or "inválida, 0 puntos"
    return fallback, rationale or raw[:180], True, notes or f"inválida, se toma {fallback}"


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
