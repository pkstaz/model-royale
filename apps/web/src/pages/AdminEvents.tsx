import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, storage } from "../api";
import { tApiError, useT } from "../i18n";
import type { Avatar, EventInfo, Live } from "../types";
import { formatLabel, MatchCard, StatusPill } from "../ui";

const emptyEvent = {
  name: "",
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
  const { t } = useT();
  const token = storage.adminToken();
  const [events, setEvents] = useState<EventInfo[]>([]);
  const [avatars, setAvatars] = useState<Avatar[]>([]);
  const [form, setForm] = useState(emptyEvent);
  const [selected, setSelected] = useState<EventInfo | null>(null);
  const [live, setLive] = useState<Live | null>(null);
  const [error, setError] = useState("");

  const load = () => {
    api.get("/api/admin/events", token).then(setEvents).catch((err) => setError(tApiError(err.message, t)));
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
        { ...form, name: form.name || t("newEvent"), judge_avatar_id: form.judge_avatar_id || null },
        token,
      );
      setForm(emptyEvent);
      load();
      setSelected(created);
    } catch (err) {
      setError(tApiError((err as Error).message, t));
    }
  };

  const act = async (path: string) => {
    if (!selected) return;
    try {
      const updated = await api.post(path, {}, token);
      setSelected(updated);
      load();
    } catch (err) {
      setError(tApiError((err as Error).message, t));
    }
  };

  return (
    <>
      <p className="kicker">{t("maintainer")}</p>
      <h1>{t("events")}</h1>
      <p className="hint">{t("eventsHint")}</p>
      {error ? <p className="flash">{error}</p> : null}
      <div className="grid grid-2" style={{ marginTop: 16 }}>
        <form className="card" onSubmit={create}>
          <h3>{t("createEvent")}</h3>
          <label className="field">
            <span>{t("name")}</span>
            <input
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder={t("newEvent")}
            />
          </label>
          <label className="field">
            <span>{t("codeAuto")}</span>
            <input value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value.toUpperCase() })} />
          </label>
          <label className="field">
            <span>{t("format")}</span>
            <select value={form.format} onChange={(e) => setForm({ ...form, format: e.target.value })}>
              <option value="elimination">{t("fmtElimination")}</option>
              <option value="round_robin">{t("fmtRoundRobin")}</option>
              <option value="groups">{t("fmtGroups")}</option>
            </select>
          </label>
          <label className="field">
            <span>{t("roundsPerMatch")}</span>
            <input
              type="number"
              min={1}
              max={21}
              value={form.rounds_per_match}
              onChange={(e) => setForm({ ...form, rounds_per_match: Number(e.target.value) })}
            />
          </label>
          <label className="field">
            <span>{t("playerCap")}</span>
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
                <span>{t("groupSize")}</span>
                <input
                  type="number"
                  min={2}
                  value={form.group_size}
                  onChange={(e) => setForm({ ...form, group_size: Number(e.target.value) })}
                />
              </label>
              <label className="field">
                <span>{t("advancePerGroup")}</span>
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
            <span>{t("whatModelSees")}</span>
            <select value={form.reveal_mode} onChange={(e) => setForm({ ...form, reveal_mode: e.target.value })}>
              <option value="history">{t("revealHistory")}</option>
              <option value="blind">{t("revealBlind")}</option>
              <option value="open">{t("revealOpen")}</option>
            </select>
          </label>
          <label className="field">
            <span>{t("payoffMatrix")}</span>
            <select value={form.payoff_preset} onChange={(e) => setForm({ ...form, payoff_preset: e.target.value })}>
              <option value="royale">{t("presetRoyale")}</option>
              <option value="prisoner">{t("presetPrisoner")}</option>
              <option value="chicken">{t("presetChicken")}</option>
              <option value="stag">{t("presetStag")}</option>
            </select>
          </label>
          <label className="field">
            <span>{t("judgeOptional")}</span>
            <select
              value={form.judge_avatar_id}
              onChange={(e) => setForm({ ...form, judge_avatar_id: e.target.value })}
            >
              <option value="">{t("localParser")}</option>
              {avatars.map((avatar) => (
                <option key={avatar.id} value={avatar.id}>
                  {avatar.name}
                </option>
              ))}
            </select>
          </label>
          <button className="btn btn-primary" type="submit">
            {t("create")}
          </button>
        </form>
        <div className="card">
          <h3>{t("list")}</h3>
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
              <div className="hint">{formatLabel(item, t)}</div>
            </button>
          ))}
        </div>
      </div>
      {selected ? (
        <div className="card" style={{ marginTop: 16 }}>
          <h3>
            {selected.name} <span className="code">{selected.code}</span>
          </h3>
          <p className="hint">{formatLabel(selected, t)}</p>
          <div className="btn-row" style={{ margin: "12px 0" }}>
            <button className="btn btn-primary" onClick={() => act(`/api/admin/events/${selected.id}/open`)}>
              {t("openReg")}
            </button>
            <button className="btn" onClick={() => act(`/api/admin/events/${selected.id}/start`)}>
              {t("start")}
            </button>
            <button className="btn" onClick={() => act(`/api/admin/events/${selected.id}/reset`)}>
              {t("reset")}
            </button>
            <Link className="btn" to={`/tablero/${selected.code}`}>
              {t("viewBoard")}
            </Link>
          </div>
          {live ? (
            <>
              <p className="hint">
                {t("enrolledLive", {
                  players: live.players.length,
                  running: live.matches.filter((m) => m.status === "running").length,
                })}
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
