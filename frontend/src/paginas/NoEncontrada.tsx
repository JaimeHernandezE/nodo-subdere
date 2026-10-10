import { Link, Navigate, useLocation } from "react-router";

import { rutaNueva } from "../app/redirecciones";
import { useTitulo } from "../util/formato";

/** Toda ruta desconocida pasa por acá: si es una dirección de la maqueta, redirige. */
export function NoEncontrada() {
  const { pathname, search, hash } = useLocation();
  const destino = rutaNueva(pathname, search, hash);
  if (destino) return <Navigate to={destino} replace />;
  return <PaginaNoExiste />;
}

export function PaginaNoExiste() {
  useTitulo("Página no encontrada");
  return (
    <section>
      <div className="wrap">
        <p className="eyebrow">Error 404</p>
        <h2>Esa página no existe</h2>
        <p className="lead">Puede que el enlace esté mal escrito, o que la página haya cambiado de nombre.</p>
        <div className="acciones" style={{ marginTop: 24, display: "flex", gap: 12, flexWrap: "wrap" }}>
          <Link className="btn btn-p" to="/">
            Volver al inicio
          </Link>
          <Link className="btn" style={{ borderColor: "var(--line)", color: "var(--navy)" }} to="/servicios">
            Ir al catálogo de servicios
          </Link>
        </div>
      </div>
    </section>
  );
}
