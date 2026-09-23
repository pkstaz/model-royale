import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, storage } from "../api";
import { tApiError, useT } from "../i18n";
import { Masthead } from "../ui";

export default function AdminLogin() {
  const { t } = useT();
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
      setError(tApiError((err as Error).message, t));
    }
  };

  return (
    <div className="page hero">
      <Masthead />
      <div className="hero-body">
        <p className="kicker">{t("maintainer")}</p>
        <h1>{t("admin")}</h1>
        <p className="lede">{t("adminLede")}</p>
        <form className="card" onSubmit={onSubmit}>
          <label className="field">
            <span>{t("password")}</span>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </label>
          {error ? <p className="flash">{error}</p> : null}
          <button className="btn btn-primary" type="submit">
            {t("enter")}
          </button>
        </form>
      </div>
    </div>
  );
}
