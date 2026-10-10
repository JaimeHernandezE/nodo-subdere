import { Link } from "react-router";

import { useTitulo } from "../util/formato";

export function Participar() {
  useTitulo("Cómo participar");
  return (
    <main>
      <section>
        <div className="wrap">
          <p className="eyebrow">Cómo participar</p>
          <h2>Empieza a usar el nodo desde donde estás</h2>
          <p className="lead">
            No hace falta cambiar de sistema ni pedir permiso para empezar. Hay dos momentos que conviene
            no mezclar:
          </p>
          <ul className="lead">
            <li>
              <strong>Construir y practicar</strong>, con datos inventados. No le pide permiso a nadie.
            </li>
            <li>
              <strong>Trabajar con datos de un municipio.</strong> Para eso el municipio acepta los{" "}
              <Link to="/wiki/glosario#terminos-y-condiciones">Términos y Condiciones</Link> con SUBDERE
              y recibe una <Link to="/wiki/glosario#credencial">credencial</Link> a su nombre.
            </li>
          </ul>
          <p className="lead">
            El detalle de cada paso está en <Link to="/wiki/conectar">conectar un sistema</Link>.
          </p>
        </div>
      </section>

      <section className="gris">
        <div className="wrap">
          <div className="cols-3">
            <div className="card">
              <div className="num">MUNICIPIOS</div>
              <h3>Quiero usar el nodo</h3>
              <p>
                No necesitas cambiar de sistema. Si el tuyo cumple lo publicado, se conecta directo al
                nodo; para trabajar con datos reales basta aceptar los Términos y Condiciones y recibir la
                credencial.
              </p>
              <p>
                <Link to="/wiki/conectar">Cómo conectar tu sistema →</Link>
              </p>
            </div>
            <div className="card">
              <div className="num">PROVEEDORES</div>
              <h3>Quiero conectar mi sistema</h3>
              <p>
                Todo lo que publicamos es público, y cualquiera puede construir a partir de ahí. La
                pantalla del propio SGM entra por la{" "}
                <Link className="termino" to="/wiki/glosario#puerta-de-acceso">
                  misma puerta
                </Link>{" "}
                que tú: nadie tiene atajos.
              </p>
              <p>
                <Link to="/apis">Ver el catálogo de APIs →</Link> ·{" "}
                <Link to="/wiki/ficha">Cómo leer una ficha →</Link>
              </p>
            </div>
            <div className="card">
              <div className="num">INSTITUCIONES</div>
              <h3>Recibo información de municipios</h3>
              <p>
                En vez de recibir envíos sueltos de trescientos y tantos municipios, recibes de uno solo.
                No tienes que cambiar nada de tu lado: el nodo te entrega en el formato que ya aceptas
                hoy.
              </p>
              <p className="pendiente" style={{ marginTop: 12 }}>
                Pendiente: todavía no está levantado qué envían los municipios a cada institución, ni por
                qué canal.
              </p>
              <p>
                <Link to="/wiki/recorrido">Cómo funciona un intercambio →</Link>
              </p>
            </div>
          </div>
        </div>
      </section>

      <section>
        <div className="wrap">
          <p className="eyebrow">Practicar y operar</p>
          <h2>Practica sin pedir permiso; opera con credencial</h2>
          <ul className="lead">
            <li>
              <strong>Para practicar</strong> se usan datos inventados, y no hace falta aceptar nada.
            </li>
            <li>
              <strong>Para trabajar de verdad</strong> hace falta la credencial a nombre del municipio.
              Sin ella no se trabaja con datos reales.
            </li>
            <li>
              Lo que el servicio promete entregar es lo mismo en los dos casos; cambian los datos y el
              permiso.
            </li>
          </ul>
          <p>
            <Link to="/wiki/conectar">Ver la comparación completa →</Link>
          </p>
        </div>
      </section>

      <section className="gris">
        <div className="wrap">
          <p className="eyebrow">Dónde estamos</p>
          <h2>Qué está listo y qué falta</h2>
          <table>
            <thead>
              <tr>
                <th>Qué cosa</th>
                <th>Cómo está</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Qué entrega cada intercambio</td>
                <td>
                  <span className="tag tag-dev">Parcial</span> — Publicado para los Códigos Únicos
                  Territoriales (copia exacta) y los permisos de circulación (propuesta reconstruida). Los
                  demás se suman cuando tengan contrato, pantalla y entrada de wiki. Ver el{" "}
                  <Link to="/wiki#intercambios">índice de intercambios</Link>.
                </td>
              </tr>
              <tr>
                <td>Zona de práctica</td>
                <td>
                  <span className="tag tag-dev">Por construir</span> — La{" "}
                  <Link to="/wiki/glosario#zona-de-practica">zona de práctica</Link> del nodo, con datos
                  inventados y una por servicio, todavía no existe.
                </td>
              </tr>
              <tr>
                <td>Términos y Condiciones y credencial</td>
                <td>
                  <span className="tag tag-dev">Por definir</span> — Lo que un municipio acepta con
                  SUBDERE para trabajar con sus datos, y que habilita la credencial. Todavía no está
                  redactado.
                </td>
              </tr>
              <tr>
                <td>Quién entra y cómo se controla</td>
                <td>
                  <span className="tag tag-dev">Propuesta</span> — Una sola{" "}
                  <Link className="termino" to="/wiki/glosario#puerta-de-acceso">
                    puerta
                  </Link>{" "}
                  que revisa quién pide, cuánto puede pedir y deja registro. Está diseñada, pero no
                  construida.
                </td>
              </tr>
              <tr>
                <td>El catálogo y sus fichas</td>
                <td>
                  <span className="tag">Primera versión</span> — Esto que estás mirando.
                </td>
              </tr>
            </tbody>
          </table>
          <p style={{ marginTop: 16 }}>Actualizamos esta tabla a medida que cada cosa avanza.</p>
        </div>
      </section>

      <section>
        <div className="wrap">
          <p className="eyebrow">Ayuda</p>
          <h2>¿Algo no se entiende?</h2>
          <p className="lead">
            Si una explicación no se entiende, falta una entrada en la wiki o encontraste un error,
            queremos saberlo.
          </p>
          <p className="pendiente">Pendiente: todavía no hay un canal de contacto publicado.</p>
        </div>
      </section>
    </main>
  );
}
