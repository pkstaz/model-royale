import { useParams } from "react-router-dom";
import { formatLabel, Masthead, MatchCard, PayoffGrid, StandingsTable, StatusPill, useLive } from "../ui";

export default function Board() {
  const { code = "TALLER" } = useParams();
  const { live, error } = useLive(code);
  const event = live?.event;
  const running = live?.matches.filter((item) => item.status === "running") || [];
  const done = live?.matches.filter((item) => item.status === "completed") || [];
  const waiting = live?.players.filter((item) => !item.avatar_id) || [];

  return (
    <div className="page">
      <Masthead
        right={
          <nav>
            {event ? <StatusPill status={event.status} /> : null}
            <span className="code">{code}</span>
          </nav>
        }
      />
      <div className="main">
        {error ? <p className="flash">{error}</p> : null}
        {!event ? (
          <p className="hint">Esperando evento {code}…</p>
        ) : (
          <>
            <p className="kicker">Tablero central</p>
            <h1>{event.name}</h1>
            <p className="hint">{formatLabel(event)}</p>
            <div className="grid grid-3" style={{ margin: "16px 0" }}>
              <div className="card stat">
                <span>Inscritos</span>
                <b>
                  {live.players.length}/{event.max_players}
                </b>
              </div>
              <div className="card stat">
                <span>Avanzan</span>
                <b>{live.players.filter((item) => !item.eliminated).length}</b>
              </div>
              <div className="card stat">
                <span>Combates vivos</span>
                <b>{running.length}</b>
              </div>
            </div>
            <div className="grid grid-2">
              <div className="card">
                <h3>Inscritos</h3>
                <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                  {live.players.map((player) => (
                    <li key={player.id} style={{ padding: "8px 0", borderBottom: "1px solid var(--bg-400)" }}>
                      <span className="swatch" style={{ background: player.avatar?.color || "#444" }} />
                      <strong>{player.display_name}</strong>
                      <span className="hint"> · {player.avatar?.name || "sin avatar"}</span>
                      {player.locked ? <StatusPill status="running" /> : null}
                      {player.eliminated ? <span className="hint"> · fuera</span> : null}
                      {player.group_label ? <span className="hint"> · grupo {player.group_label}</span> : null}
                    </li>
                  ))}
                </ul>
                {waiting.length ? <p className="hint">{waiting.length} aún eligen avatar.</p> : null}
              </div>
              <div className="card">
                <h3>Matriz</h3>
                <PayoffGrid payoff={event.payoff} />
              </div>
            </div>
            <div className="card" style={{ margin: "16px 0" }}>
              <h3>Quién avanza</h3>
              <StandingsTable standings={live.standings} />
            </div>
            <h3>Batallas</h3>
            <div className="grid grid-2">
              {running.map((match) => (
                <MatchCard key={match.id} match={match} />
              ))}
              {done.map((match) => (
                <MatchCard key={match.id} match={match} />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
