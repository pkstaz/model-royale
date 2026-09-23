import { useParams } from "react-router-dom";
import { useT } from "../i18n";
import { formatLabel, Masthead, MatchCard, PayoffGrid, StandingsTable, StatusPill, useLive } from "../ui";

export default function Board() {
  const { t } = useT();
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
          <p className="hint">{t("waitingEvent", { code })}</p>
        ) : (
          <>
            <p className="kicker">{t("centralBoard")}</p>
            <h1>{event.name}</h1>
            <p className="hint">{formatLabel(event, t)}</p>
            <div className="grid grid-3" style={{ margin: "16px 0" }}>
              <div className="card stat">
                <span>{t("registered")}</span>
                <b>
                  {live.players.length}/{event.max_players}
                </b>
              </div>
              <div className="card stat">
                <span>{t("advancing")}</span>
                <b>{live.players.filter((item) => !item.eliminated).length}</b>
              </div>
              <div className="card stat">
                <span>{t("liveMatches")}</span>
                <b>{running.length}</b>
              </div>
            </div>
            <div className="grid grid-2">
              <div className="card">
                <h3>{t("registered")}</h3>
                <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                  {live.players.map((player) => (
                    <li key={player.id} style={{ padding: "8px 0", borderBottom: "1px solid var(--bg-400)" }}>
                      <span className="swatch" style={{ background: player.avatar?.color || "#444" }} />
                      <strong>{player.display_name}</strong>
                      <span className="hint"> · {player.avatar?.name || t("noAvatar")}</span>
                      {player.locked ? <StatusPill status="running" /> : null}
                      {player.eliminated ? <span className="hint"> · {t("out")}</span> : null}
                      {player.group_label ? (
                        <span className="hint">
                          {" "}
                          · {t("group")} {player.group_label}
                        </span>
                      ) : null}
                    </li>
                  ))}
                </ul>
                {waiting.length ? <p className="hint">{t("stillPicking", { n: waiting.length })}</p> : null}
              </div>
              <div className="card">
                <h3>{t("matrix")}</h3>
                <PayoffGrid payoff={event.payoff} />
              </div>
            </div>
            <div className="card" style={{ margin: "16px 0" }}>
              <h3>{t("whoAdvances")}</h3>
              <StandingsTable standings={live.standings} />
            </div>
            <h3>{t("battles")}</h3>
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
