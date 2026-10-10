import { Link, Navigate, useLocation, useParams } from "react-router";

import { ErrorApi, esEstado } from "../api/cliente";
import { useArchivoDeEspecificacion, useEntradas, useNodo, useServicios } from "../api/consultas";
import { Especificacion } from "../componentes/Especificacion";
import { Cargando, ErrorDeCarga, Pendiente } from "../componentes/Estados";
import { ACCESO, COPIA, FORMATO, INTERCAMBIO, MADUREZ } from "../componentes/etiquetas";
import type { Nodo } from "../tipos";
import { fechaLarga, useIrAlAncla, useTitulo } from "../util/formato";

/** La ficha se compone de tres pedidos independientes: el nodo, sus servicios y su wiki.
 * Ninguno es obligatorio junto a los otros; se muestra lo que existe. */
export function Ficha() {
  const { id = "" } = useParams();
  const consulta = useNodo(id);
  const { hash } = useLocation();

  if (consulta.isPending) {
    return (
      <div className="wrap">
        <Cargando />
      </div>
    );
  }
  if (consulta.isError) return <FichaConError id={id} error={consulta.error} />;

  const nodo = consulta.data;
  // Un alias responde con el nodo vigente: la dirección pasa a ser la del identificador.
  if (nodo.identificador !== id) {
    return <Navigate to={`/apis/${encodeURIComponent(nodo.identificador)}${hash}`} replace />;
  }
  return <FichaDeNodo nodo={nodo} />;
}

function FichaConError({ id, error }: { id: string; error: unknown }) {
  useTitulo(esEstado(error, 410) ? "Intercambio retirado" : "Nodo no encontrado");
  if (esEstado(error, 404)) {
    return (
      <div className="wrap">
        <p className="miga">
          <Link to="/apis">APIs</Link>
        </p>
        <section>
          <h2>Nodo no encontrado</h2>
          <p className="lead">
            Volver al <Link to="/apis">catálogo de APIs</Link>.
          </p>
        </section>
      </div>
    );
  }
  if (esEstado(error, 410)) {
    const leido = (error as ErrorApi).detalles.find((d) => d.campo === "leido_en")?.valor;
    return (
      <div className="wrap">
        <p className="miga">
          <Link to="/apis">APIs</Link> / {id}
        </p>
        <section>
          <p className="eyebrow">Intercambio retirado</p>
          <h2>
            <code>{id}</code> ya no está en el catálogo
          </h2>
          <p className="lead">
            {(error as ErrorApi).message}
            {typeof leido === "string" && ` Se leyó por última vez el ${fechaLarga(leido)}.`}
          </p>
          <p className="lead">
            Volver al <Link to="/apis">catálogo de APIs</Link>.
          </p>
        </section>
      </div>
    );
  }
  return (
    <div className="wrap">
      <section>
        <ErrorDeCarga error={error} />
      </section>
    </div>
  );
}

