from __future__ import annotations

import asyncio
import json
import random
import time

from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.connection import load_connection
from app.database import SessionLocal
from app.hub import hub
from app.i18n import t
from app.judge import judge_move
from app.llm import complete_chat, mock_move
from app.models import Avatar, Event, Match, Player, Round
from app.serialize import event_out, match_out, player_out
from app.standings import player_is_locked, standings_for_event
from app.tournament import maybe_advance, payoff_of


def snapshot(db: Session, event: Event) -> dict:
    players = (
        db.query(Player)
        .options(joinedload(Player.avatar))
        .filter(Player.event_id == event.id)
        .order_by(Player.seed.asc())
        .all()
    )
    matches = (
        db.query(Match)
        .options(joinedload(Match.rounds))
        .filter(Match.event_id == event.id)
        .order_by(Match.wave.asc(), Match.bracket_slot.asc())
        .all()
    )
    locked = {player.id: player_is_locked(db, player.id) for player in players}
    by_id = {player.id: player for player in players}
    return {
        "type": "snapshot",
        "event": event_out(event),
        "players": [player_out(player, locked=locked[player.id]) for player in players],
        "matches": [match_out(match, by_id, event.rounds_per_match) for match in matches],
        "standings": standings_for_event(db, event),
    }


async def publish_snapshot(event_id: str) -> None:
    db = SessionLocal()
    try:
        event = db.get(Event, event_id)
        if event:
            await hub.publish(event_id, snapshot(db, event))
    finally:
        db.close()


_match_tasks: dict[str, asyncio.Task] = {}


def _spawn_match(match_id: str) -> None:
    current = _match_tasks.get(match_id)
    if current and not current.done():
        return
    task = asyncio.create_task(run_match(match_id))
    _match_tasks[match_id] = task
    task.add_done_callback(lambda _task: _match_tasks.pop(match_id, None))


async def engine_loop() -> None:
    while True:
        try:
            await _tick()
        except Exception as exc:
            print(f"engine tick error: {exc}")
            await asyncio.sleep(1.5)
            continue
        await asyncio.sleep(0.6)


async def _tick() -> None:
    db = SessionLocal()
    try:
        events = db.query(Event).filter(Event.status == "running").all()
        running = db.query(Match).filter(Match.status == "running").all()
        started = 0
        for match in running:
            task = _match_tasks.get(match.id)
            if task and not task.done():
                continue
            match.status = "pending"
            db.commit()
            print(f"engine requeue orphan match={match.id}")
        running = db.query(Match).filter(Match.status == "running").all()
        busy = set()
        for match in running:
            if match.player_a_id:
                busy.add(match.player_a_id)
            if match.player_b_id:
                busy.add(match.player_b_id)
        for event in events:
            pending = (
                db.query(Match)
                .filter(Match.event_id == event.id, Match.status == "pending", Match.player_b_id.is_not(None))
                .order_by(Match.wave.asc(), Match.bracket_slot.asc())
                .all()
            )
            for match in pending:
                if started >= 4:
                    break
                if match.player_a_id in busy or match.player_b_id in busy:
                    continue
                match.status = "running"
                if match.player_a_id:
                    busy.add(match.player_a_id)
                if match.player_b_id:
                    busy.add(match.player_b_id)
                db.commit()
                _spawn_match(match.id)
                started += 1
    finally:
        db.close()


def _history_for(rounds: list[Round], side: str) -> list[dict]:
    history = []
    for item in rounds:
        if side == "a":
            history.append({"me": item.move_a, "opp": item.move_b, "pts_me": item.points_a, "pts_opp": item.points_b})
        else:
            history.append({"me": item.move_b, "opp": item.move_a, "pts_me": item.points_b, "pts_opp": item.points_a})
    return history


