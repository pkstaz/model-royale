from __future__ import annotations

from typing import Literal

from app.config import settings

Lang = Literal["en", "es", "pt"]

EN = {
    "default_rules": (
        "You are an avatar in Model Royale. Each round you choose exactly one action: A or B.\n\n"
        "The payoff matrix for this event is shown below. Reply only with JSON:\n"
        '{"move": "A" or "B", "rationale": "one sentence"}\n\n'
        "Do not use markdown. Do not explain outside the JSON."
    ),
    "seed_event_name": "Model Royale Workshop",
    "avatar_granite_desc": "Red Hat / IBM Granite avatar. Paste the OpenShift AI endpoint here.",
    "avatar_granite_personality": "You are Granite: direct, sober, you favor consistency over bluffing.",
    "avatar_llama_desc": "Meta Llama served in the cluster. Fill in URL and model id.",
    "avatar_llama_personality": "You are Llama: you explore, adapt, and do not lock onto a single tactic.",
    "avatar_mistral_desc": "Mistral / Mixtral on OpenShift AI.",
    "avatar_mistral_personality": "You are Mistral: compact, tactical, you chase expected payoff.",
    "avatar_glm_desc": "GLM. The model lives outside this game.",
    "avatar_glm_personality": "You are GLM: analytical, you explain little and play with discipline.",
    "avatar_kimi_desc": "Kimi. Configure the predictor when it exists.",
    "avatar_kimi_personality": "You are Kimi: you watch the history and adjust round by round.",
    "payoff_json": "Payoff matrix JSON: {payoff}",
    "player_strategy": "Strategy from player {name}:\n{strategy}",
    "no_extra_strategy": "(no extra instructions)",
    "new_round": "New round. Choose A or B.",
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
    "cannot_open_reg": "Registration can no longer be opened",
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
        '{"move": "A" o "B", "rationale": "una frase"}\n\n'
        "No uses markdown. No expliques fuera del JSON."
    ),
    "seed_event_name": "Taller Model Royale",
    "avatar_granite_desc": "Avatar Red Hat / IBM Granite. Pega aquí el endpoint de OpenShift AI.",
    "avatar_granite_personality": "Eres Granite: directo, sobrio, priorizas consistencia sobre faroleo.",
    "avatar_llama_desc": "Meta Llama servido en el cluster. Completa URL y model id.",
    "avatar_llama_personality": "Eres Llama: exploras, adaptas y no te cascas en una sola táctica.",
    "avatar_mistral_desc": "Mistral / Mixtral en OpenShift AI.",
    "avatar_mistral_personality": "Eres Mistral: compacto, táctico, buscas el pago esperado.",
    "avatar_glm_desc": "GLM. El modelo vive fuera de este juego.",
    "avatar_glm_personality": "Eres GLM: analítico, explicas poco y juegas con disciplina.",
    "avatar_kimi_desc": "Kimi. Configura el predictor cuando exista.",
    "avatar_kimi_personality": "Eres Kimi: observas el historial y ajustas ronda a ronda.",
    "payoff_json": "Matriz de pagos JSON: {payoff}",
    "player_strategy": "Estrategia del jugador {name}:\n{strategy}",
    "no_extra_strategy": "(sin instrucciones extra)",
    "new_round": "Ronda nueva. Elige A o B.",
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
    "cannot_open_reg": "Ya no se puede abrir inscripción",
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
        '{"move": "A" ou "B", "rationale": "uma frase"}\n\n'
        "Não use markdown. Não explique fora do JSON."
    ),
    "seed_event_name": "Oficina Model Royale",
    "avatar_granite_desc": "Avatar Red Hat / IBM Granite. Cole aqui o endpoint do OpenShift AI.",
    "avatar_granite_personality": "Você é Granite: direto, sóbrio, prioriza consistência em vez de blefe.",
    "avatar_llama_desc": "Meta Llama servido no cluster. Preencha URL e model id.",
    "avatar_llama_personality": "Você é Llama: explora, adapta e não se prende a uma só tática.",
    "avatar_mistral_desc": "Mistral / Mixtral no OpenShift AI.",
    "avatar_mistral_personality": "Você é Mistral: compacto, tático, busca o pagamento esperado.",
    "avatar_glm_desc": "GLM. O modelo vive fora deste jogo.",
    "avatar_glm_personality": "Você é GLM: analítico, explica pouco e joga com disciplina.",
    "avatar_kimi_desc": "Kimi. Configure o predictor quando existir.",
    "avatar_kimi_personality": "Você é Kimi: observa o histórico e ajusta a cada rodada.",
    "payoff_json": "Matriz de pagamentos JSON: {payoff}",
    "player_strategy": "Estratégia do jogador {name}:\n{strategy}",
    "no_extra_strategy": "(sem instruções extras)",
    "new_round": "Nova rodada. Escolha A ou B.",
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
    "cannot_open_reg": "Já não é possível abrir inscrição",
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
            "name": "Granite",
            "slug": "granite",
            "description": t("avatar_granite_desc"),
            "color": "#EE0000",
            "personality": t("avatar_granite_personality"),
        },
        {
            "name": "Llama",
            "slug": "llama",
            "description": t("avatar_llama_desc"),
            "color": "#F0AB00",
            "personality": t("avatar_llama_personality"),
        },
        {
            "name": "Mistral",
            "slug": "mistral",
            "description": t("avatar_mistral_desc"),
            "color": "#73C5C5",
            "personality": t("avatar_mistral_personality"),
        },
        {
            "name": "GLM",
            "slug": "glm",
            "description": t("avatar_glm_desc"),
            "color": "#7CC674",
            "personality": t("avatar_glm_personality"),
        },
        {
            "name": "Kimi",
            "slug": "kimi",
            "description": t("avatar_kimi_desc"),
            "color": "#A18FFF",
            "personality": t("avatar_kimi_personality"),
        },
    ]
