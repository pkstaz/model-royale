import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { storage } from "../api";
import { useT } from "../i18n";
import { Masthead } from "../ui";

export default function AdminLayout() {
  const { t } = useT();
  const navigate = useNavigate();
  useEffect(() => {
    if (!storage.adminToken()) navigate("/admin/login");
  }, [navigate]);

  return (
    <div className="page">
      <Masthead
        right={
          <nav>
            <NavLink to="/admin">{t("events")}</NavLink>
            <NavLink to="/admin/avatares">{t("avatars")}</NavLink>
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
