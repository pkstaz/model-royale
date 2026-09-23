import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, storage } from "../api";
import { tApiError, useT } from "../i18n";
import { Masthead } from "../ui";

export default function Home() {
  const { t } = useT();
  const navigate = useNavigate();
  const [mode, setMode] = useState<"join" | "login">("join");
  const [code, setCode] = useState(() => localStorage.getItem("mr_code") || "TALLER");
  const [name, setName] = useState(() => localStorage.getItem("mr_name") || "");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [hasSession, setHasSession] = useState(Boolean(storage.playerToken()));

  useEffect(() => {
    const token = storage.playerToken();
    if (!token) {
      setHasSession(false);
      return;
    }
    api
      .get("/api/play/me", token)
      .then(() => setHasSession(true))
      .catch(() => {
        storage.clearPlayer();
        setHasSession(false);
      });
  }, []);

  const remember = () => {
    localStorage.setItem("mr_code", code);
    localStorage.setItem("mr_name", name);
  };

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      remember();
      const path = mode === "join" ? "/api/play/join" : "/api/play/login";
      const body = await api.post(path, { code, display_name: name, password });
      storage.setPlayerToken(body.token);
      navigate("/jugar");
    } catch (err) {
      setError(tApiError((err as Error).message, t));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="page hero">
      <Masthead
        right={
          <nav>
            <Link to="/tablero/TALLER">{t("board")}</Link>
            <Link to="/admin">{t("admin")}</Link>
          </nav>
        }
      />
      <div className="hero-body">
        <div className="kicker">{t("kicker")}</div>
        <h1>{t("heroTitle")}</h1>
        <p className="lede">{t("heroLede")}</p>
        {hasSession ? (
          <p className="card" style={{ marginBottom: 16 }}>
            {t("hasSession")} <Link to="/jugar">{t("backToArena")}</Link>
          </p>
        ) : null}
        <form className="card" onSubmit={onSubmit}>
          <div className="seg">
            <button type="button" className={mode === "join" ? "active" : ""} onClick={() => setMode("join")}>
              {t("join")}
            </button>
            <button type="button" className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>
              {t("enter")}
            </button>
          </div>
          <label className="field">
            <span>{t("eventCode")}</span>
            <input value={code} onChange={(e) => setCode(e.target.value.toUpperCase())} autoCapitalize="characters" />
          </label>
          <label className="field">
            <span>{t("yourName")}</span>
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Ada" required minLength={2} />
          </label>
          <label className="field">
            <span>{mode === "join" ? t("createPassword") : t("yourPassword")}</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={4}
              autoComplete={mode === "join" ? "new-password" : "current-password"}
              placeholder={t("passwordHint")}
            />
          </label>
          {error ? <p className="flash">{error}</p> : null}
          <button className="btn btn-primary" type="submit" disabled={busy} style={{ width: "100%" }}>
            {mode === "join" ? t("join") : t("enterHistory")}
          </button>
          <p className="hint" style={{ marginTop: 12 }}>
            {mode === "join" ? t("joinHint") : t("loginHint")}
          </p>
        </form>
      </div>
    </div>
  );
}
