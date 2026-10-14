import { Navigate, NavLink, Outlet, useLocation } from "react-router";

import { Cargando } from "../../componentes/Estados";
import { ROLES, useSesion } from "../../sesion/Sesion";
import { gestionaPerfiles } from "./comun";

/** El marco de /admin: exige sesión y muestra solo las secciones que el rol puede usar. */
export function MarcoAdmin() {
  const { token, yo, cargando, sinPerfil } = useSesion();
  const { pathname } = useLocation();

  if (!token) return <Navigate to="/entrar" replace state={{ volverA: pathname }} />;
  if (sinPerfil) return <Navigate to="/sin-perfil" replace />;
  if (cargando || !yo) {
    return (
      <section>
        <div className="wrap">
          <Cargando />
        </div>
      </section>
    );
  }

  return (
    <section className="admin">
      <div className="wrap">
        <p className="eyebrow">Administración</p>
        <p className="admin__quien">
          {yo.nombre} · {ROLES[yo.rol]}
          {yo.municipio ? ` · ${yo.municipio.nombre}` : " · SUBDERE"}
          {yo.es_encargado ? " · encargado del municipio" : ""}
        </p>
        <nav className="admin__nav" aria-label="Secciones de la administración">
          <NavLink to="/admin/fuentes">Fuentes</NavLink>
          <NavLink to="/admin/nodos">Visibilidad</NavLink>
          {gestionaPerfiles(yo) && <NavLink to="/admin/perfiles">Perfiles</NavLink>}
        </nav>
        <Outlet />
      </div>
    </section>
  );
}
