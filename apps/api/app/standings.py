from __future__ import annotations

from collections import defaultdict

from sqlalchemy.orm import Session

from app.models import Event, Match, Player, Round


def standings_for_event(db: Session, event: Event) -> list[dict]:
    players = db.query(Player).filter(Player.event_id == event.id).all()
    matches = (
        db.query(Match)
        .filter(Match.event_id == event.id, Match.status == "completed", Match.player_b_id.is_not(None))
        .all()
    )
    stats: dict[str, dict] = {
        player.id: {
            "player_id": player.id,
            "display_name": player.display_name,
            "avatar": player.avatar.name if player.avatar else None,
            "avatar_color": player.avatar.color if player.avatar else "#EE0000",
            "group_label": player.group_label,
            "eliminated": player.eliminated,
            "points": 0,
            "wins": 0,
            "losses": 0,
            "matches": 0,
            "invalids": 0,
            "seed": player.seed,
        }
        for player in players
    }
    rounds = db.query(Round).join(Match).filter(Match.event_id == event.id).all()
    invalids = defaultdict(int)
    for round_ in rounds:
        match = next((item for item in matches if item.id == round_.match_id), None)
        if not match:
            continue
        if round_.invalid_a and match.player_a_id:
            invalids[match.player_a_id] += 1
        if round_.invalid_b and match.player_b_id:
            invalids[match.player_b_id] += 1
    for match in matches:
        if match.player_a_id in stats:
            stats[match.player_a_id]["points"] += match.score_a
            stats[match.player_a_id]["matches"] += 1
        if match.player_b_id in stats:
            stats[match.player_b_id]["points"] += match.score_b
            stats[match.player_b_id]["matches"] += 1
        if match.winner_id and match.winner_id in stats:
            stats[match.winner_id]["wins"] += 1
            loser = match.player_b_id if match.winner_id == match.player_a_id else match.player_a_id
            if loser in stats:
                stats[loser]["losses"] += 1
    for player_id, count in invalids.items():
        if player_id in stats:
            stats[player_id]["invalids"] = count
    rows = list(stats.values())
    rows.sort(key=lambda row: (-row["points"], -row["wins"], row["invalids"], row["seed"]))
    for index, row in enumerate(rows, start=1):
        row["rank"] = index
    return rows


def player_is_locked(db: Session, player_id: str) -> bool:
    running = (
        db.query(Match)
        .filter(
            Match.status == "running",
            (Match.player_a_id == player_id) | (Match.player_b_id == player_id),
        )
        .count()
    )
    return running > 0
