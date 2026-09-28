import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { useT, type MsgKey } from "./i18n";
import type { EventInfo, Live, Match, Standing } from "./types";

export function Mark() {
  return <span className="mark">MR</span>;
}

export function Masthead({ right }: { right?: ReactNode }) {
  return (
    <header className="masthead">
      <Link to="/" className="brand">
        <Mark />
        Model Royale
      </Link>
      {right}
    </header>
  );
}

export function StatusPill({ status }: { status: string }) {
  const { t } = useT();
  const map: Record<string, string> = {
    draft: "warn",
    registration: "info",
    running: "live",
    completed: "ok",
    pending: "warn",
    queued: "info",
    bye: "info",
  };
  const labels: Record<string, MsgKey> = {
    draft: "statusDraft",
    registration: "statusRegistration",
    running: "statusRunning",
    completed: "statusCompleted",
    pending: "statusPending",
    queued: "statusQueued",
    bye: "statusBye",
  };
  const key = labels[status];
  return <span className={`pill ${map[status] || ""}`}>{key ? t(key) : status}</span>;
}

export const PAYOFF_PRESETS: Record<string, Record<string, number[]>> = {
  royale: { AA: [-2, -2], AB: [5, 0], BA: [0, 5], BB: [2, 2] },
  prisoner: { AA: [1, 1], AB: [5, 0], BA: [0, 5], BB: [3, 3] },
  chicken: { AA: [-5, -5], AB: [2, -1], BA: [-1, 2], BB: [1, 1] },
  stag: { AA: [1, 1], AB: [1, 0], BA: [0, 1], BB: [4, 4] },
};

export function PayoffGrid({ payoff }: { payoff: Record<string, number[]> }) {
  const { t } = useT();
  const cell = (key: string) => (payoff?.[key] || [0, 0]).join(" / ");
  return (
    <>
      <div className="payoff">
        <div />
        <div>{t("opponentA")}</div>
        <div>{t("opponentB")}</div>
        <div>{t("youA")}</div>
        <div>{cell("AA")}</div>
        <div>{cell("AB")}</div>
        <div>{t("youB")}</div>
        <div>{cell("BA")}</div>
        <div>{cell("BB")}</div>
      </div>
      <p className="hint">{t("sameMoveHint")}</p>
    </>
  );
}

export function formatLabel(event: EventInfo, t: (key: MsgKey, vars?: Record<string, string | number>) => string) {
  const formats: Record<string, MsgKey> = {
    round_robin: "fmtRoundRobin",
    groups: "fmtGroups",
    elimination: "fmtElimination",
  };
  const reveal: Record<string, MsgKey> = {
    blind: "revealBlindShort",
    history: "revealHistoryShort",
    open: "revealOpenShort",
  };
  return t("fmtLabel", {
    format: t(formats[event.format] || "fmtElimination"),
    rounds: event.rounds_per_match,
    reveal: t(reveal[event.reveal_mode] || "revealHistoryShort"),
  });
}

