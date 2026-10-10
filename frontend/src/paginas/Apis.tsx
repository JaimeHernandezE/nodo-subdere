import { Link, useSearchParams } from "react-router";

import { useAmbitos, useNodos } from "../api/consultas";
import { Cargando, ErrorDeCarga } from "../componentes/Estados";
import { ACCESO, MADUREZ } from "../componentes/etiquetas";
import type { NodoResumen } from "../tipos";
import { fechaLarga, sinTildes, slug, useTitulo } from "../util/formato";

function TarjetaDeNodo({ nodo }: { nodo: NodoResumen }) {
  return (
    <Link className="nodo" to={`/apis/${encodeURIComponent(nodo.identificador)}`}>
      <div className="cab">
        <h4>{nodo.nombre}</h4>
      </div>
      <p className="func">{nodo.funcion}</p>
      <div className="meta">
        {nodo.clase === "plataforma" && <span className="tag tag-plataforma">Base · está siempre</span>}
        <span className={MADUREZ[nodo.madurez]}>{nodo.madurez}</span>
        <span className="tag tag-acceso">{ACCESO[nodo.acceso_tipo]}</span>
      </div>
      <div className="pie-tarjeta">
        <span>
          Actualizado el <time dateTime={nodo.leido_en}>{fechaLarga(nodo.leido_en)}</time>
        </span>
      </div>
    </Link>
  );
}

export function Apis() {
  useTitulo("Catálogo de APIs");
  const [params, setParams] = useSearchParams();
  const texto = params.get("q") ?? "";
  const ambito = params.get("ambito") ?? "";
  const nodos = useNodos();
  const ambitos = useAmbitos();

  const cambiarTexto = (valor: string) => {
    const siguientes = new URLSearchParams(params);
    if (valor.trim()) siguientes.set("q", valor);
    else siguientes.delete("q");
    setParams(siguientes, { replace: true });
  };

  const todos = nodos.data ?? [];
  const buscado = sinTildes(texto.trim());
  const lista = todos.filter(
    (n) =>
      (!ambito || n.ambito === ambito) &&
      (!buscado || sinTildes(`${n.nombre} ${n.sigla} ${n.funcion}`).includes(buscado)),
  );
  const orden = [
    ...(ambitos.data ?? []).map((a) => a.nombre),
    ...new Set(todos.map((n) => n.ambito)),
  ].filter((a, i, todas) => todas.indexOf(a) === i && (!ambito || a === ambito));

  return (
    <main>
      <section style={{ paddingBottom: 18 }}>
        <div className="wrap">
          <p className="eyebrow">Catálogo de APIs</p>
          <h2>Los intercambios publicados</h2>
          <p className="lead">
            Cada nodo es un intercambio en el que participa el municipio. La ficha dice qué entrega, con
            quién conversa, en qué estado está y muestra la especificación operación por operación.
          </p>
          <div className="filtros">
            <input
              className="buscador"
              type="search"
              placeholder="Buscar por nombre o institución…"
              aria-label="Buscar intercambios"
              value={texto}
              onChange={(e) => cambiarTexto(e.target.value)}
            />
          </div>

          {nodos.isPending ? (
            <Cargando />
          ) : nodos.isError ? (
            <ErrorDeCarga error={nodos.error} />
          ) : (
            <>
              <p className="conteo">
                {lista.length === todos.length
                  ? todos.length === 1
                    ? "1 intercambio en el catálogo"
                    : `${todos.length} intercambios en el catálogo`
                  : `${lista.length} de ${todos.length} intercambios`}
              </p>
              {todos.length === 0 ? (
                <p className="pendiente">
                  Todavía no hay intercambios publicados. El catálogo va a ir creciendo.
                </p>
              ) : lista.length === 0 ? (
                <p className="pendiente">
                  Ningún intercambio coincide con esa búsqueda. El catálogo todavía es muy corto y va a ir
                  creciendo.
                </p>
              ) : (
                orden.map((nombre) => {
                  const grupo = lista.filter((n) => n.ambito === nombre);
                  if (!grupo.length) return null;
                  const id = `cat-${slug(nombre)}`;
                  return (
                    <div className="grupo-cat" key={nombre} aria-labelledby={id}>
                      <h3 className="grupo-cat__tit" id={id}>
                        {nombre}{" "}
                        <span className="grupo-cat__n">
                          {grupo.length === 1 ? "1 nodo" : `${grupo.length} nodos`}
                        </span>
                      </h3>
                      <div className="grid-nodos">
                        {grupo.map((n) => (
                          <TarjetaDeNodo key={n.identificador} nodo={n} />
                        ))}
                      </div>
                    </div>
                  );
                })
              )}
            </>
          )}
        </div>
      </section>

      <section className="gris">
        <div className="wrap">
          <p className="eyebrow">Cómo leer una tarjeta</p>
          <h2>Qué dice cada parte de la tarjeta</h2>
          <div className="anatomia">
            <div className="nodo" aria-hidden="true">
              <div className="cab">
                <h4>
                  <span className="anota">1</span> Nombre del intercambio
                </h4>
              </div>
              <p className="func">
                <span className="anota">2</span> Qué entrega el intercambio, en una frase.
              </p>
              <div className="meta">
                <span className="anota">3</span>
                <span className="tag tag-dev">En desarrollo</span>
                <span className="tag tag-acceso">Con credencial</span>
              </div>
              <div className="pie-tarjeta">
                <span>
                  <span className="anota">4</span> Actualizado el 15 de septiembre de 2026
                </span>
              </div>
            </div>
            <ol className="anatomia__lista">
              <li>
                <span className="anota">1</span>
                <div>
                  <b>Nombre del intercambio.</b> Lleva a la ficha completa.
                </div>
              </li>
              <li>
                <span className="anota">2</span>
                <div>
                  <b>Qué entrega.</b> La función del intercambio, dicha en una frase.
                </div>
              </li>
              <li>
                <span className="anota">3</span>
                <div>
                  <b>Madurez y acceso.</b> La primera etiqueta dice en qué etapa está:{" "}
                  <span className="tag tag-mad">Deseable</span>,{" "}
                  <span className="tag tag-eval">En evaluación</span>,{" "}
                  <span className="tag tag-dev">En desarrollo</span> u{" "}
                  <span className="tag tag-oper">Operativo</span>. La siguiente dice cómo se entra:{" "}
                  <span className="tag tag-acceso">Abierto</span>,{" "}
                  <span className="tag tag-acceso">Con credencial</span> o{" "}
                  <span className="tag tag-acceso">Clave Única</span>.
                </div>
              </li>
              <li>
                <span className="anota">4</span>
                <div>
                  <b>Fecha de actualización.</b> Es la última vez que el catálogo leyó la ficha. No es la
                  fecha del contrato ni la del servicio.
                </div>
              </li>
            </ol>
          </div>
          <p className="lead">
            El detalle de procedencia del contrato y de cada modo de acceso está en la wiki:{" "}
            <Link to="/wiki/ficha">cómo leer una ficha</Link>.
          </p>
        </div>
      </section>
    </main>
  );
}
