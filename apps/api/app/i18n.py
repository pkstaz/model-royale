from __future__ import annotations

from typing import Literal

from app.config import settings

Lang = Literal["en", "es", "pt"]

EN = {
    "default_rules": (
        "You are an avatar in Model Royale. Each round you choose exactly one action: A or B.\n\n"
        "The payoff matrix for this event is shown below. Reply only with JSON:\n"
        '{"move": "A" or "B", "rationale": "max 12 words"}\n\n'
        "Do not use markdown. Do not explain outside the JSON."
    ),
    "seed_event_name": "Model Royale Workshop",
    "avatar_redrock_desc": "Granite 3.2 8B instruct. Red Hat's rock on the workshop MaaS.",
    "avatar_redrock_personality": "You are Redrock (Granite 3.2 8B): direct, sober, you favor consistency over bluffing.",
    "avatar_slate_desc": "Phi-4. Compact dense model, slate-gray precision.",
    "avatar_slate_personality": "You are Slate (Phi-4): compact, precise, you write little and play tight.",
    "avatar_nexus_desc": "Qwen 3 14B. Generalist hub that connects tactics.",
    "avatar_nexus_personality": "You are Nexus (Qwen 3 14B): you connect threads, adapt, and switch tactics when the history says so.",
    "avatar_trail_desc": "Llama Scout 17B. Explorer that marks the path.",
    "avatar_trail_personality": "You are Trail (Llama Scout): you scout the history and adjust round by round; you explore but you mark the path.",
    "avatar_forge_desc": "gpt-oss-20b. Open-weight forge — 20B, not 120B.",
    "avatar_forge_personality": "You are Forge (gpt-oss-20b): you hit harder, you forge a plan and you commit; still you read the opponent.",
    "payoff_json": "Payoff matrix JSON: {payoff}",
    "player_strategy": "Strategy from player {name}:\n{strategy}",
    "no_extra_strategy": "(no extra instructions)",
    "new_round": "New round. Choose A or B.",
    "overtime_round": (
        "The match is tied. Choose A or B. Same moves still assign a random extra: "
        "AA gives -3 to one player, BB gives +2 to one player."
    ),
    "same_move_rule": (
        "If both play A, one random player gets -3 extra. If both play B, one random player gets +2 extra."
    ),
    "same_move_split": "Both {move}: {delta:+d} to {name}",
    "history_header": "History of this match:",
    "history_line": "round {n}: me={me} opp={opp} pts={pts_me}/{pts_opp}",
    "blind_mode": "You do not know the history or the opponent's current move.",
    "opponent_just_played": "The opponent just played {move} this round.",
    "judge_system": 'You are the Model Royale judge. Extract action A or B. Reply JSON {"move":"A"|"B"|null,"notes":"..."}.',
    "judge_local": "local parser",
    "judge_notes": "judge",
    "judge_failed": "judge failed: {exc}",
    "invalid_zero": "invalid, 0 points",
    "invalid_fallback": "invalid, using {move}",
    "mock_fixed_a": "Fixed strategy: A",
    "mock_fixed_b": "Fixed strategy: B",
    "mock_tft": "Tit-for-tat on the opponent's last move",
    "mock_grim": "Grim trigger",
    "mock_forgive": "Cooperate; punish only streaks",
    "mock_mix": "Mix derived from the prompt",
    "ping_no_endpoint": "No URL or model id: this avatar will use the mock engine.",
    "ping_system": 'Reply with JSON {"ok": true}',
    "missing_token": "Missing token",
    "invalid_token": "Invalid token",
    "admin_required": "Admin required",
    "player_required": "Player required",
    "player_not_found": "Player not found",
    "bad_admin_password": "Incorrect password",
    "slug_exists": "Slug already exists",
    "avatar_not_found": "Avatar not found",
    "event_not_found": "Event not found",
    "event_locked": "A running event cannot be edited",
    "code_taken": "That event code is already in use",
    "cannot_open_reg": "Registration can no longer be opened",
    "cannot_start": "The event already started",
    "cannot_next_round": "Start the event before launching a round",
    "round_in_progress": "This round is still running",
    "not_enough_players": "Not enough players",
    "players_without_avatar": "Some players have no avatar",
    "reg_closed": "Registration is not open. If you already signed up, use Log in.",
    "event_full": "Event is full",
    "name_taken": "That name is already registered. Log in with your password.",
    "no_player": "There is no registration with that name",
    "no_password": "This account has no password. Sign up again or ask an admin to reset it.",
    "bad_password": "Incorrect password",
    "in_combat": "Your avatar is in a match. You can edit when it ends.",
    "avatar_unavailable": "Avatar is not available",
}

