import type { Origen } from "../tipos";
import { fechaHora } from "../util/formato";
import { ORIGEN } from "./etiquetas";

/** La etiqueta que va junto a cada respuesta: de dónde salió y de cuándo es. */
export function EtiquetaDeOrigen({ origen, obtenidoEn }: { origen: Origen; obtenidoEn: string }) {
  return (
    <span className="fuente" data-origen={origen} data-vivo={origen === "fuente" ? "1" : undefined}>
      {ORIGEN[origen]}
      {origen !== "muestra" && ` · ${fechaHora(obtenidoEn)}`}
    </span>
  );
}

/** El recuadro de «De dónde salen estos datos», dicho según la última respuesta. */
export function AvisoDeOrigen({ origen, obtenidoEn }: { origen: Origen; obtenidoEn: string }) {
  if (origen === "fuente") {
    return (
      <div className="aviso aviso-neutro">
        <p>
          <b>Conectado al servicio.</b> La respuesta viene del servicio, en vivo.
        </p>
      </div>
    );
  }
  if (origen === "foto") {
    return (
      <div className="aviso">
        <p>
          <b>El servicio no respondió.</b> Se muestra la copia guardada del {fechaHora(obtenidoEn)}: son
          datos reales, pero pueden no estar al día.
        </p>
      </div>
    );
  }
  return (
    <div className="aviso">
      <p>
        <b>Los datos de esta pantalla son ficticios.</b> Ninguno corresponde a un registro real: este
        ambiente no tiene la fuente configurada.
      </p>
    </div>
  );
}
