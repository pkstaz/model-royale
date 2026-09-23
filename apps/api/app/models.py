from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def uid() -> str:
    return uuid.uuid4().hex


class Avatar(Base):
    __tablename__ = "avatars"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(80))
    slug: Mapped[str] = mapped_column(String(80), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    color: Mapped[str] = mapped_column(String(16), default="#EE0000")
    provider: Mapped[str] = mapped_column(String(40), default="openshift-ai")
    base_url: Mapped[str] = mapped_column(String(400), default="")
    model_id: Mapped[str] = mapped_column(String(200), default="")
    api_key: Mapped[str] = mapped_column(String(400), default="")
    temperature: Mapped[float] = mapped_column(Float, default=0.4)
    max_tokens: Mapped[int] = mapped_column(Integer, default=220)
    personality: Mapped[str] = mapped_column(Text, default="")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(120))
    code: Mapped[str] = mapped_column(String(16), unique=True)
    status: Mapped[str] = mapped_column(String(24), default="draft")
    format: Mapped[str] = mapped_column(String(24), default="elimination")
    rounds_per_match: Mapped[int] = mapped_column(Integer, default=5)
    max_players: Mapped[int] = mapped_column(Integer, default=16)
    min_players: Mapped[int] = mapped_column(Integer, default=2)
    group_size: Mapped[int] = mapped_column(Integer, default=4)
    advance_per_group: Mapped[int] = mapped_column(Integer, default=2)
    reveal_mode: Mapped[str] = mapped_column(String(24), default="history")
    payoff_json: Mapped[str] = mapped_column(Text, default="")
    rules_prompt: Mapped[str] = mapped_column(Text, default="")
    judge_avatar_id: Mapped[str | None] = mapped_column(String(32), ForeignKey("avatars.id"), nullable=True)
    invalid_move_policy: Mapped[str] = mapped_column(String(24), default="default_a")
    auto_advance: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    players: Mapped[list[Player]] = relationship(back_populates="event")
    matches: Mapped[list[Match]] = relationship(back_populates="event")


class Player(Base):
    __tablename__ = "players"
    __table_args__ = (UniqueConstraint("event_id", "display_name"),)

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    event_id: Mapped[str] = mapped_column(ForeignKey("events.id"))
    display_name: Mapped[str] = mapped_column(String(80))
    avatar_id: Mapped[str | None] = mapped_column(ForeignKey("avatars.id"), nullable=True)
    strategy_prompt: Mapped[str] = mapped_column(Text, default="")
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    password_hash: Mapped[str] = mapped_column(String(64), default="")
    seed: Mapped[int] = mapped_column(Integer, default=0)
    group_label: Mapped[str | None] = mapped_column(String(8), nullable=True)
    eliminated: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    event: Mapped[Event] = relationship(back_populates="players")
    avatar: Mapped[Avatar | None] = relationship()


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    event_id: Mapped[str] = mapped_column(ForeignKey("events.id"))
    stage: Mapped[str] = mapped_column(String(32), default="league")
    wave: Mapped[int] = mapped_column(Integer, default=0)
    group_label: Mapped[str | None] = mapped_column(String(8), nullable=True)
    bracket_slot: Mapped[int] = mapped_column(Integer, default=0)
    player_a_id: Mapped[str | None] = mapped_column(ForeignKey("players.id"), nullable=True)
    player_b_id: Mapped[str | None] = mapped_column(ForeignKey("players.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="pending")
    winner_id: Mapped[str | None] = mapped_column(ForeignKey("players.id"), nullable=True)
    score_a: Mapped[int] = mapped_column(Integer, default=0)
    score_b: Mapped[int] = mapped_column(Integer, default=0)
    first_mover: Mapped[str] = mapped_column(String(8), default="a")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    event: Mapped[Event] = relationship(back_populates="matches")
    rounds: Mapped[list[Round]] = relationship(back_populates="match", order_by="Round.index")


class Round(Base):
    __tablename__ = "rounds"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    match_id: Mapped[str] = mapped_column(ForeignKey("matches.id"))
    index: Mapped[int] = mapped_column(Integer)
    move_a: Mapped[str] = mapped_column(String(4), default="")
    move_b: Mapped[str] = mapped_column(String(4), default="")
    points_a: Mapped[int] = mapped_column(Integer, default=0)
    points_b: Mapped[int] = mapped_column(Integer, default=0)
    raw_a: Mapped[str] = mapped_column(Text, default="")
    raw_b: Mapped[str] = mapped_column(Text, default="")
    rationale_a: Mapped[str] = mapped_column(Text, default="")
    rationale_b: Mapped[str] = mapped_column(Text, default="")
    judge_notes: Mapped[str] = mapped_column(Text, default="")
    invalid_a: Mapped[bool] = mapped_column(Boolean, default=False)
    invalid_b: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    match: Mapped[Match] = relationship(back_populates="rounds")