def _messages(
    event: Event,
    player: Player,
    avatar: Avatar,
    history: list[dict],
    extra: str,
    overtime: bool = False,
) -> list[dict]:
    rules = event.rules_prompt or ""
    payoff = event.payoff_json
    system = "\n\n".join(
        part
        for part in (
            avatar.personality.strip() if avatar.personality else "",
            rules.strip(),
            t("payoff_json", payoff=payoff),
            t("same_move_rule"),
            t(
                "player_strategy",
                name=player.display_name,
                strategy=player.strategy_prompt or t("no_extra_strategy"),
            ),
        )
        if part
    )
    history_lines = [
        t("history_line", n=index + 1, me=item["me"], opp=item["opp"], pts_me=item["pts_me"], pts_opp=item["pts_opp"])
        for index, item in enumerate(history)
    ]
    user = t("overtime_round") if overtime else t("new_round")
    if extra:
        user += "\n" + extra
    if event.reveal_mode == "history" and history_lines:
        user += "\n" + t("history_header") + "\n" + "\n".join(history_lines)
    elif event.reveal_mode == "blind":
        user += "\n" + t("blind_mode")
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


async def _move_for(
    event: Event,
    player: Player,
    avatar: Avatar,
    history: list[dict],
    extra: str,
    overtime: bool = False,
) -> str:
    base_url, _api_key = load_connection(avatar)
    if settings.mock_inference or not base_url or not avatar.model_id:
        mocked = mock_move(player.strategy_prompt, history, player.display_name)
        return json.dumps(mocked)
    messages = _messages(event, player, avatar, history, extra, overtime=overtime)
    try:
        return await complete_chat(
            avatar,
            messages,
            temperature=0.4 if player.temperature is None else player.temperature,
        )
    except Exception as exc:
        print(f"llm fail {avatar.name}: {exc}")
        return json.dumps({"move": "B", "rationale": str(exc)[:160]})


SUDDEN_DEATH_CAP = 6


def _pick_winner(match: Match, rounds: list[Round] | None = None) -> str | None:
    if not match.player_b_id:
        return match.player_a_id
    if match.score_a > match.score_b:
        return match.player_a_id
    if match.score_b > match.score_a:
        return match.player_b_id
    played = rounds if rounds is not None else list(match.rounds or [])
    invalid_a = sum(1 for item in played if item.invalid_a)
    invalid_b = sum(1 for item in played if item.invalid_b)
    if invalid_a < invalid_b:
        return match.player_a_id
    if invalid_b < invalid_a:
        return match.player_b_id
    for item in reversed(played):
        if item.move_a != item.move_b:
            if item.points_a > item.points_b:
                return match.player_a_id
            if item.points_b > item.points_a:
                return match.player_b_id
    return match.player_a_id if int(match.id[:8], 16) % 2 == 0 else match.player_b_id


def _same_move_split(
    move_a: str,
    move_b: str,
    pts_a: int,
    pts_b: int,
    name_a: str,
    name_b: str,
) -> tuple[int, int, str]:
    if move_a != move_b or move_a not in {"A", "B"}:
        return pts_a, pts_b, ""
    delta = -3 if move_a == "A" else 2
    if random.choice(["a", "b"]) == "a":
        pts_a += delta
        name = name_a
    else:
        pts_b += delta
        name = name_b
    return pts_a, pts_b, t("same_move_split", move=move_a, delta=delta, name=name)


