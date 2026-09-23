import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { api, storage } from "../api";
import { useT } from "../i18n";
import { Masthead } from "../ui";

export default function AdminLayout() {
  const { t } = useT();
  const navigate = useNavigate();

  useEffect(() => {
    const token = storage.adminToken();
    if (!token) {
      navigate("/admin/login");
      return;
    }
    api.get("/api/admin/events", token).catch(() => {
      storage.clearAdmin();
      navigate("/admin/login");
    });
  }, [navigate]);

  const logout = () => {
    storage.clearAdmin();
    navigate("/admin/login");
  };

  return (
    <div className="page">
      <Masthead
        right={
          <nav>
            <NavLink to="/admin">{t("events")}</NavLink>
            <NavLink to="/admin/avatares">{t("avatars")}</NavLink>
            <button className="btn-link" type="button" onClick={logout}>
              {t("exit")}
            </button>
          </nav>
        }
      />
      <div className="shell">
        <aside className="sidebar">
          <NavLink to="/admin" end>
            {t("events")}
          </NavLink>
          <NavLink to="/admin/avatares">{t("avatars")}</NavLink>
          <NavLink to="/tablero/TALLER">{t("publicBoard")}</NavLink>
        </aside>
        <div className="main">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
