import { useMutation } from "@tanstack/react-query";
import { useEffect, useState, type FormEvent } from "react";
import { Link, useLocation } from "react-router";

import { ErrorApi, pedir } from "../../api/cliente";
import { Pendiente } from "../../componentes/Estados";
import { EtiquetaDeOrigen } from "../../componentes/Origen";
import { useSesion } from "../../sesion/Sesion";
import type { Permiso, PermisoProvisional, PermisosRespuesta } from "../../tipos";
import { fechaLarga, pesos } from "../../util/formato";
import type { AlResponder } from "../Servicio";

const RE_PATENTE = /^([A-Z]{2}[0-9]{4}|[A-Z]{4}[0-9]{2})$/;
const RE_PROVISORIA = /^PR[0-9]{4}$/;

const normalizar = (texto: string) => texto.trim().toUpperCase().replace(/[\s.-]/g, "");

type Pedido = { patente: string; procedimiento: string; tramite: string };

/** Entrega datos de personas: exige sesión, pide el trámite que motiva la consulta y avisa que
 * queda registrada. El registro lo escribe el backend; la pantalla solo lo dice. */
export function ConsultaPermisos({ alResponder }: { alResponder: AlResponder }) {
  const { token, yo } = useSesion();
  const { pathname } = useLocation();

  if (!token || !yo) {
    return (
      <Pendiente>
        Esta consulta entrega datos de personas, así que exige sesión con un perfil del nodo.{" "}
        <Link to="/entrar" state={{ volverA: pathname }}>
          Entrar
        </Link>
        .
      </Pendiente>
    );
  }
  return <Formulario alResponder={alResponder} />;
}

function Formulario({ alResponder }: { alResponder: AlResponder }) {
  const [patente, setPatente] = useState("");
  const [procedimiento, setProcedimiento] = useState("");
  const [tramite, setTramite] = useState("");
  const [invalida, setInvalida] = useState("");

  const consulta = useMutation({
    mutationFn: ({ patente, procedimiento, tramite }: Pedido) =>
      pedir<PermisosRespuesta>(`/servicios/permisos/${encodeURIComponent(patente)}`, {
        cabeceras: {
          "X-Procedimiento": procedimiento,
          ...(tramite ? { "X-Id-Tramite": tramite } : {}),
        },
      }),
  });

  useEffect(() => {
    if (consulta.data) alResponder(consulta.data.origen, consulta.data.obtenido_en);
  }, [consulta.data, alResponder]);

  const enviar = (evento: FormEvent) => {
    evento.preventDefault();
    const p = normalizar(patente);
    if (!RE_PATENTE.test(p) && !RE_PROVISORIA.test(p)) {
      setInvalida(
        "Esa patente no tiene un formato válido. Son dos letras y cuatro dígitos, o cuatro letras y dos dígitos. Para una provisoria, PR y cuatro dígitos.",
      );
      consulta.reset();
      return;
    }
    setInvalida("");
    consulta.mutate({ patente: p, procedimiento: procedimiento.trim(), tramite: tramite.trim() });
  };

  return (
    <div>
      <div className="aviso">
        <p>
          <b>Cada consulta queda registrada</b> con tu nombre, la patente y el trámite que la motiva.
        </p>
      </div>
      <form onSubmit={enviar}>
        <div className="campo">
          <label htmlFor="patente">Patente</label>
          <input
            className="buscar-grande"
            id="patente"
            autoComplete="off"
            spellCheck={false}
            style={{ textTransform: "uppercase", letterSpacing: 2, maxWidth: 340 }}
            placeholder="BDPF18"
            aria-describedby="pista-patente"
            value={patente}
            onChange={(e) => setPatente(e.target.value)}
            required
          />
          <p className="pista" id="pista-patente">
            Sin guiones ni puntos. Para una provisoria, <code>PR</code> y cuatro dígitos.
          </p>
        </div>
        <div className="campo">
          <label htmlFor="procedimiento">Trámite que motiva la consulta</label>
          <input
            id="procedimiento"
            value={procedimiento}
            onChange={(e) => setProcedimiento(e.target.value)}
            required
          />
        </div>
        <div className="campo">
          <label htmlFor="tramite">Número del trámite (opcional)</label>
          <input id="tramite" value={tramite} onChange={(e) => setTramite(e.target.value)} />
        </div>
        <p>
          <button className="btn btn-p" type="submit" disabled={consulta.isPending}>
            {consulta.isPending ? "Consultando…" : "Consultar"}
          </button>
        </p>
      </form>

      <div aria-live="polite">
        {invalida ? (
          <p className="pendiente">{invalida}</p>
        ) : consulta.isError ? (
          <ErrorDePermisos error={consulta.error} patente={consulta.variables?.patente ?? ""} />
        ) : consulta.data ? (
          <Resultado respuesta={consulta.data} patente={consulta.variables?.patente ?? ""} />
        ) : null}
      </div>
    </div>
  );
}