async def _play_round(
    db: Session,
    match: Match,
    event: Event,
    player_a: Player,
    player_b: Player,
    avatar_a: Avatar,
    avatar_b: Avatar,
    judge: Avatar | None,
    matrix: dict,
    index: int,
    overtime: bool,
) -> None:
    played = db.query(Round).filter(Round.match_id == match.id).order_by(Round.index.asc()).all()
    hist_a = _history_for(played, "a")
    hist_b = _history_for(played, "b")
    extra_a = extra_b = ""
    first = random.choice(["a", "b"]) if event.reveal_mode == "open" else "a"
    match.first_mover = first
    round_started = time.monotonic()
    if event.reveal_mode == "open":
        if first == "a":
            raw_a = await _move_for(event, player_a, avatar_a, hist_a, "", overtime=overtime)
            move_a, rat_a, inv_a, notes_a = await judge_move(raw_a, judge, event.invalid_move_policy)
            extra_b = t("opponent_just_played", move=move_a)
            raw_b = await _move_for(event, player_b, avatar_b, hist_b, extra_b, overtime=overtime)
            move_b, rat_b, inv_b, notes_b = await judge_move(raw_b, judge, event.invalid_move_policy)
        else:
            raw_b = await _move_for(event, player_b, avatar_b, hist_b, "", overtime=overtime)
            move_b, rat_b, inv_b, notes_b = await judge_move(raw_b, judge, event.invalid_move_policy)
            extra_a = t("opponent_just_played", move=move_b)
            raw_a = await _move_for(event, player_a, avatar_a, hist_a, extra_a, overtime=overtime)
            move_a, rat_a, inv_a, notes_a = await judge_move(raw_a, judge, event.invalid_move_policy)
    else:
        raw_a, raw_b = await asyncio.gather(
            _move_for(event, player_a, avatar_a, hist_a, extra_a, overtime=overtime),
            _move_for(event, player_b, avatar_b, hist_b, extra_b, overtime=overtime),
        )
        move_a, rat_a, inv_a, notes_a = await judge_move(raw_a, judge, event.invalid_move_policy)
        move_b, rat_b, inv_b, notes_b = await judge_move(raw_b, judge, event.invalid_move_policy)
    print(f"round match={match.id} r{index}{' ot' if overtime else ''} {time.monotonic() - round_started:.2f}s")

    pts_a, pts_b = matrix.get(move_a + move_b, [0, 0])
    if event.invalid_move_policy == "zero":
        if inv_a:
            pts_a = 0
        if inv_b:
            pts_b = 0
    pts_a, pts_b, split_note = _same_move_split(
        move_a,
        move_b,
        pts_a,
        pts_b,
        player_a.display_name,
        player_b.display_name,
    )
    db.add(
        Round(
            match_id=match.id,
            index=index,
            move_a=move_a,
            move_b=move_b,
            points_a=pts_a,
            points_b=pts_b,
            raw_a=raw_a,
            raw_b=raw_b,
            rationale_a=rat_a,
            rationale_b=rat_b,
            judge_notes=" | ".join(item for item in (notes_a, notes_b, split_note) if item),
            invalid_a=inv_a,
            invalid_b=inv_b,
        )
    )
    match.score_a += pts_a
    match.score_b += pts_b
    db.commit()


async def run_match(match_id: str) -> None:
    db = SessionLocal()
    try:
        await _run_match(db, match_id)
    except Exception:
        match = db.get(Match, match_id)
        if match and match.status == "running":
            match.status = "pending"
            db.commit()
        raise
    finally:
        db.close()


async def _run_match(db: Session, match_id: str) -> None:
    match = db.get(Match, match_id)
    if not match:
        return
    event = db.get(Event, match.event_id)
    player_a = db.get(Player, match.player_a_id)
    player_b = db.get(Player, match.player_b_id)
    if not event or not player_a or not player_b:
        match.status = "completed"
        match.winner_id = match.player_a_id
        db.commit()
        return
    avatar_a = player_a.avatar or db.query(Avatar).filter(Avatar.enabled.is_(True)).first()
    avatar_b = player_b.avatar or db.query(Avatar).filter(Avatar.enabled.is_(True)).first()
    if not avatar_a or not avatar_b:
        match.status = "completed"
        match.winner_id = player_a.id
        db.commit()
        await publish_snapshot(event.id)
        return
    judge = db.get(Avatar, event.judge_avatar_id) if event.judge_avatar_id else None
    matrix = payoff_of(event)
    await publish_snapshot(event.id)

    scheduled = max(1, event.rounds_per_match)
    index = 1
    while True:
        played = (
            db.query(Round).filter(Round.match_id == match.id).order_by(Round.index.asc()).all()
        )
        overtime = index > scheduled
        if not any(item.index == index for item in played):
            await _play_round(
                db,
                match,
                event,
                player_a,
                player_b,
                avatar_a,
                avatar_b,
                judge,
                matrix,
                index,
                overtime,
            )
            await publish_snapshot(event.id)
            await asyncio.sleep(settings.match_pause_seconds)
        if index < scheduled:
            index += 1
            continue
        db.refresh(match)
        if match.score_a != match.score_b:
            break
        if index >= scheduled + SUDDEN_DEATH_CAP:
            break
        index += 1

    played = db.query(Round).filter(Round.match_id == match.id).order_by(Round.index.asc()).all()
    match.status = "completed"
    match.winner_id = _pick_winner(match, played)
    db.commit()
    if event.auto_advance:
        maybe_advance(db, event)
    await publish_snapshot(event.id)
