import { ErrorApi } from "../../api/cliente";
import type { Rol, Yo } from "../../tipos";

const ORDEN: Rol[] = ["lector", "editor", "curador", "administrador"];

/** El mismo orden acumulativo que `RolMinimo` en el backend. La pantalla solo esconde lo que el
 * backend rechazaría igual. */
export function puede(yo: Yo | null, minimo: Rol): boolean {
  return !!yo && ORDEN.indexOf(yo.rol) >= ORDEN.indexOf(minimo);
}

export function gestionaPerfiles(yo: Yo | null): boolean {
  return !!yo && (yo.rol === "administrador" || yo.es_encargado);
}

export type Resultado = { texto: string; registro?: string };

/** Lo que cambió y dónde quedó registrado. La bitácora no tiene endpoint de lectura: se dice qué
 * se registró. */
export function Registrado({ resultado, autor }: { resultado: Resultado | null; autor: string | undefined }) {
  if (!resultado) return null;
  return (
    <div className="aviso aviso-ok" role="status">
      <p>
        {resultado.texto}. Quedó registrado en {resultado.registro ?? "la bitácora"}
        {autor ? ` a nombre de ${autor}` : ""}.
      </p>
    </div>
  );
}

export function ErrorDeAccion({ error }: { error: unknown }) {
  if (!error) return null;
  const mensaje =
    error instanceof ErrorApi ? error.message : "No se pudo completar la acción. Vuelve a intentarlo.";
  const detalles = error instanceof ErrorApi ? error.detalles : [];
  return (
    <div className="aviso" role="alert">
      <p>{mensaje}</p>
      {detalles.length > 0 && (
        <ul>
          {detalles.map((d, i) => (
            <li key={i}>
              {d.campo ? <code>{d.campo}</code> : null} {d.mensaje ?? ""}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function SinPermiso() {
  return (
    <div className="pendiente" role="status">
      Tu rol no permite ver esta sección. Si la necesitas, pídeselo a un administrador del nodo.
    </div>
  );
}