function ErrorDePermisos({ error, patente }: { error: unknown; patente: string }) {
  if (error instanceof ErrorApi) {
    if (error.status === 404) {
      return (
        <p className="pendiente">
          No hay ningún vehículo inscrito con la patente <b>{patente}</b>.
        </p>
      );
    }
    if (error.codigo === "FUENTE_NO_DISPONIBLE") {
      return (
        <p className="pendiente">
          El servicio de permisos de circulación no está respondiendo. No se muestran datos de
          reemplazo: vuelve a intentarlo en un momento.
        </p>
      );
    }
    return <p className="pendiente">{error.message}</p>;
  }
  return <p className="pendiente">No se pudo consultar el servicio.</p>;
}

function Resultado({ respuesta, patente }: { respuesta: PermisosRespuesta; patente: string }) {
  const { datos, origen, obtenido_en } = respuesta;
  const etiqueta = <EtiquetaDeOrigen origen={origen} obtenidoEn={obtenido_en} />;

  if (datos.tipo === "provisoria") {
    const lista = datos.provisionales ?? [];
    if (!lista.length) {
      return (
        <p className="pendiente">
          No hay permisos provisionales para <b>{patente}</b>. {etiqueta}
        </p>
      );
    }
    return (
      <>
        <p className="conteo">
          {lista.length === 1 ? "1 permiso provisional" : `${lista.length} permisos provisionales`}{" "}
          {etiqueta}
        </p>
        {lista.map((p, i) => (
          <Provisional key={i} patente={patente} permiso={p} />
        ))}
      </>
    );
  }

  const vehiculo = datos.vehiculo;
  const permisos = datos.permisos ?? [];
  if (!vehiculo) {
    return (
      <p className="pendiente">
        No hay ningún vehículo inscrito con la patente <b>{patente}</b>. {etiqueta}
      </p>
    );
  }
  const vigente = permisos.find((p) => p.estado === "VIGENTE");
  return (
    <>
      <p className="conteo">
        {permisos.length === 1 ? "1 permiso registrado" : `${permisos.length} permisos registrados`}{" "}
        {etiqueta}
      </p>
      <div className="res">
        <div className="res-cab">
          <h3>{vehiculo.patente}</h3>
          {vigente ? (
            <span className="tag tag-dev">Permiso {vigente.anio} vigente</span>
          ) : (
            <span className="tag tag-mad">Sin permiso vigente</span>
          )}
        </div>
        <div className="jerarquia" style={{ borderTop: 0, paddingTop: 6, marginTop: 6 }}>
          <b>
            {vehiculo.marca} {vehiculo.modelo}
          </b>
          {vehiculo.color && <span className="sep">·</span>}
          {vehiculo.color}
          {vehiculo.anio_fabricacion && <span className="sep">·</span>}
          {vehiculo.anio_fabricacion}
          {vehiculo.tipo && <span className="sep">·</span>}
          {vehiculo.tipo}
        </div>
      </div>
      {permisos.length ? (
        permisos.map((p) => <TarjetaDePermiso key={`${p.anio}-${p.comuna.cut}`} permiso={p} />)
      ) : (
        <p className="pendiente">Este vehículo no tiene permisos de circulación registrados.</p>
      )}
    </>
  );
}

function TarjetaDePermiso({ permiso }: { permiso: Permiso }) {
  return (
    <div className="res">
      <div className="res-cab">
        <h3>Permiso {permiso.anio}</h3>
        <span className={permiso.estado === "VIGENTE" ? "tag tag-dev" : "tag"}>{permiso.estado}</span>
      </div>
      <div className="jerarquia" style={{ borderTop: 0, paddingTop: 6, marginTop: 6 }}>
        Recaudado por <b>{permiso.comuna.nombre}</b> <code>{permiso.comuna.cut}</code>
        <span className="sep">·</span> Total <b>{pesos(permiso.monto_total)}</b>
        {permiso.vigente_hasta && (
          <>
            <span className="sep">·</span> Vigente hasta <b>{fechaLarga(permiso.vigente_hasta)}</b>
          </>
        )}
      </div>
      {permiso.cuotas.length > 0 && (
        <div className="tabla-ancha">
          <table>
            <thead>
              <tr>
                <th></th>
                <th>Monto</th>
                <th>Pagada</th>
                <th>Medio</th>
              </tr>
            </thead>
            <tbody>
              {permiso.cuotas.map((c) => (
                <tr key={c.numero}>
                  <td>Cuota {c.numero}</td>
                  <td>{pesos(c.monto)}</td>
                  <td>{fechaLarga(c.fecha_pago)}</td>
                  <td>{c.medio_pago || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function Provisional({ patente, permiso }: { patente: string; permiso: PermisoProvisional }) {
  return (
    <div className="res">
      <div className="res-cab">
        <h3>{patente}</h3>
        <span className="res-nivel">Permiso provisional</span>
      </div>
      <div className="jerarquia" style={{ borderTop: 0, paddingTop: 6, marginTop: 6 }}>
        <b>
          {permiso.marca || "—"} {permiso.modelo}
        </b>
        <span className="sep">·</span> {permiso.anio}, semestre {permiso.semestre}
        <span className="sep">·</span> {permiso.comuna.nombre} <code>{permiso.comuna.cut}</code>
      </div>
      <div className="jerarquia">
        Titular <b>{permiso.titular.razon_social}</b> <code>{permiso.titular.rut}</code>
      </div>
    </div>
  );
}
