import { load } from "js-yaml";
import { useMemo } from "react";

import { Pendiente } from "./Estados";
import { agrupar, tipo, type Documento, type Operacion } from "./openapi";

const DONDE: Record<string, string> = { path: "en la ruta", query: "en la consulta" };

/** Dibuja un contrato OpenAPI operación por operación. Nada de lo que muestra se escribe a mano:
 * si el archivo cambia y la ficha no, la ficha está mintiendo. */
export function Especificacion({ archivo }: { archivo: string }) {
  const leido = useMemo(() => {
    try {
      const doc = load(archivo);
      if (typeof doc !== "object" || doc === null) throw new Error("no es un documento");
      return { doc: doc as Documento };
    } catch (error) {
      return { error: error instanceof Error ? error.message : String(error) };
    }
  }, [archivo]);

  if ("error" in leido) {
    return <Pendiente>No se pudo leer la especificación ({leido.error}).</Pendiente>;
  }

  const { doc } = leido;
  const grupos = agrupar(doc);
  const total = grupos.reduce((n, g) => n + g.operaciones.length, 0);
  const descripcion = doc.info?.description ? String(doc.info.description).trim() : "";

  return (
    <div>
      {descripcion && <p>{descripcion}</p>}
      <dl className="contrato">
        <dt>Título</dt>
        <dd>{doc.info?.title || "—"}</dd>
        <dt>Versión</dt>
        <dd>{doc.info?.version || "—"}</dd>
        <dt>Ruta base</dt>
        <dd>
          <code>{doc.servers?.[0]?.url || "—"}</code>
        </dd>
        <dt>Operaciones</dt>
        <dd>{total}</dd>
      </dl>
      {grupos.map((g) => (
        <div key={g.tag}>
          <h3 className="grupo">{g.tag}</h3>
          {g.operaciones.map((o) => (
            <OperacionDesplegable key={`${o.metodo} ${o.ruta}`} doc={doc} op={o} />
          ))}
        </div>
      ))}
    </div>
  );
}

function OperacionDesplegable({ doc, op }: { doc: Documento; op: Operacion }) {
  return (
    <details className="op">
      <summary>
        <span className={`metodo m-${op.metodo}`}>{op.metodo.toUpperCase()}</span>
        <code className="ruta">{op.ruta}</code>
        <span className="sumario">{op.resumen}</span>
      </summary>
      <div className="op-cuerpo">
        {op.descripcion && <p>{op.descripcion}</p>}
        {op.parametros.length ? (
          <>
            <h4>Parámetros</h4>
            <div className="tabla-ancha">
              <table>
                <thead>
                  <tr>
                    <th>Nombre</th>
                    <th>Dónde</th>
                    <th>Tipo</th>
                    <th>Obligatorio</th>
                  </tr>
                </thead>
                <tbody>
                  {op.parametros.map((p) => (
                    <tr key={`${p.in}-${p.name}`}>
                      <td>
                        <code>{p.name}</code>
                      </td>
                      <td>{DONDE[p.in] ?? p.in}</td>
                      <td>{tipo(doc, p.schema)}</td>
                      <td>{p.required ? "Sí" : "No"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        ) : (
          <p className="sin-params">Sin parámetros.</p>
        )}
        <h4>Respuestas</h4>
        {op.respuestas.map((r) => (
          <div className="respuesta" key={r.codigo}>
            <div className="rc">
              <span className={`codigo ${r.codigo.startsWith("2") ? "rc-ok" : "rc-err"}`}>{r.codigo}</span>
              <span>{r.descripcion}</span>
            </div>
            {r.ejemplo !== null ? (
              <pre className="ejemplo">
                <code>{JSON.stringify(r.ejemplo, null, 2)}</code>
              </pre>
            ) : (
              <p className="sin-params">Sin cuerpo de respuesta.</p>
            )}
          </div>
        ))}
      </div>
    </details>
  );
}
