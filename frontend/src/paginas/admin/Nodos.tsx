import { Fragment, useState, type FormEvent } from "react";
import { Link } from "react-router";

import { useEditarNodo, useNodosTodos } from "../../api/administracion";
import { useNodo } from "../../api/consultas";
import { Cargando, ErrorDeCarga } from "../../componentes/Estados";
import { MADUREZ } from "../../componentes/etiquetas";
import { useSesion } from "../../sesion/Sesion";
import type { NodoResumen, Visibilidad } from "../../tipos";
import { fechaHora, useTitulo } from "../../util/formato";
import { ErrorDeAccion, puede, Registrado, type Resultado } from "./comun";

export const VISIBILIDAD: Record<Visibilidad, { texto: string; clase: string }> = {
  publicado: { texto: "Publicado", clase: "tag tag-dev" },
  oculto: { texto: "Oculto", clase: "tag tag-eval" },
  retirado: { texto: "Retirado", clase: "tag tag-sin" },
};

/** De `retirado` solo se vuelve a `oculto`: publicarlo otra vez pasa por revisarlo. */
const TRANSICIONES: Record<Visibilidad, { a: Visibilidad; texto: string }[]> = {
  oculto: [
    { a: "publicado", texto: "Publicar" },
    { a: "retirado", texto: "Retirar" },
  ],
  publicado: [
    { a: "oculto", texto: "Ocultar" },
    { a: "retirado", texto: "Retirar" },
  ],
  retirado: [{ a: "oculto", texto: "Volver a oculto" }],
};

