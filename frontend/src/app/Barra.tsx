import { useRef, useState, type KeyboardEvent, type MouseEvent } from "react";
import { Link, NavLink, useNavigate } from "react-router";

import { ROLES, useSesion } from "../sesion/Sesion";

const SECCIONES = [
  { a: "/", texto: "Inicio", fin: true },
  { a: "/que-es", texto: "Qué es el nodo" },
  { a: "/apis", texto: "APIs" },
  { a: "/servicios", texto: "Servicios" },
  { a: "/wiki", texto: "Wiki" },
  { a: "/participar", texto: "Cómo participar" },
];

export function Barra() {
  return (
    <header className="topbar">
      <div className="wrap">
        <Link className="brand" to="/" style={{ color: "#fff" }}>
          <span>Subdere</span>
          <b>Nodo SUBDERE</b>
        </Link>
        <nav className="nav" aria-label="Secciones del sitio">
          {SECCIONES.map((s) => (
            <NavLink key={s.a} to={s.a} end={s.fin}>
              {s.texto}
            </NavLink>
          ))}
        </nav>
        <MenuDeSesion />
      </div>
    </header>
  );
}

/** Un <details> nativo, como en la maqueta: se abre con Enter o espacio y se cierra con Escape. */
function MenuDeSesion() {
  const { token, yo, cargando, sinPerfil, salir } = useSesion();
  const [abierto, setAbierto] = useState(false);
  const resumen = useRef<HTMLElement>(null);
  const navegar = useNavigate();

  if (!token) {
    return (
      <Link className="entrar" to="/entrar">
        Entrar
      </Link>
    );
  }

  const alternar = (evento: MouseEvent | KeyboardEvent) => {
    evento.preventDefault();
    setAbierto((a) => !a);
  };

  const teclas = (evento: KeyboardEvent<HTMLElement>) => {
    if (evento.key === "Enter" || evento.key === " ") alternar(evento);
  };

  const cerrarConEscape = (evento: KeyboardEvent<HTMLDetailsElement>) => {
    if (evento.key === "Escape" && abierto) {
      setAbierto(false);
      resumen.current?.focus();
    }
  };

  const etiqueta = cargando ? "Sesión…" : sinPerfil ? "Sin perfil" : (yo?.nombre ?? "Sesión");

  return (
    <details className="sesion" open={abierto} onKeyDown={cerrarConEscape}>
      <summary ref={resumen} onClick={alternar} onKeyDown={teclas}>
        {etiqueta}
      </summary>
      <div className="sesion__menu">
        {yo ? (
          <>
            <p>
              <b>{yo.nombre}</b>
            </p>
            <p>Rol: {ROLES[yo.rol]}</p>
            <p>{yo.municipio ? `Municipio: ${yo.municipio.nombre}` : "SUBDERE"}</p>
          </>
        ) : sinPerfil ? (
          <p>Te autenticaste, pero no tienes perfil en el nodo.</p>
        ) : null}
        <button
          type="button"
          onClick={() => {
            setAbierto(false);
            salir();
            navegar("/");
          }}
        >
          Salir
        </button>
      </div>
    </details>
  );
}
