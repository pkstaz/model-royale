import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
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
  const map: Record<string, string> = {
    draft: "warn",
    registration: "info",
    running: "live",
    completed: "ok",
    pending: "warn",
    bye: "info",
  };
  const labels: Record<string, string> = {
    draft: "Borrador",
    registration: "Inscripción",
    running: "En vivo",
    completed: "Cerrado",
    pending: "Pendiente",
    bye: "Bye",
  };
  return <span className={`pill ${map[status] || ""}`}>{labels[status] || status}</span>;
}

export function PayoffGrid({ payoff }: { payoff: Record<string, number[]> }) {
  const cell = (key: string) => (payoff?.[key] || [0, 0]).join(" / ");
  return (
    <div className="payoff">
      <div />
      <div>Oponente A</div>
      <div>Oponente B</div>
      <div>Tú A</div>
      <div>{cell("AA")}</div>
      <div>{cell("AB")}</div>
      <div>Tú B</div>
      <div>{cell("BA")}</div>
      <div>{cell("BB")}</div>
    </div>
  );
}

export function formatLabel(event: EventInfo) {
  const formats: Record<string, string> = {
    round_robin: "Todos contra todos",
    groups: "Grupos + eliminación",
    elimination: "Eliminación directa",
  };
  const reveal: Record<string, string> = {
    blind: "Ciego",
    history: "Con historial",
    open: "Abierto",
  };
  return `${formats[event.format] || event.format} · ${event.rounds_per_match} rondas · ${reveal[event.reveal_mode] || event.reveal_mode}`;
}

export function StandingsTable({
  standings,
  me,
}: {
  standings: Standing[];
  me?: string;
}) {
  return (
    <table className="table">
      <thead>
        <tr>
          <th>#</th>
          <th>Jugador</th>
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

export function MatchCard({ match }: { match: Match }) {
  return (
    <article className={`match ${match.status}`}>
      <div className="fighters">
        <div className={`fighter ${match.winner_id === match.player_a_id ? "win" : ""}`}>
          <div>{match.player_a_name || "Bye"}</div>
          <div className="score">{match.score_a}</div>
        </div>
        <StatusPill status={match.status} />
        <div className={`fighter ${match.winner_id === match.player_b_id ? "win" : ""}`} style={{ textAlign: "right" }}>
          <div>{match.player_b_name || "Bye"}</div>
          <div className="score">{match.score_b}</div>
        </div>
      </div>
      <div className="hint" style={{ marginTop: 6 }}>
        {match.stage} {match.group_label ? `· grupo ${match.group_label}` : ""} · oleada {match.wave}
      </div>
      {match.rounds?.length ? (
        <div className="rounds">
          {match.rounds.map((round) => (
            <div className="chip" key={round.id} title={`${round.rationale_a} vs ${round.rationale_b}`}>
              R{round.index} <span className="a">{round.move_a}</span>
              {round.points_a}–{round.points_b}
              <span className="b">{round.move_b}</span>
            </div>
          ))}
        </div>
      ) : null}
    </article>
  );
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
          const payload = JSON.parse(event.data) as Live;
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
