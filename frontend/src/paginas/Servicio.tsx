import { useCallback, useState, type ComponentType } from "react";
import { Link, useParams } from "react-router";

import { esEstado } from "../api/cliente";
import { useEntradas, useNodo, useServicio } from "../api/consultas";
import { Cargando, ErrorDeCarga } from "../componentes/Estados";
import { ESTADO_SERVICIO } from "../componentes/etiquetas";
import { AvisoDeOrigen } from "../componentes/Origen";
import type { Origen, Servicio as TipoServicio } from "../tipos";
import { fechaLarga, useTitulo } from "../util/formato";
import { PaginaNoExiste } from "./NoEncontrada";
import { BuscadorCut } from "./herramientas/BuscadorCut";
import { ConsultaPermisos } from "./herramientas/ConsultaPermisos";

export type AlResponder = (origen: Origen, obtenidoEn: string) => void;

// La herramienta sale del nodo sobre el que se construye el servicio, no del texto: el texto lo
// edita un curador, la herramienta es código.
const HERRAMIENTAS: Record<string, ComponentType<{ alResponder: AlResponder }>> = {
  cut: BuscadorCut,
  "permisos-de-circulacion": ConsultaPermisos,
};

export function Servicio() {
  const { slug = "" } = useParams();
  const consulta = useServicio(slug);

  if (consulta.isPending) {
    return (
      <div className="wrap">
        <Cargando />
      </div>
    );
  }
  if (consulta.isError) {
    if (esEstado(consulta.error, 404)) return <PaginaNoExiste />;
    return (
      <div className="wrap">
        <section>
          <ErrorDeCarga error={consulta.error} />
        </section>
      </div>
    );
  }
  return <PantallaDeServicio servicio={consulta.data} />;
}

function PantallaDeServicio({ servicio }: { servicio: TipoServicio }) {
  useTitulo(servicio.nombre);
  const nodo = useNodo(servicio.nodo);
  const entradas = useEntradas(servicio.nodo);
  const [respuesta, setRespuesta] = useState<{ origen: Origen; obtenidoEn: string } | null>(null);
  const alResponder = useCallback<AlResponder>(
    (origen, obtenidoEn) => setRespuesta({ origen, obtenidoEn }),
    [],
  );
  const Herramienta = HERRAMIENTAS[servicio.nodo];
  const estado = ESTADO_SERVICIO[servicio.estado];
  const entrada = entradas.data?.[0];

  return (
    <main>
      <section style={{ paddingBottom: 10 }}>
        <div className="wrap">
          <p className="miga">
            <Link to="/servicios">Servicios</Link> / {servicio.nombre}
          </p>
          <p className="eyebrow">Servicio</p>
          <h2>{servicio.nombre}</h2>
          <div className="servicio-grid">
            <div>
              {servicio.descripcion && <p className="lead">{servicio.descripcion}</p>}
              {servicio.nota && (
                <div className="aviso">
                  <p>{servicio.nota}</p>
                </div>
              )}
              {Herramienta && (
                <Herramienta alResponder={alResponder} />
              )}
            </div>
            <div className="ficha-lado">
              <aside className="panel">
                <p className="panel-tit">Documentación</p>
                <ul className="panel-enlaces">
                  <li>
                    <Link to={`/apis/${encodeURIComponent(servicio.nodo)}`}>
                      <b>La API que usa</b>
                      <span>{nodo.data?.nombre ?? servicio.nodo}</span>
                    </Link>
                  </li>
                  {entrada && (
                    <li>
                      <Link to={`/wiki/${entrada.slug}`}>
                        <b>Entrada de wiki</b>
                        <span>{entrada.titulo}</span>
                      </Link>
                    </li>
                  )}
                </ul>
              </aside>
              <aside className="panel">
                <dl>
                  <dt>Estado</dt>
                  <dd>
                    <span className={estado.clase}>{estado.texto}</span>
                  </dd>
                  <dt>Actualizado por última vez</dt>
                  <dd>{fechaLarga(servicio.actualizado)}</dd>
                </dl>
              </aside>
            </div>
          </div>
        </div>
      </section>

      <section className="gris">
        <div className="wrap">
          <p className="eyebrow">De dónde salen estos datos</p>
          <h2>Quién genera cada dato</h2>
          {servicio.fuentes.length > 0 && (
            <div className="tabla-ancha">
              <table>
                <thead>
                  <tr>
                    <th>Dato</th>
                    <th>De dónde viene</th>
                  </tr>
                </thead>
                <tbody>
                  {servicio.fuentes.map((f) => (
                    <tr key={f.dato}>
                      <td>{f.dato}</td>
                      <td>{f.origen}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {respuesta && <AvisoDeOrigen origen={respuesta.origen} obtenidoEn={respuesta.obtenidoEn} />}
        </div>
      </section>
    </main>
  );
}
