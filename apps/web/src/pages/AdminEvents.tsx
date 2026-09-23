import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, storage } from "../api";
import type { Avatar, EventInfo, Live } from "../types";
import { formatLabel, MatchCard, StatusPill } from "../ui";

const emptyEvent = {
  name: "Nuevo evento",
  code: "",
  format: "elimination",
  rounds_per_match: 5,
  max_players: 16,
  min_players: 2,
  group_size: 4,
  advance_per_group: 2,
  reveal_mode: "history",
  payoff_preset: "royale",
  judge_avatar_id: "",
  invalid_move_policy: "default_a",
  auto_advance: true,
};

export default function AdminEvents() {
  const token = storage.adminToken();
  const [events, setEvents] = useState<EventInfo[]>([]);
  const [avatars, setAvatars] = useState<Avatar[]>([]);
  const [form, setForm] = useState(emptyEvent);
  const [selected, setSelected] = useState<EventInfo | null>(null);
  const [live, setLive] = useState<Live | null>(null);
  const [error, setError] = useState("");

  const load = () => {
    api.get("/api/admin/events", token).then(setEvents).catch((err) => setError(err.message));
    api.get("/api/admin/avatars", token).then(setAvatars).catch(() => undefined);
  };

  useEffect(() => {
    load();
  }, []);

  useEffect(() => {
    if (!selected) return;
    api.get(`/api/admin/events/${selected.id}/live`, token).then(setLive).catch(() => undefined);
    const timer = setInterval(() => {
      api.get(`/api/admin/events/${selected.id}/live`, token).then(setLive).catch(() => undefined);
    }, 2500);
    return () => clearInterval(timer);
  }, [selected, token]);

  const create = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    try {
      const created = await api.post(
        "/api/admin/events",
        { ...form, judge_avatar_id: form.judge_avatar_id || null },
        token,
      );
      setForm(emptyEvent);
      load();
      setSelected(created);
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const act = async (path: string) => {
    if (!selected) return;
    try {
      const updated = await api.post(path, {}, token);
      setSelected(updated);
      load();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <>
      <p className="kicker">Mantenedor</p>
      <h1>Eventos</h1>
      <p className="hint">Formato, rondas y revelado se fijan antes de largar. Los modelos no se despliegan aquí.</p>
      {error ? <p className="flash">{error}</p> : null}
      <div className="grid grid-2" style={{ marginTop: 16 }}>
        <form className="card" onSubmit={create}>
          <h3>Crear evento</h3>
          <label className="field">
            <span>Nombre</span>
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </label>
          <label className="field">
            <span>Código (vacío = automático)</span>
            <input value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value.toUpperCase() })} />
          </label>
          <label className="field">
            <span>Formato</span>
            <select value={form.format} onChange={(e) => setForm({ ...form, format: e.target.value })}>
              <option value="elimination">Eliminación directa</option>
              <option value="round_robin">Todos contra todos</option>
              <option value="groups">Grupos + eliminación</option>
            </select>
          </label>
          <label className="field">
            <span>Rondas por combate</span>
            <input
              type="number"
              min={1}
              max={21}
              value={form.rounds_per_match}
              onChange={(e) => setForm({ ...form, rounds_per_match: Number(e.target.value) })}
            />
          </label>
          <label className="field">
            <span>Cupo de jugadores</span>
            <input
              type="number"
              min={2}
              value={form.max_players}
              onChange={(e) => setForm({ ...form, max_players: Number(e.target.value) })}
            />
          </label>
          {form.format === "groups" ? (
            <>
              <label className="field">
                <span>Tamaño de grupo</span>
                <input
                  type="number"
                  min={2}
                  value={form.group_size}
                  onChange={(e) => setForm({ ...form, group_size: Number(e.target.value) })}
                />
              </label>
              <label className="field">
                <span>Avanzan por grupo</span>
                <input
                  type="number"
                  min={1}
                  value={form.advance_per_group}
                  onChange={(e) => setForm({ ...form, advance_per_group: Number(e.target.value) })}
                />
              </label>
            </>
          ) : null}
          <label className="field">
            <span>Qué ve el modelo</span>
            <select value={form.reveal_mode} onChange={(e) => setForm({ ...form, reveal_mode: e.target.value })}>
              <option value="history">Historial (recomendado)</option>
              <option value="blind">Ciego</option>
              <option value="open">Abierto (el segundo ve la jugada actual)</option>
            </select>
          </label>
          <label className="field">
            <span>Matriz de pagos</span>
            <select value={form.payoff_preset} onChange={(e) => setForm({ ...form, payoff_preset: e.target.value })}>
              <option value="royale">Royale (−2/−2, +5/0, +2/+2)</option>
              <option value="prisoner">Dilema del prisionero</option>
              <option value="chicken">Gallina</option>
              <option value="stag">Caza del ciervo</option>
            </select>
          </label>
          <label className="field">
            <span>Juez (opcional)</span>
            <select
              value={form.judge_avatar_id}
              onChange={(e) => setForm({ ...form, judge_avatar_id: e.target.value })}
            >
              <option value="">Parser local</option>
              {avatars.map((avatar) => (
                <option key={avatar.id} value={avatar.id}>
                  {avatar.name}
                </option>
              ))}
            </select>
          </label>
          <button className="btn btn-primary" type="submit">
            Crear
          </button>
        </form>
        <div className="card">
          <h3>Lista</h3>
          {events.map((item) => (
            <button
              key={item.id}
              className="nav"
              style={{
                display: "block",
                width: "100%",
                textAlign: "left",
                background: selected?.id === item.id ? "var(--bg-400)" : "none",
                border: 0,
                color: "inherit",
                padding: "10px 0",
                cursor: "pointer",
              }}
              onClick={() => setSelected(item)}
              type="button"
            >
              <strong>{item.name}</strong> <span className="code">{item.code}</span> <StatusPill status={item.status} />
              <div className="hint">{formatLabel(item)}</div>
            </button>
          ))}
        </div>
      </div>
      {selected ? (
        <div className="card" style={{ marginTop: 16 }}>
          <h3>
            {selected.name} <span className="code">{selected.code}</span>
          </h3>
          <p className="hint">{formatLabel(selected)}</p>
          <div className="btn-row" style={{ margin: "12px 0" }}>
            <button className="btn btn-primary" onClick={() => act(`/api/admin/events/${selected.id}/open`)}>
              Abrir inscripción
            </button>
            <button className="btn" onClick={() => act(`/api/admin/events/${selected.id}/start`)}>
              Largar
            </button>
            <button className="btn" onClick={() => act(`/api/admin/events/${selected.id}/reset`)}>
              Reset
            </button>
            <Link className="btn" to={`/tablero/${selected.code}`}>
              Ver tablero
            </Link>
          </div>
          {live ? (
            <>
              <p className="hint">
                {live.players.length} inscritos · {live.matches.filter((m) => m.status === "running").length} en combate
              </p>
              <div className="grid grid-2">
                {live.matches.slice(0, 6).map((match) => (
                  <MatchCard key={match.id} match={match} />
                ))}
              </div>
            </>
          ) : null}
        </div>
      ) : null}
    </>
  );
}
