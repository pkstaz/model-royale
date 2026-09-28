import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, storage } from "../api";
import { tApiError, useT } from "../i18n";
import type { Avatar, EventInfo, Live } from "../types";
import { formatLabel, MatchCard, PayoffGrid, PAYOFF_PRESETS, StatusPill } from "../ui";

function formFromEvent(item: EventInfo) {
  return {
    name: item.name,
    code: item.code,
    format: item.format,
    rounds_per_match: item.rounds_per_match,
    max_players: item.max_players,
    min_players: item.min_players,
    group_size: item.group_size,
    advance_per_group: item.advance_per_group,
    reveal_mode: item.reveal_mode,
    payoff_preset: item.payoff_preset || "royale",
    judge_avatar_id: item.judge_avatar_id || "",
    invalid_move_policy: item.invalid_move_policy,
    auto_advance: item.auto_advance,
  };
}

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
  const [ok, setOk] = useState("");

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

  const save = async (event?: FormEvent) => {
    event?.preventDefault();
    setError("");
    setOk("");
    try {
      const payload = { ...form, name: form.name || t("newEvent"), judge_avatar_id: form.judge_avatar_id || null };
      const saved = selected
        ? await api.patch(`/api/admin/events/${selected.id}`, payload, token)
        : await api.post("/api/admin/events", payload, token);
      setSelected(saved);
      setForm(formFromEvent(saved));
      setOk(t("eventSaved"));
      load();
    } catch (err) {
      setError(tApiError((err as Error).message, t));
    }
  };

  const pick = (item: EventInfo) => {
    setSelected(item);
    setForm(formFromEvent(item));
    setError("");
    setOk("");
  };

  const startBlank = () => {
    setSelected(null);
    setLive(null);
    setForm(emptyEvent);
    setError("");
    setOk("");
  };

  const act = async (path: string, body: Record<string, unknown> = {}) => {
    if (!selected) return;
    try {
      const updated = await api.post(path, body, token);
      setSelected(updated);
      load();
    } catch (err) {
      setError(tApiError((err as Error).message, t));
    }
  };

  const paramsLocked = selected?.status === "running";
  const canStart = selected && (selected.status === "draft" || selected.status === "registration");
  const roundOpen = Boolean(
    live?.matches.some((item) => item.status === "pending" || item.status === "running"),
  );
  const hasQueued = Boolean(live?.matches.some((item) => item.status === "queued"));
  const moreRounds =
    selected?.status === "running" &&
    !roundOpen &&
    (hasQueued || (selected.format !== "round_robin" && (live?.players.filter((p) => !p.eliminated).length || 0) > 1));

  return (
    <>
      <p className="kicker">{t("maintainer")}</p>
      <h1>{t("events")}</h1>
      <p className="hint">{t("eventsHint")}</p>
      {error ? <p className="flash">{error}</p> : null}
      {ok ? <p className="okmsg">{ok}</p> : null}
      <div className="grid grid-2" style={{ marginTop: 16 }}>
        <form className="card" onSubmit={save} noValidate>
          <h3>{selected ? t("editEvent") : t("createEvent")}</h3>
          <label className="field">
            <span>{t("name")}</span>
            <input
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder={t("newEvent")}
              disabled={Boolean(selected)}
            />
          </label>
          {selected ? <p className="hint">{t("nameLocked")}</p> : null}
          <label className="field">
            <span>{t("codeAuto")}</span>
            <input
              value={form.code}
              maxLength={24}
              onChange={(e) => setForm({ ...form, code: e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, "") })}
            />
          </label>
          <label className="field">
            <span>{t("format")}</span>
            <select value={form.format} disabled={paramsLocked} onChange={(e) => setForm({ ...form, format: e.target.value })}>
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
              disabled={paramsLocked}
              onChange={(e) => setForm({ ...form, rounds_per_match: Number(e.target.value) })}
            />
          </label>
          <label className="field">
            <span>{t("playerCap")}</span>
            <input
              type="number"
              min={2}
              value={form.max_players}
              disabled={paramsLocked}
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
            <select value={form.reveal_mode} disabled={paramsLocked} onChange={(e) => setForm({ ...form, reveal_mode: e.target.value })}>
              <option value="history">{t("revealHistory")}</option>
              <option value="blind">{t("revealBlind")}</option>
              <option value="open">{t("revealOpen")}</option>
            </select>
          </label>
          <label className="field">
            <span>{t("payoffMatrix")}</span>
            <select value={form.payoff_preset} disabled={paramsLocked} onChange={(e) => setForm({ ...form, payoff_preset: e.target.value })}>
              <option value="royale">{t("presetRoyale")}</option>
              <option value="prisoner">{t("presetPrisoner")}</option>
              <option value="chicken">{t("presetChicken")}</option>
              <option value="stag">{t("presetStag")}</option>
            </select>
            <PayoffGrid payoff={PAYOFF_PRESETS[form.payoff_preset] || PAYOFF_PRESETS.royale} />
          </label>
          <label className="field">
            <span>{t("judgeOptional")}</span>
            <select
              value={form.judge_avatar_id}
              disabled={paramsLocked}
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
          <div className="btn-row">
            <button className="btn btn-primary" type="button" onClick={() => save()}>
              {selected ? t("save") : t("create")}
            </button>
            {selected ? (
              <button className="btn" type="button" onClick={startBlank}>
                {t("newEventAction")}
              </button>
            ) : null}
          </div>
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
              onClick={() => pick(item)}
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
          <p className="hint">{t("runModeHint")}</p>
          <div className="btn-row" style={{ margin: "12px 0" }}>
            <button className="btn btn-primary" onClick={() => act(`/api/admin/events/${selected.id}/open`)}>
              {t("openReg")}
            </button>
            {canStart ? (
              <>
                <button className="btn btn-primary" onClick={() => act(`/api/admin/events/${selected.id}/start`, { auto_advance: true })}>
                  {t("launchAll")}
                </button>
                <button className="btn" onClick={() => act(`/api/admin/events/${selected.id}/start`, { auto_advance: false })}>
                  {t("runRound")}
                </button>
              </>
            ) : null}
            {selected.status === "running" && !selected.auto_advance ? (
              <>
                <button className="btn btn-primary" disabled={!moreRounds} onClick={() => act(`/api/admin/events/${selected.id}/next-round`)}>
                  {t("nextRound")}
                </button>
                <button className="btn" onClick={() => act(`/api/admin/events/${selected.id}/run-all`)}>
                  {t("launchRest")}
                </button>
              </>
            ) : null}
            <button className="btn" onClick={() => act(`/api/admin/events/${selected.id}/reset`)}>
              {t("reset")}
            </button>
            <Link className="btn" to={`/admin/tablero/${selected.code}`}>
              {t("viewBoard")}
            </Link>
          </div>
          {selected.status === "running" && selected.auto_advance ? <p className="hint">{t("autoRunning")}</p> : null}
          {selected.status === "running" && !selected.auto_advance && !roundOpen ? <p className="hint">{t("waitingNext")}</p> : null}
          {live ? (
            <>
              <p className="hint">
                {t("enrolledLive", {
                  players: live.players.length,
                  running: live.matches.filter((m) => m.status === "running").length,
                })}
              </p>
              <div className="grid grid-2">
                {live.matches.slice(0, 8).map((match) => (
                  <MatchCard key={match.id} match={match} compact showRound />
                ))}
              </div>
            </>
          ) : null}
        </div>
      ) : null}
    </>
  );
}
