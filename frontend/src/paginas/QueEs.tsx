import { Link } from "react-router";

import { useTitulo } from "../util/formato";

const NOTA_PLATAFORMA =
  "https://github.com/JaimeHernandezE/nodo-subdere/blob/main/docs/plataforma-control.md";

export function QueEs() {
  useTitulo("Qué es el nodo");
  return (
    <main>
      <section>
        <div className="wrap">
          <p className="eyebrow">Descripción general</p>
          <h2>Cómo funciona el nodo</h2>
          <p className="lead">
            El Nodo SUBDERE se presenta en tres piezas —el catálogo de <Link to="/apis">APIs</Link>, el
            de <Link to="/servicios">servicios</Link> y la <Link to="/wiki">wiki</Link>—. Esta página
            explica cómo funciona el intercambio que las sostiene.
          </p>
          <p className="lead">
            El municipio intercambia información con otras instituciones de dos maneras:{" "}
            <strong>entrega</strong> lo que le piden y <strong>pregunta</strong> por lo que necesita. Hoy
            esa información está dispersa: cada intercambio se hace de una forma distinta con cada
            institución, y casi ninguno tiene un estándar publicado. El nodo es el punto donde esos
            intercambios se cruzan: publica el estándar de cada uno y los expone por una sola interfaz.
          </p>
          <p className="lead">
            Para cada intercambio, el nodo publica de antemano{" "}
            <strong>qué se entrega y en qué forma</strong>. Eso es lo que llamamos el estándar, y está
            escrito de manera que un programa pueda leerlo, no solo una persona.
          </p>
          <p className="lead">
            <strong>Las entregas las hace el sistema del municipio.</strong> Las aplicaciones del
            catálogo de servicios permiten probar algunas de las APIs desde una pantalla. Usan las mismas
            APIs publicadas, así que un sistema que se conecte a ellas obtendrá los mismos resultados.
          </p>
        </div>
      </section>

      <section className="gris">
        <div className="wrap">
          <p className="eyebrow">Un ejemplo</p>
          <h2>Tres municipios, tres sistemas, el mismo informe</h2>
          <p className="lead">
            Todos los municipios tienen que entregar el mismo reporte a fin de mes. Uno usa el SGM, otro
            un sistema que armó su propia unidad de informática y un tercero se lo compró a un
            proveedor. Desde ahí en adelante el camino es idéntico:{" "}
            <strong>
              al nodo no le importa quién hizo el sistema, solo que cumpla lo que está publicado.
            </strong>
          </p>
          <p className="lead">
            El{" "}
            <a href="https://jaimehernandeze.github.io/sgm-nueva-arquitectura/">
              <strong>SGM</strong>
            </a>{" "}
            es el Sistema de Gestión Municipal que desarrolla SUBDERE. Es el primer sistema conectado al
            nodo y sirve como referencia para los demás.
          </p>
          <div className="cols-2">
            <div className="card">
              <h3>Publicamos el estándar de antemano</h3>
              <p>
                En SUBDERE publicamos cómo debe venir cada informe que recibimos por mandato y qué reglas
                le aplicamos, con un número de versión. Si la regla cambia, publicamos una versión nueva
                y queda claro cuál rige.
              </p>
            </div>
            <div className="card">
              <h3>Revisar es gratis y se puede repetir</h3>
              <p>
                El sistema del municipio puede revisar su informe las veces que quiera, y los errores
                aparecen en la misma pantalla donde el funcionario está trabajando. En este paso no sale
                nada del municipio.
              </p>
            </div>
            <div className="card">
              <h3>Enviar lo decide el municipio</h3>
              <p>
                Recién cuando el informe está limpio, el funcionario responsable autoriza el envío.
                Entregar sigue siendo una decisión del municipio, no algo que ocurre solo.
              </p>
            </div>
            <div className="card">
              <h3>Y queda comprobante</h3>
              <p>
                Qué se envió, cuándo, a quién, y contra qué versión de la regla se revisó. Se puede
                consultar después, en el mismo lugar para todos los intercambios.
              </p>
            </div>
          </div>
          <p className="lead" style={{ marginTop: 22 }}>
            Ese es el camino cuando el municipio <strong>entrega</strong>. Cuando en cambio{" "}
            <strong>pregunta</strong> —el código de una comuna, el estado de una compra— no hay nada que
            autorizar: el sistema pregunta y el nodo responde, y queda registrado quién preguntó qué.
          </p>
          <p>
            Más detalle en la wiki: <Link to="/wiki/recorrido">cómo funciona un intercambio →</Link>
          </p>
        </div>
      </section>

      <section>
        <div className="wrap">
          <p className="eyebrow">Qué revisa</p>
          <h2>La información que recopilamos, estandarizada aquí</h2>
          <p className="lead">
            Toda la información que recopilamos como SUBDERE desde las municipalidades queda
            estandarizada en el nodo: cada informe tiene su estándar publicado, y el nodo lo revisa antes
            de que salga del municipio. Cada entrega dice qué se revisó.
          </p>
          <table>
            <thead>
              <tr>
                <th>Con qué revisa</th>
                <th>Qué hace</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <strong>Con nuestras reglas</strong>
                </td>
                <td>Compara el informe con el estándar que publicamos para ese intercambio.</td>
              </tr>
              <tr>
                <td>
                  <strong>Con las reglas de la norma</strong>
                </td>
                <td>
                  Aplica lo que dice la norma que obliga la entrega, escrito como regla y mantenido al
                  día.
                </td>
              </tr>
            </tbody>
          </table>
          <p className="alt">
            (Pendiente de discutir: qué hace el nodo con lo que las municipalidades envían a otros
            organismos del Estado. Todavía no está levantado qué se envía, a quién ni por qué canal.)
          </p>
        </div>
      </section>

      <section className="gris">
        <div className="wrap">
          <p className="eyebrow">Por dónde pasa todo</p>
          <h2>Una sola puerta, y queda registro de quién entró</h2>
          <p className="lead">
            Detrás de cada API del catálogo hay un <strong>servicio</strong>: el sistema que atiende ese
            intercambio. Cuando el municipio entrega, el servicio revisa el informe con su estándar,
            devuelve las observaciones, recibe el envío autorizado y emite el comprobante; cuando el
            municipio pregunta, el servicio responde. Las aplicaciones del catálogo de servicios son
            pantallas que usan estos servicios.
          </p>
          <p className="alt">
            (Para discutir con el equipo: «servicio» nombra dos cosas en el sitio, el sistema detrás de
            cada API y la pestaña «Servicios», que reúne aplicaciones. Una opción es renombrar la pestaña
            a «Aplicaciones».)
          </p>
          <p className="lead">
            Todos los sistemas llegan a los servicios por la{" "}
            <Link className="termino" to="/wiki/glosario#puerta-de-acceso">
              misma puerta
            </Link>
            , que comprueba quién llama y deja constancia.{" "}
            <strong>Esto todavía no está construido:</strong> es el diseño que se propone.
          </p>

          <div
            className="flujo"
            role="img"
            aria-label="El sistema del municipio pide un permiso de entrada, llama a la puerta con ese permiso, la puerta comprueba y deja pasar al servicio, y queda registro"
          >
            <div className="flujo__caja">
              <strong>El sistema del municipio</strong>
              <span>Entrega o pregunta</span>
            </div>
            <div className="flujo__flecha" aria-hidden="true">→</div>
            <div className="flujo__caja">
              <strong>Pide un permiso</strong>
              <span>Con la credencial del municipio</span>
            </div>
            <div className="flujo__flecha" aria-hidden="true">→</div>
            <div className="flujo__caja">
              <strong>La puerta</strong>
              <span>Comprueba quién es y qué puede pedir</span>
            </div>
            <div className="flujo__flecha" aria-hidden="true">→</div>
            <div className="flujo__caja">
              <strong>El servicio</strong>
              <span>Responde o recibe</span>
            </div>
            <div className="flujo__flecha" aria-hidden="true">→</div>
            <div className="flujo__caja">
              <strong>Queda registro</strong>
              <span>Quién pidió qué, y cuándo</span>
            </div>
          </div>

          <p className="lead" style={{ marginTop: 20 }}>
            Dos cosas que conviene notar. La primera: <strong>nadie tiene atajos.</strong> La pantalla
            del propio SGM entra por esta misma puerta, igual que el sistema de cualquier municipio o de
            cualquier proveedor. La segunda: el permiso de entrada es temporal y se pide cada vez, así que
            revocarle el acceso a alguien es inmediato y no depende de avisarle a nadie.
          </p>
          <p className="lead">
            La{" "}
            <Link className="termino" to="/wiki/glosario#puerta-de-acceso">
              puerta
            </Link>{" "}
            tiene dos partes: una que sabe <strong>quién es cada municipio o sistema</strong> y le
            entrega su permiso, y otra que <strong>revisa ese permiso en cada llamada</strong>, limita
            cuánto se puede pedir y lo anota. No decide nada del contenido: validar el informe, devolver
            observaciones y emitir el comprobante lo hace cada servicio. La{" "}
            <a href={NOTA_PLATAFORMA}>nota de la plataforma de control</a> tiene el detalle técnico.
          </p>
          <p>
            Más detalle en la wiki:{" "}
            <Link to="/wiki/glosario#puerta-de-acceso">qué es la puerta de acceso →</Link>
          </p>
        </div>
      </section>

      <section>
        <div className="wrap">
          <p className="eyebrow">Probar y operar</p>
          <h2>Un espacio para practicar y otro para operar</h2>
          <p className="lead">
            Lo que el servicio promete entregar es idéntico en las dos; lo que cambia son los datos y el
            permiso que hace falta.
          </p>
          <table>
            <thead>
              <tr>
                <th></th>
                <th>Para practicar</th>
                <th>Para trabajar de verdad</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <strong>Quién</strong>
                </td>
                <td>Cualquiera que esté construyendo un sistema</td>
                <td>El municipio, o el sistema que él autorice</td>
              </tr>
              <tr>
                <td>
                  <strong>Con qué datos</strong>
                </td>
                <td>Datos inventados; ninguno de un municipio real</td>
                <td>Los datos del municipio que autorizó</td>
              </tr>
              <tr>
                <td>
                  <strong>¿Hace falta el Uso de Términos y Condiciones?</strong>
                </td>
                <td>No</td>
                <td>Sí, con SUBDERE</td>
              </tr>
              <tr>
                <td>
                  <strong>Permiso</strong>
                </td>
                <td>Abierto o de prueba, según el servicio</td>
                <td>
                  Una credencial a nombre del municipio, que sale del Uso de Términos y Condiciones
                </td>
              </tr>
            </tbody>
          </table>
          <div className="aviso">
            <p>
              <b>Todavía no existe.</b> La idea es que cada servicio publicado tenga su zona de práctica
              —un <em>sandbox</em>— con datos inventados, para que cualquiera pueda construir sin pedir
              permiso ni aceptar términos y condiciones. Para trabajar con datos de un municipio sí hace
              falta el Uso de Términos y Condiciones con SUBDERE, que es lo que habilita la credencial.
              Hoy no hay ninguna zona de práctica funcionando; cada ficha del catálogo dice en qué estado
              está.
            </p>
          </div>
        </div>
      </section>

      <section className="gris">
        <div className="wrap">
          <p className="eyebrow">Casos</p>
          <h2>Cómo se conecta un sistema en la práctica</h2>
          <div className="cols-3">
            <div className="card">
              <div className="num num-letra">A</div>
              <h3>El SGM, sistema de referencia</h3>
              <p>
                El SGM es el primer sistema de gestión municipal conectado al nodo y el primero en cumplir
                sus estándares. Funciona como sistema de referencia y de prueba: con él se comprueba que
                cada estándar publicado funciona antes de que se conecten otros sistemas.
              </p>
            </div>
            <div className="card">
              <div className="num num-letra">B</div>
              <h3>Un municipio con otro sistema</h3>
              <p>
                Lo publicado es público y cualquiera puede construir contra ello: el proveedor del
                municipio o su propio equipo de desarrollo. Cada estándar tendrá una zona de práctica con
                datos inventados para probar antes de conectarse. Para trabajar con datos reales hace
                falta el Uso de Términos y Condiciones y la credencial.
              </p>
            </div>
            <div className="card">
              <div className="num num-letra">C</div>
              <h3>Cuando cambia un estándar</h3>
              <p>
                Cuando SUBDERE publique una versión nueva de un estándar, avisará con antelación a quienes
                estén conectados, y la versión anterior seguirá funcionando durante un período de gracia,
                para que cada sistema se actualice sin interrumpir sus entregas.
              </p>
              <p className="alt">
                (Para definir con el equipo: cómo se avisa a las entidades conectadas y cuánto dura el
                período de gracia.)
              </p>
            </div>
          </div>
          <p style={{ marginTop: 22 }}>
            Más detalle en la wiki: <Link to="/wiki/conectar">conectar un sistema →</Link>
          </p>
        </div>
      </section>
    </main>
  );
}
