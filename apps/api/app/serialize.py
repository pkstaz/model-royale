from app.models import Avatar, Event, Match, Player, Round


def avatar_out(avatar: Avatar, public: bool = False) -> dict:
    data = {
        "id": avatar.id,
        "name": avatar.name,
        "slug": avatar.slug,
        "description": avatar.description,
        "color": avatar.color,
        "provider": avatar.provider,
        "base_url": "" if public else avatar.base_url,
        "model_id": avatar.model_id,
        "has_api_key": False if public else bool(avatar.api_key),
        "temperature": avatar.temperature,
        "max_tokens": avatar.max_tokens,
        "personality": avatar.personality,
        "enabled": avatar.enabled,
        "reachable": bool(avatar.base_url and avatar.model_id),
    }
    return data


def player_out(player: Player, locked: bool = False) -> dict:
    return {
        "id": player.id,
        "event_id": player.event_id,
        "display_name": player.display_name,
        "avatar_id": player.avatar_id,
        "avatar": avatar_out(player.avatar, public=True) if player.avatar else None,
        "strategy_prompt": player.strategy_prompt,
        "group_label": player.group_label,
        "eliminated": player.eliminated,
        "seed": player.seed,
        "locked": locked,
        "created_at": player.created_at.isoformat() if player.created_at else None,
    }


def round_out(round_: Round) -> dict:
    return {
        "id": round_.id,
        "index": round_.index,
        "move_a": round_.move_a,
        "move_b": round_.move_b,
        "points_a": round_.points_a,
        "points_b": round_.points_b,
        "rationale_a": round_.rationale_a,
        "rationale_b": round_.rationale_b,
        "judge_notes": round_.judge_notes,
        "invalid_a": round_.invalid_a,
        "invalid_b": round_.invalid_b,
    }


def match_out(match: Match, players: dict[str, Player] | None = None) -> dict:
    def name_of(pid: str | None) -> str | None:
        if not pid:
            return None
        if players and pid in players:
            return players[pid].display_name
        return pid

    return {
        "id": match.id,
        "stage": match.stage,
        "wave": match.wave,
        "group_label": match.group_label,
        "bracket_slot": match.bracket_slot,
        "player_a_id": match.player_a_id,
        "player_b_id": match.player_b_id,
        "player_a_name": name_of(match.player_a_id),
        "player_b_name": name_of(match.player_b_id),
        "status": match.status,
        "winner_id": match.winner_id,
        "score_a": match.score_a,
        "score_b": match.score_b,
        "rounds": [round_out(item) for item in (match.rounds or [])],
    }


def event_out(event: Event) -> dict:
    import json

    try:
        payoff = json.loads(event.payoff_json) if event.payoff_json else {}
    except json.JSONDecodeError:
        payoff = {}
    return {
        "id": event.id,
        "name": event.name,
        "code": event.code,
        "status": event.status,
        "format": event.format,
        "rounds_per_match": event.rounds_per_match,
        "max_players": event.max_players,
        "min_players": event.min_players,
        "group_size": event.group_size,
        "advance_per_group": event.advance_per_group,
        "reveal_mode": event.reveal_mode,
        "payoff": payoff,
        "rules_prompt": event.rules_prompt,
        "judge_avatar_id": event.judge_avatar_id,
        "invalid_move_policy": event.invalid_move_policy,
        "auto_advance": event.auto_advance,
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }
