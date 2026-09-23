import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, storage } from "../api";
import type { Avatar, EventInfo, Player } from "../types";
import { formatLabel, Masthead, MatchCard, PayoffGrid, StandingsTable, StatusPill, useLive } from "../ui";

export default function Play() {
  const navigate = useNavigate();
  const token = storage.playerToken();
  const [tab, setTab] = useState<"arena" | "estrategia">("estrategia");
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
      setMsg("Estrategia guardada");
    } catch (err) {
      setError((err as Error).message);
    }
  };

  if (!event || !player) {
    return (
      <div className="page">
        <Masthead />
        <p style={{ padding: 24 }}>Cargando…</p>
      </div>
    );
  }

  return (
    <div className="page play">
      <Masthead
        right={
          <nav>
            <StatusPill status={live?.event.status || event.status} />
            <Link to={`/tablero/${event.code}`}>Tablero</Link>
          </nav>
        }
      />
      <div className="main" style={{ paddingBottom: 24 }}>
        {tab === "arena" ? (
          <Arena live={live} me={player.id} event={event} />
        ) : (
          <form onSubmit={save}>
            <p className="kicker">{event.name}</p>
            <h2>Tu estrategia</h2>
            <p className="hint">
              {formatLabel(event)}. El system prompt no se edita. Tus instrucciones sí, excepto en combate.
            </p>
            <div className="card" style={{ margin: "16px 0" }}>
              <strong>Reglas (system)</strong>
              <pre className="rules">{event.rules_prompt}</pre>
              <div style={{ marginTop: 12 }}>
                <PayoffGrid payoff={event.payoff} />
              </div>
            </div>
            <h3>Avatar</h3>
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
              <span>Instrucciones extra</span>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                disabled={player.locked}
                placeholder="Ej: tit-for-tat, empiezo en B, si me traicionan dos veces paso a A."
              />
            </label>
            {player.locked ? (
              <p className="flash">Estás en combate. La estrategia se desbloquea al terminar.</p>
            ) : null}
            {error ? <p className="flash">{error}</p> : null}
            {msg ? <p className="okmsg">{msg}</p> : null}
            <button className="btn btn-primary" disabled={player.locked || !avatarId}>
              Guardar
            </button>
          </form>
        )}
      </div>
      <div className="tabbar">
        <button className={tab === "arena" ? "active" : ""} onClick={() => setTab("arena")} type="button">
          Arena
        </button>
        <button className={tab === "estrategia" ? "active" : ""} onClick={() => setTab("estrategia")} type="button">
          Estrategia
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
  const mine = live?.matches.filter((item) => item.player_a_id === me || item.player_b_id === me) || [];
  const running = live?.matches.filter((item) => item.status === "running") || [];
  return (
    <>
      <p className="kicker">{event.code}</p>
      <h2>Arena</h2>
      <div className="grid grid-3" style={{ margin: "12px 0 18px" }}>
        <div className="card stat">
          <span>Jugadores</span>
          <b>{live?.players.length || 0}</b>
        </div>
        <div className="card stat">
          <span>En combate</span>
          <b>{running.length}</b>
        </div>
        <div className="card stat">
          <span>Tu puesto</span>
          <b>{live?.standings.find((row) => row.player_id === me)?.rank || "—"}</b>
        </div>
      </div>
      <h3>Clasificación</h3>
      <div className="card" style={{ marginBottom: 16 }}>
        <StandingsTable standings={live?.standings || []} me={me} />
      </div>
      <h3>Tus combates</h3>
      <div className="grid">
        {mine.length ? mine.map((match) => <MatchCard key={match.id} match={match} />) : <p className="hint">Aún no hay emparejamientos.</p>}
      </div>
      <h3 style={{ marginTop: 18 }}>En vivo</h3>
      <div className="grid">
        {running.map((match) => (
          <MatchCard key={match.id} match={match} />
        ))}
      </div>
    </>
  );
}
