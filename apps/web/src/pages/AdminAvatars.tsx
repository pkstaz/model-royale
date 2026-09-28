import { FormEvent, useEffect, useState } from "react";
import { api, storage } from "../api";
import { tApiError, useT } from "../i18n";
import type { Avatar, InferenceSettings } from "../types";

const DEFAULT_MAAS = "https://maas-rhdp.apps.maas.redhatworkshops.io/v1/models";

const blank = {
  name: "",
  slug: "",
  description: "",
  color: "#EE0000",
  provider: "maas",
  base_url: "",
  model_id: "",
  api_key: "",
  use_global_endpoint: true,
  use_global_api_key: true,
  max_tokens: 220,
  personality: "",
  enabled: true,
};

type PingState = { status: "testing" | "ok" | "fail"; detail?: string };

export default function AdminAvatars() {
  const { t } = useT();
  const token = storage.adminToken();
  const [rows, setRows] = useState<Avatar[]>([]);
  const [form, setForm] = useState(blank);
  const [editing, setEditing] = useState<string | null>(null);
  const [settings, setSettings] = useState<InferenceSettings>({ default_base_url: DEFAULT_MAAS, has_api_key: false });
  const [globalUrl, setGlobalUrl] = useState(DEFAULT_MAAS);
  const [globalKey, setGlobalKey] = useState("");
  const [pings, setPings] = useState<Record<string, PingState>>({});
  const [error, setError] = useState("");
  const [saved, setSaved] = useState("");

  const load = () => {
    api.get("/api/admin/avatars", token).then(setRows);
    api.get("/api/admin/settings", token).then((body: InferenceSettings) => {
      setSettings(body);
      setGlobalUrl(body.default_base_url || DEFAULT_MAAS);
    });
  };

  useEffect(() => {
    load();
  }, []);

  const saveGlobals = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    setSaved("");
    try {
      const body: InferenceSettings = await api.patch(
        "/api/admin/settings",
        { default_base_url: globalUrl, default_api_key: globalKey },
        token,
      );
      setSettings(body);
      setGlobalKey("");
      setSaved(t("savedGlobals"));
      load();
    } catch (err) {
      setError(tApiError((err as Error).message, t));
    }
  };

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
      use_global_endpoint: avatar.use_global_endpoint !== false,
      use_global_api_key: avatar.use_global_api_key !== false,
      max_tokens: avatar.max_tokens,
      personality: avatar.personality,
      enabled: avatar.enabled,
    });
  };

  const test = async (id: string) => {
    setPings((prev) => ({ ...prev, [id]: { status: "testing" } }));
    try {
      const body = await api.post(`/api/admin/avatars/${id}/ping`, {}, token);
      setPings((prev) => ({
        ...prev,
        [id]: { status: body.ok ? "ok" : "fail", detail: body.ok ? undefined : String(body.detail || "") },
      }));
    } catch (err) {
      setPings((prev) => ({
        ...prev,
        [id]: { status: "fail", detail: tApiError((err as Error).message, t) },
      }));
    }
  };

  return (
    <>
      <p className="kicker">{t("maintainer")}</p>
      <h1>{t("avatars")}</h1>
      <p className="hint">{t("avatarsHint")}</p>
      {error ? <p className="flash">{error}</p> : null}
      {saved ? <p className="hint">{saved}</p> : null}

      <form className="card" onSubmit={saveGlobals} style={{ marginTop: 16 }}>
        <h3>{t("maasTitle")}</h3>
        <p className="hint">{t("maasHint")}</p>
        <label className="field">
          <span>{t("globalEndpoint")}</span>
          <input value={globalUrl} onChange={(e) => setGlobalUrl(e.target.value)} placeholder={DEFAULT_MAAS} />
        </label>
        <label className="field">
          <span>{t("globalApiKey")}</span>
          <input
            type="password"
            value={globalKey}
            onChange={(e) => setGlobalKey(e.target.value)}
            placeholder={settings.has_api_key ? t("keyConfigured") : t("noGlobalKey")}
            autoComplete="off"
          />
        </label>
        <div className="btn-row">
          <button className="btn btn-primary" type="submit">
            {t("saveGlobals")}
          </button>
        </div>
      </form>

      <div className="grid grid-2" style={{ marginTop: 16 }}>
        <form className="card" onSubmit={submit}>
          <h3>{editing ? t("edit") : t("newAvatar")}</h3>
          <label className="field">
            <span>{t("name")}</span>
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          </label>
          <label className="field">
            <span>{t("slug")}</span>
            <input value={form.slug} onChange={(e) => setForm({ ...form, slug: e.target.value })} placeholder="redrock" />
          </label>
          <label className="field">
            <span>{t("color")}</span>
            <input value={form.color} onChange={(e) => setForm({ ...form, color: e.target.value })} />
          </label>
          <label className="field">
            <span>{t("modelId")}</span>
            <input
              value={form.model_id}
              onChange={(e) => setForm({ ...form, model_id: e.target.value })}
              placeholder="granite-3-2-8b-instruct"
            />
          </label>
          <fieldset className="field">
            <span>{t("endpointMode")}</span>
            <div className="seg">
              <label>
                <input
                  type="radio"
                  name="endpoint-mode"
                  checked={form.use_global_endpoint}
                  onChange={() => setForm({ ...form, use_global_endpoint: true })}
                />
                {t("useGlobal")}
              </label>
              <label>
                <input
                  type="radio"
                  name="endpoint-mode"
                  checked={!form.use_global_endpoint}
                  onChange={() => setForm({ ...form, use_global_endpoint: false })}
                />
                {t("useCustom")}
              </label>
            </div>
          </fieldset>
          {form.use_global_endpoint ? (
            <p className="hint">{settings.default_base_url || DEFAULT_MAAS}</p>
          ) : (
            <label className="field">
              <span>{t("baseUrl")}</span>
              <input
                value={form.base_url}
                onChange={(e) => setForm({ ...form, base_url: e.target.value })}
                placeholder={DEFAULT_MAAS}
              />
            </label>
          )}
          <fieldset className="field">
            <span>{t("apiKeyMode")}</span>
            <div className="seg">
              <label>
                <input
                  type="radio"
                  name="key-mode"
                  checked={form.use_global_api_key}
                  onChange={() => setForm({ ...form, use_global_api_key: true })}
                />
                {t("useGlobal")}
              </label>
              <label>
                <input
                  type="radio"
                  name="key-mode"
                  checked={!form.use_global_api_key}
                  onChange={() => setForm({ ...form, use_global_api_key: false })}
                />
                {t("useCustom")}
              </label>
            </div>
          </fieldset>
          {!form.use_global_api_key ? (
            <label className="field">
              <span>{t("apiKey")}</span>
              <input
                type="password"
                value={form.api_key}
                onChange={(e) => setForm({ ...form, api_key: e.target.value })}
                autoComplete="off"
              />
            </label>
          ) : null}
          <label className="field">
            <span>{t("personality")}</span>
            <textarea value={form.personality} onChange={(e) => setForm({ ...form, personality: e.target.value })} />
          </label>
          <label className="field">
            <span>{t("description")}</span>
            <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </label>
          <label className="field">
            <span>{t("maxTokens")}</span>
            <input
              type="number"
              min="16"
              max="4096"
              value={form.max_tokens}
              onChange={(e) => setForm({ ...form, max_tokens: Number(e.target.value) })}
            />
          </label>
          <label className="check">
            <input
              type="checkbox"
              checked={form.enabled}
              onChange={(e) => setForm({ ...form, enabled: e.target.checked })}
            />
            {t("enabled")}
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
          {rows.map((avatar) => {
            const ping = pings[avatar.id];
            return (
              <div
                key={avatar.id}
                className={`avatar-row${ping ? ` ping-${ping.status}` : ""}`}
              >
                <div className="avatar-row-head">
                  <div>
                    <span className="swatch" style={{ background: avatar.color }} />
                    <strong>{avatar.name}</strong>
                    <span className="hint"> · {avatar.model_id || t("noEndpoint")}</span>
                  </div>
                  {ping?.status === "testing" ? <span className="pill info">{t("testing")}</span> : null}
                  {ping?.status === "ok" ? <span className="pill ok">{t("testOk")}</span> : null}
                  {ping?.status === "fail" ? <span className="pill fail">{t("testFail")}</span> : null}
                </div>
                <div className="hint" style={{ marginTop: 4 }}>
                  {avatar.use_global_endpoint !== false ? t("usingGlobal") : t("usingCustom")}
                  {" · "}
                  {avatar.has_resolved_api_key ? t("keySet") : t("noKey")}
                </div>
                {ping?.status === "fail" && ping.detail ? (
                  <p className="ping-detail fail">{ping.detail}</p>
                ) : null}
                <div className="btn-row" style={{ marginTop: 8 }}>
                  <button className="btn" type="button" onClick={() => edit(avatar)}>
                    {t("edit")}
                  </button>
                  <button
                    className="btn"
                    type="button"
                    disabled={ping?.status === "testing"}
                    onClick={() => test(avatar.id)}
                  >
                    {t("test")}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </>
  );
}
