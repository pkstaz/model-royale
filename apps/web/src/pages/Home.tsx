import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, storage } from "../api";
import { Masthead } from "../ui";

export default function Home() {
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
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="page hero">
      <Masthead
        right={
          <nav>
            <Link to="/tablero/TALLER">Tablero</Link>
            <Link to="/admin">Admin</Link>
          </nav>
        }
      />
      <div className="hero-body">
        <div className="kicker">OpenShift AI · Battle royale</div>
        <h1>Elige un avatar. Escribe la estrategia. Que peleen los modelos.</h1>
        <p className="lede">
          Tú no combates: inscribes un modelo ya servido en el cluster, le das instrucciones, y el
          tablero muestra quién avanza ronda a ronda.
        </p>
        {hasSession ? (
          <p className="card" style={{ marginBottom: 16 }}>
            Ya tenés una sesión en este dispositivo.{" "}
            <Link to="/jugar">Volver a tu arena</Link>
          </p>
        ) : null}
        <form className="card" onSubmit={onSubmit}>
          <div className="seg">
            <button type="button" className={mode === "join" ? "active" : ""} onClick={() => setMode("join")}>
              Inscribirse
            </button>
            <button type="button" className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>
              Entrar
            </button>
          </div>
          <label className="field">
            <span>Código del evento</span>
            <input value={code} onChange={(e) => setCode(e.target.value.toUpperCase())} autoCapitalize="characters" />
          </label>
          <label className="field">
            <span>Tu nombre</span>
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Ada" required minLength={2} />
          </label>
          <label className="field">
            <span>{mode === "join" ? "Elegí una clave" : "Tu clave"}</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={4}
              autoComplete={mode === "join" ? "new-password" : "current-password"}
              placeholder="mínimo 4 caracteres"
            />
          </label>
          {error ? <p className="flash">{error}</p> : null}
          <button className="btn btn-primary" type="submit" disabled={busy} style={{ width: "100%" }}>
            {mode === "join" ? "Inscribirse" : "Entrar a mi historial"}
          </button>
          <p className="hint" style={{ marginTop: 12 }}>
            {mode === "join"
              ? "Guardá la clave: con ella volvés a entrar al mismo evento aunque te salgas."
              : "Podés entrar aunque el evento ya haya arrancado o terminado, para ver tus combates."}
          </p>
        </form>
      </div>
    </div>
  );
}
