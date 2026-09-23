import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, storage } from "../api";
import { Masthead } from "../ui";

export default function AdminLogin() {
  const navigate = useNavigate();
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      const body = await api.post("/api/admin/login", { password });
      storage.setAdminToken(body.token);
      navigate("/admin");
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <div className="page hero">
      <Masthead />
      <div className="hero-body">
        <p className="kicker">Mantenedor</p>
        <h1>Admin</h1>
        <p className="lede">Avatares, eventos y el tablero. Los modelos se configuran aquí; viven en OpenShift AI.</p>
        <form className="card" onSubmit={onSubmit}>
          <label className="field">
            <span>Password</span>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </label>
          {error ? <p className="flash">{error}</p> : null}
          <button className="btn btn-primary" type="submit">
            Entrar
          </button>
        </form>
      </div>
    </div>
  );
}