export function Nodos() {
  useTitulo("Visibilidad · Administración");
  const { yo } = useSesion();
  const nodos = useNodosTodos();
  const editar = useEditarNodo();
  const [abierto, setAbierto] = useState<string | null>(null);
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const [error, setError] = useState<unknown>(null);

  const avisar = (r: Resultado) => {
    setError(null);
    setResultado(r);
  };
  const fallar = (e: unknown) => {
    setResultado(null);
    setError(e);
  };

  const cambiar = (nodo: NodoResumen, a: Visibilidad) => {
    if (
      a === "retirado" &&
      !window.confirm(
        `¿Retirar ${nodo.nombre}? Sale del catálogo, también por enlace directo, y deja de leerse su repositorio.`,
      )
    ) {
      return;
    }
    editar.mutate(
      { identificador: nodo.identificador, visibilidad: a },
      {
        onSuccess: () =>
          avisar({
            texto: `Visibilidad de ${nodo.identificador}: ${VISIBILIDAD[nodo.visibilidad].texto.toLowerCase()} a ${VISIBILIDAD[a].texto.toLowerCase()}`,
          }),
        onError: fallar,
      },
    );
  };

  return (
    <>
      <h2>Visibilidad</h2>
      <p className="lead">
        Qué fichas muestra el catálogo público. Publicar es una decisión editorial: no exige pantalla,
        wiki ni servicio disponible. Una ficha recién registrada queda oculta.
      </p>

      <Registrado resultado={resultado} autor={yo?.nombre} />
      <ErrorDeAccion error={error} />

      {nodos.isPending ? (
        <Cargando />
      ) : nodos.isError ? (
        <ErrorDeCarga error={nodos.error} />
      ) : nodos.data.length === 0 ? (
        <p className="sin-params">Todavía no hay nodos. Aparecen al registrar una fuente.</p>
      ) : (
        <div className="tabla-ancha">
          <table className="admin-tabla">
            <thead>
              <tr>
                <th>Nodo</th>
                <th>Visibilidad</th>
                <th>Madurez</th>
                <th>Leído</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {nodos.data.map((n) => (
                <Fragment key={n.identificador}>
                  <tr>
                    <td>
                      <Link to={`/apis/${n.identificador}`}>{n.nombre}</Link>
                      <span className="admin-meta">
                        <code>{n.identificador}</code>
                      </span>
                    </td>
                    <td>
                      <span className={VISIBILIDAD[n.visibilidad].clase}>{VISIBILIDAD[n.visibilidad].texto}</span>
                    </td>
                    <td>
                      <span className={MADUREZ[n.madurez]}>{n.madurez}</span>
                    </td>
                    <td className="admin-meta">{fechaHora(n.leido_en)}</td>
                    <td className="admin-acciones">
                      {puede(yo, "curador") &&
                        TRANSICIONES[n.visibilidad].map((t) => (
                          <button
                            key={t.a}
                            type="button"
                            className="btn-copiar"
                            onClick={() => cambiar(n, t.a)}
                            disabled={editar.isPending}
                          >
                            {t.texto}
                          </button>
                        ))}
                      <button
                        type="button"
                        className="btn-copiar"
                        aria-expanded={abierto === n.identificador}
                        onClick={() => setAbierto((a) => (a === n.identificador ? null : n.identificador))}
                      >
                        {abierto === n.identificador ? "Cerrar" : "Detalle"}
                      </button>
                    </td>
                  </tr>
                  {abierto === n.identificador && (
                    <tr>
                      <td colSpan={5}>
                        <DetalleNodo nodo={n} alAvisar={avisar} alFallar={fallar} />
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

function DetalleNodo({
  nodo,
  alAvisar,
  alFallar,
}: {
  nodo: NodoResumen;
  alAvisar: (r: Resultado) => void;
  alFallar: (e: unknown) => void;
}) {
  const { yo } = useSesion();
  // Un nodo retirado responde 410 en la ficha: se trabaja con el resumen.
  const ficha = useNodo(nodo.visibilidad === "retirado" ? undefined : nodo.identificador);
  const editar = useEditarNodo();
  const [orden, setOrden] = useState(String(nodo.orden));
  const [nota, setNota] = useState<string | null>(null);
  const notaActual = nota ?? ficha.data?.nota_editorial ?? "";
  const editable = puede(yo, "curador");

  const enviar = (evento: FormEvent) => {
    evento.preventDefault();
    editar.mutate(
      { identificador: nodo.identificador, orden: Number(orden), nota_editorial: notaActual },
      {
        onSuccess: () => alAvisar({ texto: `Orden y nota editorial de ${nodo.identificador} guardados` }),
        onError: alFallar,
      },
    );
  };

  const id = nodo.identificador;
  const deFicha: [string, string][] = [
    ["Nombre", nodo.nombre],
    ["Ámbito", nodo.ambito],
    ["Madurez", nodo.madurez],
    ["Función", nodo.funcion],
    [
      "Responsable",
      ficha.data
        ? [ficha.data.responsable.organismo, ficha.data.responsable.equipo, ficha.data.responsable.correo]
            .filter(Boolean)
            .join(" · ")
        : "",
    ],
    ["Versión del contrato", ficha.data?.especificacion?.version ?? ""],
    ["Commit leído", ficha.data?.commit ?? ""],
  ];

  return (
    <div className="admin-detalle">
      <fieldset className="admin-ficha" disabled>
        <legend>Campos de la ficha</legend>
        <p className="admin-meta" id={`nota-ficha-${id}`}>
          Los escribe la sincronización desde el repositorio del servicio. Para cambiarlos, se edita{" "}
          <code>nodo/ficha.yaml</code> allá y se resincroniza la fuente.
        </p>
        {ficha.isError && nodo.visibilidad !== "retirado" && <ErrorDeCarga error={ficha.error} />}
        <div className="admin-rejilla">
          {deFicha.map(([etiqueta, valor]) => {
            const campo = `${id}-${etiqueta}`;
            return (
              <div className="campo" key={etiqueta}>
                <label htmlFor={campo}>{etiqueta}</label>
                <input id={campo} value={valor} readOnly disabled aria-describedby={`nota-ficha-${id}`} />
              </div>
            );
          })}
        </div>
      </fieldset>

      <form onSubmit={enviar}>
        <fieldset className="admin-editorial" disabled={!editable}>
          <legend>Decisión editorial</legend>
          <div className="admin-fila">
            <div className="campo">
              <label htmlFor={`${id}-orden`}>Orden en el catálogo</label>
              <input
                id={`${id}-orden`}
                type="number"
                min={0}
                max={32767}
                value={orden}
                onChange={(e) => setOrden(e.target.value)}
              />
            </div>
          </div>
          <div className="campo">
            <label htmlFor={`${id}-nota`}>Nota editorial</label>
            <textarea
              id={`${id}-nota`}
              className="admin-nota"
              value={notaActual}
              onChange={(e) => setNota(e.target.value)}
              placeholder="Por ejemplo, el aviso de que el servicio es una demostración."
            />
          </div>
          {editable && (
            <p>
              <button className="btn btn-p" type="submit" disabled={editar.isPending}>
                Guardar
              </button>
            </p>
          )}
        </fieldset>
      </form>
    </div>
  );
}
