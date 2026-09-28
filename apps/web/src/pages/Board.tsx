import { Link, useParams } from "react-router-dom";
import { storage } from "../api";
import { useT } from "../i18n";
import type { Live } from "../types";
import { formatLabel, Masthead, MatchesByRound, PayoffGrid, StandingsTable, StatusPill, useLive } from "../ui";

export function BoardBody({
  code,
  live,
  error,
}: {
  code: string;
  live: Live | null;
  error: string;
}) {
  const { t } = useT();
  const event = live?.event;
  const running = live?.matches.filter((item) => item.status === "running") || [];
  const waiting = live?.players.filter((item) => !item.avatar_id) || [];
  const champion = event?.status === "completed" ? live?.standings.find((row) => !row.eliminated) || live?.standings[0] : null;
  const elim = live?.matches.filter((item) => item.stage === "elimination") || [];
  const league = live?.matches.filter((item) => item.stage !== "elimination") || [];

  if (error) return <p className="flash">{error}</p>;
  if (!event || !live) return <p className="hint">{t("waitingEvent", { code })}</p>;

  return (
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
          <h3>{t("payoffMatrix")}</h3>
          <PayoffGrid payoff={event.payoff} />
        </div>
      </div>
      <div className="card" style={{ margin: "16px 0" }}>
        <h3>{t("whoAdvances")}</h3>
        {champion ? (
          <p className="champion">
            {t("champion")}: <strong>{champion.display_name}</strong>
          </p>
        ) : null}
        <StandingsTable standings={live.standings} />
      </div>
      {league.length ? (
        <>
          <h3>{event.format === "groups" ? t("groupStage") : t("battles")}</h3>
          <MatchesByRound matches={league} format={event.format} />
        </>
      ) : null}
      {elim.length ? (
        <>
          <h3>{t("fmtElimination")}</h3>
          <MatchesByRound matches={elim} format="elimination" tree />
        </>
      ) : null}
      {!league.length && !elim.length ? <p className="hint">{t("noPairings")}</p> : null}
    </>
  );
}

export default function Board() {
  const { t } = useT();
  const { code = "TALLER" } = useParams();
  const { live, error } = useLive(code);
  const admin = Boolean(storage.adminToken());

  return (
    <div className="page">
      <Masthead
        right={
          <nav>
            {live?.event ? <StatusPill status={live.event.status} /> : null}
            <span className="code">{code}</span>
            {admin ? <Link to="/admin">{t("admin")}</Link> : null}
          </nav>
        }
      />
      <div className="main board-page">
        <BoardBody code={code} live={live} error={error} />
      </div>
    </div>
  );
}
