import type { ReactNode } from "react";

import { ErrorApi } from "../api/cliente";

export function Pendiente({ children }: { children: ReactNode }) {
  return <div className="pendiente">{children}</div>;
}

export function Cargando({ texto = "Cargando…" }: { texto?: string }) {
  return (
    <p className="sin-params" role="status">
      {texto}
    </p>
  );
}

/** Un error de carga que no es «no existe»: se dice qué pasó, sin pantalla en blanco. */
export function ErrorDeCarga({ error }: { error: unknown }) {
  const mensaje =
    error instanceof ErrorApi ? error.message : "Algo falló al pedir esta información al nodo.";
  return (
    <Pendiente>
      No se pudo cargar: {mensaje} Vuelve a intentarlo en un momento.
    </Pendiente>
  );
}
