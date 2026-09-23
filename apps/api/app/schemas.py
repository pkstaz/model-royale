from __future__ import annotations

from pydantic import BaseModel, Field


PAYOFF_PRESETS = {
    "royale": {"AA": [-2, -2], "AB": [5, 0], "BA": [0, 5], "BB": [2, 2]},
    "prisoner": {"AA": [1, 1], "AB": [5, 0], "BA": [0, 5], "BB": [3, 3]},
    "chicken": {"AA": [-5, -5], "AB": [2, -1], "BA": [-1, 2], "BB": [1, 1]},
    "stag": {"AA": [1, 1], "AB": [1, 0], "BA": [0, 1], "BB": [4, 4]},
}

DEFAULT_RULES = """Eres un avatar en Model Royale. En cada ronda eliges exactamente una acción: A o B.

La matriz de pagos de este evento se indica más abajo. Responde únicamente con JSON:
{"move": "A" o "B", "rationale": "una frase"}

No uses markdown. No expliques fuera del JSON."""


class AvatarIn(BaseModel):
    name: str
    slug: str | None = None
    description: str = ""
    color: str = "#EE0000"
    provider: str = "openshift-ai"
    base_url: str = ""
    model_id: str = ""
    api_key: str | None = None
    temperature: float = 0.4
    max_tokens: int = 220
    personality: str = ""
    enabled: bool = True


class AvatarOut(BaseModel):
    id: str
    name: str
    slug: str
    description: str
    color: str
    provider: str
    base_url: str
    model_id: str
    has_api_key: bool
    temperature: float
    max_tokens: int
    personality: str
    enabled: bool
    reachable: bool


class EventIn(BaseModel):
    name: str
    code: str | None = None
    format: str = "elimination"
    rounds_per_match: int = Field(default=5, ge=1, le=21)
    max_players: int = Field(default=16, ge=2, le=128)
    min_players: int = Field(default=2, ge=2)
    group_size: int = Field(default=4, ge=2)
    advance_per_group: int = Field(default=2, ge=1)
    reveal_mode: str = "history"
    payoff: dict | None = None
    payoff_preset: str | None = "royale"
    rules_prompt: str | None = None
    judge_avatar_id: str | None = None
    invalid_move_policy: str = "default_a"
    auto_advance: bool = True


class JoinIn(BaseModel):
    code: str
    display_name: str = Field(min_length=2, max_length=32)


class StrategyIn(BaseModel):
    avatar_id: str | None = None
    strategy_prompt: str | None = None


class LoginIn(BaseModel):
    password: str
