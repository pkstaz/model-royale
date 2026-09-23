import { FormEvent, useEffect, useState } from "react";
import { api, storage } from "../api";
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
      setError((err as Error).message);
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
    setPing("Probando…");
    const body = await api.post(`/api/admin/avatars/${id}/ping`, {}, token);
    setPing(body.ok ? `OK: ${body.detail}` : `Falló: ${body.detail}`);
  };

  return (
    <>
      <p className="kicker">Mantenedor</p>
      <h1>Avatares</h1>
      <p className="hint">
        Un avatar es una ficha: nombre, color y endpoint OpenAI-compatible. El serving (InferenceService, vLLM) vive en
        otro namespace / otro GitOps.
      </p>
      {error ? <p className="flash">{error}</p> : null}
      {ping ? <p className="hint">{ping}</p> : null}
      <div className="grid grid-2" style={{ marginTop: 16 }}>
        <form className="card" onSubmit={submit}>
          <h3>{editing ? "Editar" : "Nuevo avatar"}</h3>
          <label className="field">
            <span>Nombre</span>
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          </label>
          <label className="field">
            <span>Slug</span>
            <input value={form.slug} onChange={(e) => setForm({ ...form, slug: e.target.value })} placeholder="granite" />
          </label>
          <label className="field">
            <span>Color</span>
            <input value={form.color} onChange={(e) => setForm({ ...form, color: e.target.value })} />
          </label>
          <label className="field">
            <span>Base URL (incluye /v1)</span>
            <input
              value={form.base_url}
              onChange={(e) => setForm({ ...form, base_url: e.target.value })}
              placeholder="https://granite-predictor.apps.cluster/v1"
            />
          </label>
          <label className="field">
            <span>Model id</span>
            <input
              value={form.model_id}
              onChange={(e) => setForm({ ...form, model_id: e.target.value })}
              placeholder="granite-3.1-8b-instruct"
            />
          </label>
          <label className="field">
            <span>API key (opcional, vacío = no tocar)</span>
            <input value={form.api_key} onChange={(e) => setForm({ ...form, api_key: e.target.value })} />
          </label>
          <label className="field">
            <span>Personalidad (system del avatar, visible al jugador)</span>
            <textarea value={form.personality} onChange={(e) => setForm({ ...form, personality: e.target.value })} />
          </label>
          <label className="field">
            <span>Descripción</span>
            <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </label>
          <div className="btn-row">
            <button className="btn btn-primary" type="submit">
              {editing ? "Guardar" : "Crear"}
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
                Cancelar
              </button>
            ) : null}
          </div>
        </form>
        <div className="card">
          <h3>Registrados</h3>
          {rows.map((avatar) => (
            <div key={avatar.id} style={{ padding: "12px 0", borderBottom: "1px solid var(--bg-400)" }}>
              <span className="swatch" style={{ background: avatar.color }} />
              <strong>{avatar.name}</strong>
              <span className="hint"> · {avatar.reachable ? avatar.model_id : "sin endpoint (mock)"}</span>
              <div className="btn-row" style={{ marginTop: 8 }}>
                <button className="btn" type="button" onClick={() => edit(avatar)}>
                  Editar
                </button>
                <button className="btn" type="button" onClick={() => test(avatar.id)}>
                  Probar
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