ES = {
    **EN,
    "default_rules": (
        "Eres un avatar en Model Royale. En cada ronda eliges exactamente una acción: A o B.\n\n"
        "La matriz de pagos de este evento se indica más abajo. Responde únicamente con JSON:\n"
        '{"move": "A" o "B", "rationale": "máximo 12 palabras"}\n\n'
        "No uses markdown. No expliques fuera del JSON."
    ),
    "seed_event_name": "Taller Model Royale",
    "avatar_redrock_desc": "Granite 3.2 8B instruct. La roca de Red Hat en el MaaS del taller.",
    "avatar_redrock_personality": "Eres Redrock (Granite 3.2 8B): directo, sobrio, priorizas consistencia sobre faroleo.",
    "avatar_slate_desc": "Phi-4. Modelo denso y compacto, precisión de pizarra.",
    "avatar_slate_personality": "Eres Slate (Phi-4): compacto, preciso, escribes poco y juegas apretado.",
    "avatar_nexus_desc": "Qwen 3 14B. Hub generalista que conecta tácticas.",
    "avatar_nexus_personality": "Eres Nexus (Qwen 3 14B): conectas hilos, adaptas y cambias de táctica cuando el historial lo pide.",
    "avatar_trail_desc": "Llama Scout 17B. Explorador que marca el camino.",
    "avatar_trail_personality": "Eres Trail (Llama Scout): recorres el historial y ajustas ronda a ronda; exploras, pero marcas el sendero.",
    "avatar_forge_desc": "gpt-oss-20b. Forja de pesos abiertos — 20B, no 120B.",
    "avatar_forge_personality": "Eres Forge (gpt-oss-20b): golpeas más duro, forjas un plan y te comprometes; igual lees al oponente.",
    "payoff_json": "Matriz de pagos JSON: {payoff}",
    "player_strategy": "Estrategia del jugador {name}:\n{strategy}",
    "no_extra_strategy": "(sin instrucciones extra)",
    "new_round": "Ronda nueva. Elige A o B.",
    "overtime_round": (
        "El combate está empatado. Elige A o B. Si ambos juegan lo mismo, igual hay un extra al azar: "
        "AA da -3 a un jugador, BB da +2 a un jugador."
    ),
    "same_move_rule": (
        "Si ambos juegan A, un jugador al azar recibe -3 extra. Si ambos juegan B, un jugador al azar recibe +2 extra."
    ),
    "same_move_split": "Ambos {move}: {delta:+d} a {name}",
    "history_header": "Historial de este combate:",
    "blind_mode": "No conoces el historial ni la jugada actual del oponente.",
    "opponent_just_played": "El oponente acaba de jugar {move} en esta ronda.",
    "judge_system": 'Eres el juez de Model Royale. Extrae la acción A o B. Responde JSON {"move":"A"|"B"|null,"notes":"..."}.',
    "judge_local": "parser local",
    "judge_notes": "juez",
    "judge_failed": "juez falló: {exc}",
    "invalid_zero": "inválida, 0 puntos",
    "invalid_fallback": "inválida, se toma {move}",
    "mock_fixed_a": "Estrategia fija: A",
    "mock_fixed_b": "Estrategia fija: B",
    "mock_tft": "Tit-for-tat sobre la última jugada rival",
    "mock_grim": "Grim trigger",
    "mock_forgive": "Cooperar, castigar solo rachas",
    "mock_mix": "Mezcla a partir del prompt",
    "ping_no_endpoint": "Sin URL o model id: este avatar usará el motor mock.",
    "ping_system": 'Responde JSON {"ok": true}',
    "missing_token": "Falta token",
    "invalid_token": "Token inválido",
    "admin_required": "Se requiere admin",
    "player_required": "Se requiere jugador",
    "player_not_found": "Jugador no encontrado",
    "bad_admin_password": "Clave incorrecta",
    "slug_exists": "Slug ya existe",
    "avatar_not_found": "Avatar no encontrado",
    "event_not_found": "Evento no encontrado",
    "event_locked": "No se edita un evento en curso",
    "code_taken": "Ese código de evento ya está en uso",
    "cannot_open_reg": "Ya no se puede abrir inscripción",
    "cannot_start": "El evento ya partió",
    "cannot_next_round": "Inicia el evento antes de lanzar una ronda",
    "round_in_progress": "Esta ronda todavía está en curso",
    "not_enough_players": "Faltan jugadores",
    "players_without_avatar": "Hay jugadores sin avatar",
    "reg_closed": "La inscripción no está abierta. Si ya te inscribiste, usa Entrar.",
    "event_full": "Cupo completo",
    "name_taken": "Ese nombre ya está inscrito. Entra con tu clave.",
    "no_player": "No hay una inscripción con ese nombre",
    "no_password": "Esta cuenta no tiene clave. Inscríbete de nuevo o pide un reinicio al admin.",
    "bad_password": "Clave incorrecta",
    "in_combat": "Tu avatar está en combate. Podrás editar cuando termine.",
    "avatar_unavailable": "Avatar no disponible",
}

