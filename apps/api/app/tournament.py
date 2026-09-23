from __future__ import annotations

import json
import math
import random

from sqlalchemy.orm import Session

from app.models import Event, Match, Player
from app.standings import standings_for_event


def next_power_of_two(value: int) -> int:
    if value <= 1:
        return 1
    return 2 ** math.ceil(math.log2(value))


def generate_opening(db: Session, event: Event) -> None:
    players = (
        db.query(Player)
        .filter(Player.event_id == event.id)
        .order_by(Player.seed.asc(), Player.created_at.asc())
        .all()
    )
    if event.format == "round_robin":
        _round_robin(db, event, players, stage="league", group=None, wave=0)
    elif event.format == "groups":
        _assign_groups(event, players)
        grouped: dict[str, list[Player]] = {}
        for player in players:
            grouped.setdefault(player.group_label or "A", []).append(player)
        for label, group in grouped.items():
            _round_robin(db, event, group, stage="groups", group=label, wave=0)
    else:
        _elimination_round(db, event, players, wave=0)
    db.commit()


def maybe_advance(db: Session, event: Event) -> None:
    open_matches = (
        db.query(Match)
        .filter(Match.event_id == event.id, Match.status.in_(["pending", "running"]))
        .count()
    )
    if open_matches:
        return
    if event.format == "round_robin":
        event.status = "completed"
        db.commit()
        return
    if event.format == "groups":
        elim_exists = (
            db.query(Match).filter(Match.event_id == event.id, Match.stage == "elimination").count()
        )
        if not elim_exists:
            advancers = _group_advancers(db, event)
            advancer_ids = {item.id for item in advancers}
            for player in db.query(Player).filter(Player.event_id == event.id):
                if player.id not in advancer_ids:
                    player.eliminated = True
            _elimination_round(db, event, advancers, wave=0)
            db.commit()
            return
        _advance_elimination(db, event)
        return
    _advance_elimination(db, event)


def _advance_elimination(db: Session, event: Event) -> None:
    elim = db.query(Match).filter(Match.event_id == event.id, Match.stage == "elimination").all()
    if not elim:
        event.status = "completed"
        db.commit()
        return
    wave = max(item.wave for item in elim)
    current = [item for item in elim if item.wave == wave]
    if any(item.status in {"pending", "running"} for item in current):
        return
    winners: list[Player] = []
    played_ids: set[str] = set()
    for match in current:
        if match.player_a_id:
            played_ids.add(match.player_a_id)
        if match.player_b_id:
            played_ids.add(match.player_b_id)
        if match.winner_id:
            player = db.get(Player, match.winner_id)
            if player:
                winners.append(player)
    for player in db.query(Player).filter(Player.event_id == event.id):
        if player.id in played_ids and player.id not in {item.id for item in winners}:
            player.eliminated = True
    if len(winners) <= 1:
        event.status = "completed"
        db.commit()
        return
    _elimination_round(db, event, winners, wave=wave + 1)
    db.commit()


def _assign_groups(event: Event, players: list[Player]) -> None:
    shuffled = players[:]
    random.shuffle(shuffled)
    size = max(2, event.group_size)
    for index, player in enumerate(shuffled):
        player.group_label = chr(ord("A") + (index // size))


def _round_robin(
    db: Session,
    event: Event,
    players: list[Player],
    stage: str,
    group: str | None,
    wave: int,
) -> None:
    slot = 0
    for i, left in enumerate(players):
        for right in players[i + 1 :]:
            db.add(
                Match(
                    event_id=event.id,
                    stage=stage,
                    wave=wave,
                    group_label=group,
                    bracket_slot=slot,
                    player_a_id=left.id,
                    player_b_id=right.id,
                    status="pending",
                )
            )
            slot += 1


def _elimination_round(db: Session, event: Event, players: list[Player], wave: int) -> None:
    ordered = list(players)
    target = next_power_of_two(len(ordered)) if ordered else 1
    byes_needed = target - len(ordered)
    slot = 0
    queue = ordered[:]
    while queue:
        left = queue.pop(0)
        if byes_needed > 0:
            db.add(
                Match(
                    event_id=event.id,
                    stage="elimination",
                    wave=wave,
                    bracket_slot=slot,
                    player_a_id=left.id,
                    player_b_id=None,
                    status="completed",
                    winner_id=left.id,
                )
            )
            byes_needed -= 1
            slot += 1
            continue
        if not queue:
            db.add(
                Match(
                    event_id=event.id,
                    stage="elimination",
                    wave=wave,
                    bracket_slot=slot,
                    player_a_id=left.id,
                    player_b_id=None,
                    status="completed",
                    winner_id=left.id,
                )
            )
            slot += 1
            break
        right = queue.pop(0)
        db.add(
            Match(
                event_id=event.id,
                stage="elimination",
                wave=wave,
                bracket_slot=slot,
                player_a_id=left.id,
                player_b_id=right.id,
                status="pending",
            )
        )
        slot += 1


def _group_advancers(db: Session, event: Event) -> list[Player]:
    table = standings_for_event(db, event)
    grouped: dict[str, list[dict]] = {}
    for row in table:
        grouped.setdefault(row["group_label"] or "A", []).append(row)
    advancers: list[Player] = []
    for rows in grouped.values():
        for row in rows[: event.advance_per_group]:
            player = db.get(Player, row["player_id"])
            if player:
                advancers.append(player)
    return advancers


def payoff_of(event: Event) -> dict:
    try:
        return json.loads(event.payoff_json)
    except json.JSONDecodeError:
        return {"AA": [-2, -2], "AB": [5, 0], "BA": [0, 5], "BB": [2, 2]}
