import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, storage } from "../api";
import { tApiError, useT } from "../i18n";
import type { Avatar, EventInfo, Player } from "../types";
import { formatLabel, Masthead, MatchCard, PayoffGrid, StandingsTable, StatusPill, useLive } from "../ui";

export default function Play() {
  const { t } = useT();
  const navigate = useNavigate();
  const token = storage.playerToken();
  const [tab, setTab] = useState<"arena" | "estrategia" | "historial">("estrategia");
  const [me, setMe] = useState<Player | null>(null);
  const [event, setEvent] = useState<EventInfo | null>(null);
  const [avatars, setAvatars] = useState<Avatar[]>([]);
  const [prompt, setPrompt] = useState("");
  const [avatarId, setAvatarId] = useState("");
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) {
      navigate("/");
      return;
    }
    api
      .get("/api/play/me", token)
      .then((body) => {
        setMe(body.player);
        setEvent(body.event);
        setAvatars(body.avatars);
        setPrompt(body.player.strategy_prompt || "");
        setAvatarId(body.player.avatar_id || "");
        if (body.event?.status && body.event.status !== "registration") {
          setTab("historial");
        }
      })
      .catch(() => {
        storage.clearPlayer();
        navigate("/");
      });
  }, [token, navigate]);

  const { live } = useLive(event?.code);
  const player = live?.players.find((item) => item.id === me?.id) || me;

  const save = async (eventSubmit: FormEvent) => {
    eventSubmit.preventDefault();
    setError("");
    setMsg("");
    try {
      const body = await api.patch("/api/play/me", { avatar_id: avatarId, strategy_prompt: prompt }, token);
      setMe(body);
      setMsg(t("saved"));
    } catch (err) {
      setError(tApiError((err as Error).message, t));
    }
  };

  if (!event || !player) {
    return (
      <div className="page">
        <Masthead />
        <p style={{ padding: 24 }}>{t("loading")}</p>
      </div>
    );
  }

  return (
    <div className="page play">
      <Masthead
        right={
          <nav>
            <StatusPill status={live?.event.status || event.status} />
            <Link to={`/tablero/${event.code}`}>{t("board")}</Link>
            <button
              className="btn-link"
              type="button"
              onClick={() => {
                storage.clearPlayer();
                navigate("/");
              }}
            >
              {t("exit")}
            </button>
          </nav>
        }
      />
      <div className="main" style={{ paddingBottom: 24 }}>
        {tab === "arena" ? (
          <Arena live={live} me={player.id} event={event} />
        ) : tab === "historial" ? (
          <History live={live} me={player.id} event={event} />
        ) : (
          <form onSubmit={save}>
            <p className="kicker">{event.name}</p>
            <h2>{t("yourStrategy")}</h2>
            <p className="hint">
              {formatLabel(event, t)}. {t("strategyHint")}
            </p>
            <div className="card" style={{ margin: "16px 0" }}>
              <strong>{t("rules")}</strong>
              <pre className="rules">{event.rules_prompt}</pre>
              <div style={{ marginTop: 12 }}>
                <PayoffGrid payoff={event.payoff} />
              </div>
            </div>
            <h3>{t("avatar")}</h3>
            <div className="avatar-grid">
              {avatars.map((avatar) => (
                <button
                  type="button"
                  key={avatar.id}
                  className={`avatar-tile ${avatarId === avatar.id ? "selected" : ""}`}
                  style={{ ["--tile" as string]: avatar.color }}
                  onClick={() => setAvatarId(avatar.id)}
                  disabled={player.locked}
                >
                  <div>
                    <span className="swatch" style={{ background: avatar.color }} />
                    <strong>{avatar.name}</strong>
                  </div>
                  <div className="hint">{avatar.description}</div>
                </button>
              ))}
            </div>
            <label className="field" style={{ marginTop: 16 }}>
              <span>{t("extraInstructions")}</span>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                disabled={player.locked}
                placeholder={t("extraPlaceholder")}
              />
            </label>
            {player.locked ? <p className="flash">{t("inBattle")}</p> : null}
            {error ? <p className="flash">{error}</p> : null}
            {msg ? <p className="okmsg">{msg}</p> : null}
            <button className="btn btn-primary" disabled={player.locked || !avatarId}>
              {t("save")}
            </button>
          </form>
        )}
      </div>
      <div className="tabbar">
        <button className={tab === "arena" ? "active" : ""} onClick={() => setTab("arena")} type="button">
          {t("arena")}
        </button>
        <button className={tab === "historial" ? "active" : ""} onClick={() => setTab("historial")} type="button">
          {t("history")}
        </button>
        <button className={tab === "estrategia" ? "active" : ""} onClick={() => setTab("estrategia")} type="button">
          {t("strategy")}
        </button>
      </div>
    </div>
  );
}

function Arena({
  live,
  me,
  event,
}: {
  live: ReturnType<typeof useLive>["live"];
  me: string;
  event: EventInfo;
}) {
  const { t } = useT();
  const mine = live?.matches.filter((item) => item.player_a_id === me || item.player_b_id === me) || [];
  const running = live?.matches.filter((item) => item.status === "running") || [];
  return (
    <>
      <p className="kicker">{event.code}</p>
      <h2>{t("arena")}</h2>
      <div className="grid grid-3" style={{ margin: "12px 0 18px" }}>
        <div className="card stat">
          <span>{t("players")}</span>
          <b>{live?.players.length || 0}</b>
        </div>
        <div className="card stat">
          <span>{t("inCombat")}</span>
          <b>{running.length}</b>
        </div>
        <div className="card stat">
          <span>{t("yourRank")}</span>
          <b>{live?.standings.find((row) => row.player_id === me)?.rank || "—"}</b>
        </div>
      </div>
      <h3>{t("standings")}</h3>
      <div className="card" style={{ marginBottom: 16 }}>
        <StandingsTable standings={live?.standings || []} me={me} />
      </div>
      <h3>{t("yourMatches")}</h3>
      <div className="grid">
        {mine.length ? mine.map((match) => <MatchCard key={match.id} match={match} />) : <p className="hint">{t("noPairings")}</p>}
      </div>
      <h3 style={{ marginTop: 18 }}>{t("liveNow")}</h3>
      <div className="grid">
        {running.map((match) => (
          <MatchCard key={match.id} match={match} />
        ))}
      </div>
    </>
  );
}

function History({
  live,
  me,
  event,
}: {
  live: ReturnType<typeof useLive>["live"];
  me: string;
  event: EventInfo;
}) {
  const { t } = useT();
  const mine = live?.matches.filter((item) => item.player_a_id === me || item.player_b_id === me) || [];
  const standing = live?.standings.find((row) => row.player_id === me);
  const won = mine.filter((item) => item.winner_id === me && item.status === "completed").length;
  return (
    <>
      <p className="kicker">{event.code}</p>
      <h2>{t("yourHistory")}</h2>
      <p className="hint">{t("historyHint")}</p>
      <div className="grid grid-3" style={{ margin: "12px 0 18px" }}>
        <div className="card stat">
          <span>{t("rank")}</span>
          <b>{standing?.rank || "—"}</b>
        </div>
        <div className="card stat">
          <span>{t("points")}</span>
          <b>{standing?.points ?? 0}</b>
        </div>
        <div className="card stat">
          <span>{t("wins")}</span>
          <b>{won}</b>
        </div>
      </div>
      <div className="grid">
        {mine.length ? mine.map((match) => <MatchCard key={match.id} match={match} />) : <p className="hint">{t("noMatches")}</p>}
      </div>
    </>
  );
}