PT = {
    **EN,
    "default_rules": (
        "Você é um avatar em Model Royale. Em cada rodada você escolhe exatamente uma ação: A ou B.\n\n"
        "A matriz de pagamentos deste evento aparece abaixo. Responda somente com JSON:\n"
        '{"move": "A" ou "B", "rationale": "no máximo 12 palavras"}\n\n'
        "Não use markdown. Não explique fora do JSON."
    ),
    "seed_event_name": "Oficina Model Royale",
    "avatar_redrock_desc": "Granite 3.2 8B instruct. A rocha da Red Hat no MaaS da oficina.",
    "avatar_redrock_personality": "Você é Redrock (Granite 3.2 8B): direto, sóbrio, prioriza consistência em vez de blefe.",
    "avatar_slate_desc": "Phi-4. Modelo denso e compacto, precisão de ardósia.",
    "avatar_slate_personality": "Você é Slate (Phi-4): compacto, preciso, escreve pouco e joga apertado.",
    "avatar_nexus_desc": "Qwen 3 14B. Hub generalista que conecta táticas.",
    "avatar_nexus_personality": "Você é Nexus (Qwen 3 14B): conecta fios, adapta e muda de tática quando o histórico pede.",
    "avatar_trail_desc": "Llama Scout 17B. Explorador que marca o caminho.",
    "avatar_trail_personality": "Você é Trail (Llama Scout): percorre o histórico e ajusta a cada rodada; explora, mas marca a trilha.",
    "avatar_forge_desc": "gpt-oss-20b. Forja de pesos abertos — 20B, não 120B.",
    "avatar_forge_personality": "Você é Forge (gpt-oss-20b): golpeia mais forte, forja um plano e se compromete; ainda assim lê o oponente.",
    "payoff_json": "Matriz de pagamentos JSON: {payoff}",
    "player_strategy": "Estratégia do jogador {name}:\n{strategy}",
    "no_extra_strategy": "(sem instruções extras)",
    "new_round": "Nova rodada. Escolha A ou B.",
    "overtime_round": (
        "O combate está empatado. Escolha A ou B. Se ambos jogarem a mesma ação, ainda há um extra aleatório: "
        "AA dá -3 a um jogador, BB dá +2 a um jogador."
    ),
    "same_move_rule": (
        "Se ambos jogarem A, um jogador aleatório recebe -3 extra. Se ambos jogarem B, um jogador aleatório recebe +2 extra."
    ),
    "same_move_split": "Ambos {move}: {delta:+d} para {name}",
    "history_header": "Histórico deste combate:",
    "blind_mode": "Você não conhece o histórico nem a jogada atual do oponente.",
    "opponent_just_played": "O oponente acabou de jogar {move} nesta rodada.",
    "judge_system": 'Você é o juiz de Model Royale. Extraia a ação A ou B. Responda JSON {"move":"A"|"B"|null,"notes":"..."}.',
    "judge_local": "parser local",
    "judge_notes": "juiz",
    "judge_failed": "juiz falhou: {exc}",
    "invalid_zero": "inválida, 0 pontos",
    "invalid_fallback": "inválida, usa-se {move}",
    "mock_fixed_a": "Estratégia fixa: A",
    "mock_fixed_b": "Estratégia fixa: B",
    "mock_tft": "Tit-for-tat sobre a última jogada do rival",
    "mock_grim": "Grim trigger",
    "mock_forgive": "Cooperar; punir só sequências",
    "mock_mix": "Mistura a partir do prompt",
    "ping_no_endpoint": "Sem URL ou model id: este avatar usará o motor mock.",
    "ping_system": 'Responda JSON {"ok": true}',
    "missing_token": "Falta token",
    "invalid_token": "Token inválido",
    "admin_required": "É necessário admin",
    "player_required": "É necessário jogador",
    "player_not_found": "Jogador não encontrado",
    "bad_admin_password": "Senha incorreta",
    "slug_exists": "Slug já existe",
    "avatar_not_found": "Avatar não encontrado",
    "event_not_found": "Evento não encontrado",
    "event_locked": "Não se edita um evento em andamento",
    "code_taken": "Esse código de evento já está em uso",
    "cannot_open_reg": "Já não é possível abrir inscrição",
    "cannot_start": "O evento já começou",
    "cannot_next_round": "Inicie o evento antes de lançar uma rodada",
    "round_in_progress": "Esta rodada ainda está em andamento",
    "not_enough_players": "Faltam jogadores",
    "players_without_avatar": "Há jogadores sem avatar",
    "reg_closed": "A inscrição não está aberta. Se você já se inscreveu, use Entrar.",
    "event_full": "Vagas esgotadas",
    "name_taken": "Esse nome já está inscrito. Entre com sua senha.",
    "no_player": "Não há inscrição com esse nome",
    "no_password": "Esta conta não tem senha. Inscreva-se de novo ou peça um reset ao admin.",
    "bad_password": "Senha incorreta",
    "in_combat": "Seu avatar está em combate. Você poderá editar quando terminar.",
    "avatar_unavailable": "Avatar indisponível",
}

