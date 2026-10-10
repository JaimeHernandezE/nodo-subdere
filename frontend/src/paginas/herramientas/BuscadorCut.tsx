import { useQuery } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router";

import { esEstado } from "../../api/cliente";
import { buscarCut } from "../../api/consultas";
import { Cargando, ErrorDeCarga } from "../../componentes/Estados";
import { EtiquetaDeOrigen } from "../../componentes/Origen";
import type { UnidadTerritorial } from "../../tipos";
import type { AlResponder } from "../Servicio";

const EJEMPLOS = ["Talca", "Magallanes", "Los Ríos", "13101", "1101", "07", "141"];
const NIVEL = { region: "Región", provincia: "Provincia", comuna: "Comuna" } as const;

function useDemorado(valor: string, ms: number) {
  const [demorado, setDemorado] = useState(valor);
  useEffect(() => {
    const t = setTimeout(() => setDemorado(valor), ms);
    return () => clearTimeout(t);
  }, [valor, ms]);
  return demorado;
}

/** Qué falta para poder buscar, o `null` si el texto ya se puede consultar. */
function faltaParaBuscar(texto: string): string | null {
  if (!texto) return "";
  if (/^\d+$/.test(texto)) {
    return texto.length > 5
      ? "Ese código es demasiado largo. Son dos dígitos para una región, tres para una provincia y cinco para una comuna."
      : null;
  }
  return texto.length < 2 ? "" : null;
}

export function BuscadorCut({ alResponder }: { alResponder: AlResponder }) {
  const [params, setParams] = useSearchParams();
  const [texto, setTexto] = useState(params.get("q") ?? "");
  const campo = useRef<HTMLInputElement>(null);
  const buscado = useDemorado(texto.trim(), 160);
  const falta = faltaParaBuscar(buscado);

  const consulta = useQuery({
    queryKey: ["cut", buscado],
    queryFn: ({ signal }) => buscarCut(buscado, signal),
    enabled: falta === null,
  });

  useEffect(() => {
    setParams(buscado ? { q: buscado } : {}, { replace: true });
  }, [buscado, setParams]);

  useEffect(() => {
    if (consulta.data) alResponder(consulta.data.origen, consulta.data.obtenido_en);
  }, [consulta.data, alResponder]);

  const elegir = (ejemplo: string) => {
    setTexto(ejemplo);
    campo.current?.focus();
  };

  let resultado = null;
  if (falta) {
    resultado = <p className="pendiente">{falta}</p>;
  } else if (falta === null) {
    if (consulta.isPending) resultado = <Cargando texto="Buscando…" />;
    else if (consulta.isError) {
      resultado = esEstado(consulta.error, 404) ? (
        <p className="pendiente">Ningún lugar tiene ese código.</p>
      ) : (
        <ErrorDeCarga error={consulta.error} />
      );
    } else if (!consulta.data.datos.length) {
      resultado = <p className="pendiente">Ningún lugar coincide con ese nombre.</p>;
    } else {
      const { datos, origen, obtenido_en } = consulta.data;
      resultado = (
        <>
          <p className="conteo">
            {datos.length === 1 ? "1 resultado" : `${datos.length} resultados`}{" "}
            <EtiquetaDeOrigen origen={origen} obtenidoEn={obtenido_en} />
          </p>
          {datos.map((u) => (
            <Unidad key={`${u.nivel}-${u.codigo}`} unidad={u} />
          ))}
        </>
      );
    }
  }

  return (
    <div>
      <div
        className="cut-esquema"
        role="img"
        aria-label="El código 07101 se lee así: 07 es la región del Maule, 071 la provincia de Talca y 07101 la comuna de Talca."
      >
        <div className="cut-seg cut-reg">
          <code>07</code>
          <b>Región</b>
          <span>07 · Maule</span>
        </div>
        <div className="cut-seg cut-prov">
          <code>1</code>
          <b>Provincia</b>
          <span>071 · Talca</span>
        </div>
        <div className="cut-seg cut-com">
          <code>01</code>
          <b>Comuna</b>
          <span>07101 · Talca</span>
        </div>
      </div>
      <p className="pista">
        Cada código empieza por el de su región y su provincia: dos dígitos son una región, tres una
        provincia y cinco una comuna. Los ceros a la izquierda son parte del código, pero si los omites
        igual se encuentra.
      </p>

      <div style={{ marginTop: 22 }}>
        <label htmlFor="buscar-cut" className="eyebrow" style={{ display: "block", marginBottom: 8 }}>
          Comuna, provincia, región o código
        </label>
        <input
          ref={campo}
          className="buscar-grande"
          id="buscar-cut"
          type="search"
          autoComplete="off"
          placeholder="Talca, Maule, 13101…"
          aria-describedby="ejemplos-cut"
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
        />
        <p className="pista" id="ejemplos-cut">
          Prueba con{" "}
          {EJEMPLOS.map((e) => (
            <button key={e} type="button" className="ej-pat" onClick={() => elegir(e)}>
              {e}
            </button>
          ))}
        </p>
      </div>

      <div aria-live="polite">{resultado}</div>
    </div>
  );
}

function Unidad({ unidad }: { unidad: UnidadTerritorial }) {
  const [copiado, setCopiado] = useState(false);
  const copiar = () => {
    navigator.clipboard?.writeText(unidad.codigo).then(() => {
      setCopiado(true);
      setTimeout(() => setCopiado(false), 1400);
    });
  };
  const partes = [
    unidad.provincia && (
      <>
        Provincia de <b>{unidad.provincia.nombre}</b> <code>{unidad.provincia.codigo}</code>
      </>
    ),
    unidad.region && (
      <>
        Región <b>{unidad.region.nombre}</b> <code>{unidad.region.codigo}</code>
      </>
    ),
  ].filter(Boolean);

  return (
    <div className="res">
      <div className="res-cab">
        <h3>{unidad.nombre}</h3>
        <span className="res-nivel">{NIVEL[unidad.nivel]}</span>
      </div>
      <div className="codigo-cut">
        <code>{unidad.codigo}</code>
        <button className="btn-copiar" type="button" data-ok={copiado ? "1" : undefined} onClick={copiar}>
          {copiado ? "Copiado" : "Copiar"}
        </button>
      </div>
      {partes.length > 0 && (
        <div className="jerarquia">
          {partes.map((p, i) => (
            <span key={i}>
              {i > 0 && <span className="sep">· </span>}
              {p}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
