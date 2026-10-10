import { Link } from "react-router";

import { useTitulo } from "../util/formato";

/** Un 403 con SIN_PERFIL: la persona sí se autenticó, y eso no es un error genérico. */
export function SinPerfil() {
  useTitulo("Sin perfil en el nodo");
  return (
    <section>
      <div className="wrap">
        <p className="eyebrow">Sesión</p>
        <h2>Te autenticaste, pero no tienes perfil en el nodo</h2>
        <p className="lead">
          Tu identidad está verificada, pero todavía nadie te dio un perfil, que es lo que dice qué
          puedes hacer acá.
        </p>
        <p className="lead">
          Si trabajas en un municipio, pídeselo al <strong>encargado del nodo en tu municipio</strong>.
          Si eres de SUBDERE, a un <strong>administrador del nodo</strong>.
        </p>
        <p className="lead">
          Mientras tanto, todo lo público sigue a tu alcance: los <Link to="/apis">catálogos</Link>, las
          fichas y la <Link to="/wiki">wiki</Link>.
        </p>
      </div>
    </section>
  );
}