CATALOGS: dict[str, dict[str, str]] = {"en": EN, "es": ES, "pt": PT}


def lang() -> Lang:
    raw = (settings.app_lang or "en").strip().lower()[:2]
    if raw in ("en", "es", "pt"):
        return raw  # type: ignore[return-value]
    return "en"


def t(key: str, **vars: object) -> str:
    catalog = CATALOGS[lang()]
    template = catalog.get(key) or EN[key]
    if not vars:
        return template
    return template.format(**vars)


def starter_avatars() -> list[dict]:
    return [
        {
            "name": "Redrock",
            "slug": "redrock",
            "model_id": "granite-3-2-8b-instruct",
            "description": t("avatar_redrock_desc"),
            "color": "#EE0000",
            "personality": t("avatar_redrock_personality"),
        },
        {
            "name": "Slate",
            "slug": "slate",
            "model_id": "microsoft-phi-4",
            "description": t("avatar_slate_desc"),
            "color": "#8A8D90",
            "personality": t("avatar_slate_personality"),
        },
        {
            "name": "Nexus",
            "slug": "nexus",
            "model_id": "qwen3-14b",
            "description": t("avatar_nexus_desc"),
            "color": "#73BCF7",
            "personality": t("avatar_nexus_personality"),
        },
        {
            "name": "Trail",
            "slug": "trail",
            "model_id": "llama-scout-17b",
            "description": t("avatar_trail_desc"),
            "color": "#F0AB00",
            "personality": t("avatar_trail_personality"),
        },
        {
            "name": "Forge",
            "slug": "forge",
            "model_id": "gpt-oss-20b",
            "description": t("avatar_forge_desc"),
            "color": "#EC7A08",
            "personality": t("avatar_forge_personality"),
        },
    ]