export function StandingsTable({
  standings,
  me,
}: {
  standings: Standing[];
  me?: string;
}) {
  const { t } = useT();
  return (
    <table className="table">
      <thead>
        <tr>
          <th>#</th>
          <th>{t("player")}</th>
          <th>Pts</th>
          <th>G</th>
          <th>P</th>
        </tr>
      </thead>
      <tbody>
        {standings.map((row) => (
          <tr key={row.player_id} className={`${row.player_id === me ? "me" : ""} ${row.eliminated ? "out" : ""}`}>
            <td>{row.rank}</td>
            <td>
              <span className="swatch" style={{ background: row.avatar_color }} />
              {row.display_name}
              {row.group_label ? ` · ${row.group_label}` : ""}
            </td>
            <td>{row.points}</td>
            <td>{row.wins}</td>
            <td>{row.losses}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function roundIndex(match: Match) {
  return match.wave < 1 ? 1 : match.wave;
}

export function groupByRound(matches: Match[]) {
  const map = new Map<number, Match[]>();
  for (const match of matches) {
    const wave = roundIndex(match);
    const list = map.get(wave) || [];
    list.push(match);
    map.set(wave, list);
  }
  return [...map.entries()]
    .sort((a, b) => a[0] - b[0])
    .map(([wave, items]) => ({
      wave,
      matches: items.slice().sort((a, b) => a.bracket_slot - b.bracket_slot),
    }));
}

export function roundTitle(
  wave: number,
  items: Match[],
  format: string,
  t: (key: MsgKey, vars?: Record<string, string | number>) => string,
) {
  const stage = items[0]?.stage;
  if (stage === "elimination" || format === "elimination") {
    const real = items.filter((item) => item.player_b_id);
    const n = real.length || items.length;
    if (n === 1) return t("roundFinal");
    if (n === 2) return t("roundSemis");
    if (n === 4) return t("roundQuarters");
    if (n === 8) return t("roundOf", { n: 16 });
    if (n === 16) return t("roundOf", { n: 32 });
  }
  if (stage === "groups") return `${t("roundN", { n: wave })} · ${t("groupStage")}`;
  return t("roundN", { n: wave });
}

export function MatchCard({
  match,
  compact,
  showRound = true,
}: {
  match: Match;
  compact?: boolean;
  showRound?: boolean;
}) {
  const { t } = useT();
  const live = match.status === "running";
  const pillStatus = !match.player_b_id && match.status === "completed" ? "bye" : match.status;
  const wentOt = Boolean(match.rounds?.some((item) => item.overtime));
  const hint = [
    match.group_label ? `${t("group")} ${match.group_label}` : "",
    showRound ? t("roundN", { n: roundIndex(match) }) : "",
    wentOt ? t("suddenDeath") : "",
  ]
    .filter(Boolean)
    .join(" · ");
  return (
    <article className={`match ${match.status}${compact ? " compact" : ""}`}>
      <div className="fighters">
        <div className={`fighter${live ? " thinking" : ""}${match.winner_id === match.player_a_id ? " win" : ""}`}>
          <div className="fighter-name">
            {match.player_a_name || t("statusBye")}
            {live ? <span className="dots" aria-hidden><i /><i /><i /></span> : null}
          </div>
          <div className="score">{match.score_a}</div>
        </div>
        <StatusPill status={pillStatus} />
        <div
          className={`fighter${live ? " thinking" : ""}${match.winner_id === match.player_b_id ? " win" : ""}`}
          style={{ textAlign: "right" }}
        >
          <div className="fighter-name" style={{ justifyContent: "flex-end" }}>
            {live ? <span className="dots" aria-hidden><i /><i /><i /></span> : null}
            {match.player_b_name || t("statusBye")}
          </div>
          <div className="score">{match.score_b}</div>
        </div>
      </div>
      {hint ? <div className="hint" style={{ marginTop: 6 }}>{hint}</div> : null}
      {live ? <div className="live-bar" /> : null}
      {!compact && match.rounds?.length ? (
        <div className="rounds">
          {match.rounds.map((round) => (
            <div className="chip" key={round.id} title={`${round.rationale_a} vs ${round.rationale_b}`}>
              {round.overtime ? t("otN", { n: round.index }) : `R${round.index}`}{" "}
              <span className="a">{round.move_a}</span>
              {round.points_a}–{round.points_b}
              <span className="b">{round.move_b}</span>
            </div>
          ))}
        </div>
      ) : null}
    </article>
  );
}

export function MatchesByRound({
  matches,
  format,
  tree,
}: {
  matches: Match[];
  format: string;
  tree?: boolean;
}) {
  const { t } = useT();
  const groups = groupByRound(matches);
  if (!groups.length) return <p className="hint">{t("noPairings")}</p>;
  if (tree || format === "elimination") {
    const currentWave = currentRoundWave(groups);
    return (
      <div className="bracket">
        {groups.map(({ wave, matches: items }) => (
          <div className={`bracket-round${wave === currentWave ? " current" : ""}`} key={wave}>
            <h3>
              {roundTitle(wave, items, format, t)}
              {wave === currentWave ? <span>{t("roundNow")}</span> : null}
            </h3>
            <div className="bracket-col">
              {items.map((match) => (
                <div className="bracket-slot" key={match.id}>
                  <MatchCard match={match} compact showRound={false} />
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  }

  const currentWave = currentRoundWave(groups);
  const previousWave = [...groups].reverse().find((item) => item.wave < currentWave)?.wave;
  const stacked = [...groups].sort((a, b) => b.wave - a.wave);
  return (
    <div className="round-stack">
      {stacked.map(({ wave, matches: items }) => (
        <section key={wave} className={`round-block${wave === currentWave ? " current" : ""}`}>
          <h3 className="round-head">
            {roundTitle(wave, items, format, t)}
            {wave === currentWave ? <span className="hint">{t("roundNow")}</span> : wave === previousWave ? <span className="hint">{t("roundPrev")}</span> : null}
          </h3>
          <div className="grid grid-2">
            {items.map((match) => (
              <MatchCard key={match.id} match={match} showRound={false} />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}

function currentRoundWave(groups: { wave: number; matches: Match[] }[]) {
  const active = groups.filter((group) =>
    group.matches.some((item) => item.status === "running" || item.status === "pending"),
  );
  if (active.length) return Math.max(...active.map((item) => item.wave));
  return Math.max(...groups.map((item) => item.wave), 1);
}

export function useLive(code?: string) {
  const [live, setLive] = useState<Live | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!code) return;
    let source: EventSource | null = null;
    let cancelled = false;
    fetch(`/api/public/events/${code}`)
      .then((res) => res.json())
      .then((body) => {
        if (cancelled) return;
        if (body.detail) throw new Error(body.detail);
        setLive(body.live);
        source = new EventSource(`/api/public/events/${code}/stream`);
        source.onmessage = (event) => {
          const payload = JSON.parse(event.data) as Live & { type?: string };
          if (payload.type === "thought") return;
          setLive(payload);
        };
      })
      .catch((err: Error) => setError(err.message));
    return () => {
      cancelled = true;
      source?.close();
    };
  }, [code]);

  return { live, error };
}