function FichaDeNodo({ nodo }: { nodo: Nodo }) {
  useTitulo(nodo.nombre);
  const { hash } = useLocation();
  const servicios = useServicios(nodo.identificador);
  const entradas = useEntradas(nodo.identificador);
  const especificacion = nodo.especificacion;
  const conArchivo = !!especificacion?.archivo;
  const archivo = useArchivoDeEspecificacion(nodo.identificador, conArchivo);
  useIrAlAncla(hash, !archivo.isPending || !conArchivo);

  const instituciones = Array.isArray(nodo.instituciones) ? (nodo.instituciones as string[]) : [];
  const entrada = entradas.data?.[0];
  const plataforma = nodo.clase === "plataforma";

  return (
    <>
      <div className="wrap">
        <p className="miga">
          <Link to="/apis">APIs</Link> / {nodo.nombre}
        </p>
        {nodo.visibilidad === "oculto" && (
          <div className="aviso-neutro aviso">
            <p>
              <b>Este intercambio no aparece en el catálogo.</b> Está en preparación y se muestra solo
              con sesión. Lo que dice esta ficha puede cambiar antes de publicarse.
            </p>
          </div>
        )}
      </div>

      <div className="wrap">
        <div className="ficha-cab">
          {plataforma && <span className="tag tag-plataforma">Base · está siempre</span>}{" "}
          <span className="tag tag-ambito">{nodo.ambito}</span>
          <h1>{nodo.nombre}</h1>
          <p className="func">{nodo.funcion}</p>
        </div>

        <div className="ficha-grid">
          <div>
            <h2>Para qué sirve</h2>
            <p>{nodo.descripcion}</p>
            {nodo.nota_editorial && (
              <div className="aviso">
                <p>{nodo.nota_editorial}</p>
              </div>
            )}

            {!!servicios.data?.length && (
              <>
                <h2>Aplicaciones que la usan</h2>
                <p>Para usar este intercambio a través de una aplicación.</p>
                <div className="apps-vinculadas">
                  {servicios.data.map((s) => (
                    <Link className="app-vinculada" key={s.slug} to={`/servicios/${s.slug}`}>
                      <strong>{s.nombre}</strong>
                      <span className="app-vinculada__ir">Abrir la aplicación →</span>
                      <p>{s.funcion}</p>
                    </Link>
                  ))}
                </div>
              </>
            )}

            <h2>Qué entrega, y en qué forma</h2>
            {especificacion ? (
              <dl className="contrato">
                <dt>Escrito como</dt>
                <dd>{FORMATO[especificacion.formato] ?? especificacion.formato}</dd>
                <dt>Versión</dt>
                <dd>{especificacion.version || "—"}</dd>
                <dt>Archivo</dt>
                <dd>
                  {especificacion.archivo ? (
                    <a href={especificacion.archivo} rel="noopener">
                      <code>{especificacion.ruta.split("/").pop()}</code>
                    </a>
                  ) : (
                    "El catálogo no guarda una copia, a propósito: así no se desactualiza. Está en la fuente oficial, indicada más abajo."
                  )}
                </dd>
                {especificacion.publicada && (
                  <>
                    <dt>Publicado el</dt>
                    <dd>{fechaLarga(especificacion.publicada)}</dd>
                  </>
                )}
                <dt>Quién puede usarlo</dt>
                <dd>{nodo.acceso?.detalle || ACCESO[nodo.acceso_tipo]}</dd>
                <Procedencia nodo={nodo} />
                <dt>Observaciones</dt>
                <dd>
                  {entrada ? (
                    <Link to={`/wiki/${entrada.slug}`}>{entrada.titulo} →</Link>
                  ) : (
                    "Todavía no hay una entrada de wiki para este contrato."
                  )}
                </dd>
              </dl>
            ) : (
              <Pendiente>
                Todavía no está escrito. Acá va a decir qué datos se intercambian, en qué forma, qué se
                puede pedir y qué versión rige. Se publica antes de construir nada.
              </Pendiente>
            )}

            <h2>Qué se le puede pedir</h2>
            {conArchivo ? (
              archivo.isPending ? (
                <Cargando texto="Leyendo la especificación…" />
              ) : archivo.isError ? (
                <ErrorDeCarga error={archivo.error} />
              ) : (
                <Especificacion archivo={archivo.data} />
              )
            ) : especificacion ? (
              <Pendiente>
                El catálogo no copia a mano lo que se le puede pedir a un nodo: lo lee del archivo. Ese
                archivo todavía no está acá, así que por ahora hay que ir al origen, que está indicado más
                arriba.
              </Pendiente>
            ) : (
              <Pendiente>
                Todavía no está definido. Lo primero que conviene ofrecer son consultas y revisiones, no
                operaciones que cambien datos.
              </Pendiente>
            )}

            <h2 id="probar">Dónde practicar</h2>
            <Ambientes nodo={nodo} />
          </div>

          <div className="ficha-lado">
            <aside className="panel">
              <dl>
                <dt>Tipo</dt>
                <dd>
                  {plataforma
                    ? "Base — está siempre, no se elige"
                    : "Intercambio — el municipio entrega o pregunta"}
                </dd>
                {nodo.intercambio && (
                  <>
                    <dt>En qué dirección va</dt>
                    <dd>{INTERCAMBIO[nodo.intercambio] ?? nodo.intercambio}</dd>
                  </>
                )}
                <dt>Madurez</dt>
                <dd>
                  <span className={MADUREZ[nodo.madurez]}>{nodo.madurez}</span>
                </dd>
                {instituciones.length > 0 && (
                  <>
                    <dt>Quiénes participan</dt>
                    <dd>
                      <ul>
                        {instituciones.map((i) => (
                          <li key={i}>{i}</li>
                        ))}
                      </ul>
                    </dd>
                  </>
                )}
                {nodo.origen && (
                  <>
                    <dt>De dónde salió</dt>
                    <dd>
                      {nodo.origen.norma}
                      {nodo.origen.nota && ` — ${nodo.origen.nota}`}
                    </dd>
                  </>
                )}
                <dt>Responsable</dt>
                <dd>
                  {nodo.responsable.organismo}
                  {nodo.responsable.equipo && ` · ${nodo.responsable.equipo}`}
                  {nodo.responsable.correo && (
                    <>
                      <br />
                      <a href={`mailto:${nodo.responsable.correo}`}>{nodo.responsable.correo}</a>
                    </>
                  )}
                </dd>
                <dt>Actualizado por última vez</dt>
                <dd>{fechaLarga(nodo.leido_en)}</dd>
              </dl>
            </aside>
          </div>
        </div>
      </div>
    </>
  );
}

function Procedencia({ nodo }: { nodo: Nodo }) {
  const p = nodo.procedencia;
  if (!p) return null;
  const copia = COPIA[p.copia];
  return (
    <>
      <dt className="contrato-sec">Procedencia</dt>
      <dt>Responsable</dt>
      <dd>
        {nodo.responsable.organismo}
        {nodo.responsable.equipo && ` · ${nodo.responsable.equipo}`}
      </dd>
      {p.fuente && (
        <>
          <dt>Fuente oficial</dt>
          <dd>{p.fuente}</dd>
        </>
      )}
      {(copia || p.detalle) && (
        <>
          <dt>Lo que se ve acá</dt>
          <dd>
            {copia && <span className={copia.clase}>{copia.texto}</span>} {p.detalle}
          </dd>
        </>
      )}
    </>
  );
}

function Ambientes({ nodo }: { nodo: Nodo }) {
  if (!nodo.ambientes.length) {
    return (
      <Pendiente>
        Todavía no existe. La idea es que cualquiera pueda practicar acá con datos inventados, sin
        aceptar términos y condiciones, antes de pedir acceso de verdad.
      </Pendiente>
    );
  }
  return (
    <div className="tabla-ancha">
      <table>
        <thead>
          <tr>
            <th>Ambiente</th>
            <th>Dirección base</th>
            <th>Datos</th>
          </tr>
        </thead>
        <tbody>
          {nodo.ambientes.map((a) => (
            <tr key={a.nombre}>
              <td>{a.nombre === "pruebas" ? "Pruebas" : "Producción"}</td>
              <td>
                <code>{a.base}</code>
              </td>
              <td>{a.datos === "inventados" ? "Inventados" : "Reales"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
