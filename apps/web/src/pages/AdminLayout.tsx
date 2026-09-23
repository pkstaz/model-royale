import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { storage } from "../api";
import { Masthead } from "../ui";

export default function AdminLayout() {
  const navigate = useNavigate();
  useEffect(() => {
    if (!storage.adminToken()) navigate("/admin/login");
  }, [navigate]);

  return (
    <div className="page">
      <Masthead
        right={
          <nav>
            <NavLink to="/admin">Eventos</NavLink>
            <NavLink to="/admin/avatares">Avatares</NavLink>
          </nav>
        }
      />
      <div className="shell">
        <aside className="sidebar">
          <NavLink to="/admin" end>
            Eventos
          </NavLink>
          <NavLink to="/admin/avatares">Avatares</NavLink>
          <NavLink to="/tablero/TALLER">Tablero público</NavLink>
        </aside>
        <div className="main">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
