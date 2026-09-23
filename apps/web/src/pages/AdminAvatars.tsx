import { FormEvent, useEffect, useState } from "react";
import { api, storage } from "../api";
import { tApiError, useT } from "../i18n";
import type { Avatar } from "../types";

const blank = {
  name: "",
  slug: "",
  description: "",
  color: "#EE0000",
  provider: "openshift-ai",
  base_url: "",
  model_id: "",
  api_key: "",
  temperature: 0.4,
  max_tokens: 220,
  personality: "",
  enabled: true,
};

export default function AdminAvatars() {
  const { t } = useT();
  const token = storage.adminToken();
  const [rows, setRows] = useState<Avatar[]>([]);
  const [form, setForm] = useState(blank);
  const [editing, setEditing] = useState<string | null>(null);
  const [ping, setPing] = useState("");
  const [error, setError] = useState("");

  const load = () => api.get("/api/admin/avatars", token).then(setRows);

  useEffect(() => {
    load();
  }, []);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    try {
      if (editing) {
        await api.patch(`/api/admin/avatars/${editing}`, form, token);
      } else {
        await api.post("/api/admin/avatars", form, token);
      }
      setForm(blank);
      setEditing(null);
      load();
    } catch (err) {
      setError(tApiError((err as Error).message, t));
    }
  };

  const edit = (avatar: Avatar) => {
    setEditing(avatar.id);
    setForm({
      name: avatar.name,
      slug: avatar.slug,
      description: avatar.description,
      color: avatar.color,
      provider: avatar.provider,
      base_url: avatar.base_url,
      model_id: avatar.model_id,
      api_key: "",
      temperature: avatar.temperature,
      max_tokens: avatar.max_tokens,
      personality: avatar.personality,
      enabled: avatar.enabled,
    });
  };

  const test = async (id: string) => {
    setPing(t("testing"));
    const body = await api.post(`/api/admin/avatars/${id}/ping`, {}, token);
    setPing(body.ok ? `OK: ${body.detail}` : t("failed", { detail: body.detail }));
  };

  return (
    <>
      <p className="kicker">{t("maintainer")}</p>
      <h1>{t("avatars")}</h1>
      <p className="hint">{t("avatarsHint")}</p>
      {error ? <p className="flash">{error}</p> : null}
      {ping ? <p className="hint">{ping}</p> : null}
      <div className="grid grid-2" style={{ marginTop: 16 }}>
        <form className="card" onSubmit={submit}>
          <h3>{editing ? t("edit") : t("newAvatar")}</h3>
          <label className="field">
            <span>{t("name")}</span>
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          </label>
          <label className="field">
            <span>{t("slug")}</span>
            <input value={form.slug} onChange={(e) => setForm({ ...form, slug: e.target.value })} placeholder="granite" />
          </label>
          <label className="field">
            <span>{t("color")}</span>
            <input value={form.color} onChange={(e) => setForm({ ...form, color: e.target.value })} />
          </label>
          <label className="field">
            <span>{t("baseUrl")}</span>
            <input
              value={form.base_url}
              onChange={(e) => setForm({ ...form, base_url: e.target.value })}
              placeholder="https://granite-predictor.apps.cluster/v1"
            />
          </label>
          <label className="field">
            <span>{t("modelId")}</span>
            <input
              value={form.model_id}
              onChange={(e) => setForm({ ...form, model_id: e.target.value })}
              placeholder="granite-3.1-8b-instruct"
            />
          </label>
          <label className="field">
            <span>{t("apiKey")}</span>
            <input value={form.api_key} onChange={(e) => setForm({ ...form, api_key: e.target.value })} />
          </label>
          <label className="field">
            <span>{t("personality")}</span>
            <textarea value={form.personality} onChange={(e) => setForm({ ...form, personality: e.target.value })} />
          </label>
          <label className="field">
            <span>{t("description")}</span>
            <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </label>
          <div className="btn-row">
            <button className="btn btn-primary" type="submit">
              {editing ? t("save") : t("create")}
            </button>
            {editing ? (
              <button
                className="btn"
                type="button"
                onClick={() => {
                  setEditing(null);
                  setForm(blank);
                }}
              >
                {t("cancel")}
              </button>
            ) : null}
          </div>
        </form>
        <div className="card">
          <h3>{t("registeredList")}</h3>
          {rows.map((avatar) => (
            <div key={avatar.id} style={{ padding: "12px 0", borderBottom: "1px solid var(--bg-400)" }}>
              <span className="swatch" style={{ background: avatar.color }} />
              <strong>{avatar.name}</strong>
              <span className="hint"> · {avatar.reachable ? avatar.model_id : t("noEndpoint")}</span>
              <div className="btn-row" style={{ marginTop: 8 }}>
                <button className="btn" type="button" onClick={() => edit(avatar)}>
                  {t("edit")}
                </button>
                <button className="btn" type="button" onClick={() => test(avatar.id)}>
                  {t("test")}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
