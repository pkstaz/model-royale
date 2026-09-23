import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, storage } from "../api";
import { Masthead } from "../ui";

export default function Home() {
  const navigate = useNavigate();
  const [code, setCode] = useState("TALLER");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const onJoin = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const body = await api.post("/api/play/join", { code, display_name: name });
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
        <form className="card" onSubmit={onJoin}>
          <label className="field">
            <span>Código del evento</span>
            <input value={code} onChange={(e) => setCode(e.target.value.toUpperCase())} autoCapitalize="characters" />
          </label>
          <label className="field">
            <span>Tu nombre</span>
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Ada" required minLength={2} />
          </label>
          {error ? <p className="flash">{error}</p> : null}
          <button className="btn btn-primary" type="submit" disabled={busy} style={{ width: "100%" }}>
            Inscribirse
          </button>
        </form>
        <p className="hint" style={{ marginTop: 16 }}>
          El admin abre la inscripción. Los modelos viven fuera de este juego: aquí solo se apunta al endpoint.
        </p>
      </div>
    </div>
  );
}
