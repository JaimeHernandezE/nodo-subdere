import { Link } from "react-router";

import { useTitulo } from "../util/formato";

export function Portada() {
  useTitulo();
  return (
    <main>
      <div className="hero">
        <div className="wrap">
          <p className="eyebrow">Subsecretaría de Desarrollo Regional y Administrativo</p>
          <h1>Nodo SUBDERE, la plataforma de encuentro municipal</h1>
          <p>
            Reúne en un solo sitio los estándares del dominio municipal, en tres piezas: el{" "}
            <strong>catálogo de APIs</strong>, donde cada intercambio queda publicado como contrato para
            quien construye; el <strong>catálogo de servicios</strong>, con aplicaciones que ponen esas
            mismas APIs al alcance de cualquier funcionario; y la <strong>wiki</strong>, que explica cómo
            se usa cada uno.
          </p>
          <div className="acciones">
            <Link className="btn btn-p" to="/que-es">
              Cómo funciona
            </Link>
            <Link className="btn btn-s" to="/participar">
              Cómo participar
            </Link>
          </div>
        </div>
      </div>

      <section>
        <div className="wrap">
          <p className="eyebrow">Qué propone</p>
          <h2>Una forma común de pedir y entregar información municipal</h2>
          <p className="lead">
            Hoy cada institución que le pide información a un municipio define su propio formato, su
            propia página y su propia clave, y cada comprobante queda en una plataforma distinta. El Nodo
            SUBDERE propone una forma común: qué se entrega y en qué forma queda publicado de antemano, el
            envío se revisa antes de salir, y el comprobante dice contra qué versión de la regla se
            revisó. Para el municipio, eso significa preparar cada informe una vez y saber antes de
            enviarlo si está bien.
          </p>
        </div>
      </section>

      <section className="gris">
        <div className="wrap">
          <p className="eyebrow">Qué encontrará aquí</p>
          <h2>Tres piezas, una para cada necesidad</h2>
          <div className="cols-3">
            <div className="card">
              <div className="num">APIs</div>
              <h3>Para construir</h3>
              <p>
                Cada intercambio publicado como contrato, con su versión y su estado. Es la referencia
                para quien desarrolla o mantiene un sistema municipal.
              </p>
              <p>
                <Link to="/apis">Ver las APIs →</Link>
              </p>
            </div>
            <div className="card">
              <div className="num">Servicios</div>
              <h3>Para usar</h3>
              <p>
                Aplicaciones que ponen esas mismas APIs al alcance de cualquier funcionario: buscar el
                código de una comuna, consultar un permiso de circulación.
              </p>
              <p>
                <Link to="/servicios">Ver los servicios →</Link>
              </p>
            </div>
            <div className="card">
              <div className="num">Wiki</div>
              <h3>Para entender</h3>
              <p>
                Cómo se usa cada intercambio, cómo se generan los códigos y en base a qué norma está
                definido.
              </p>
              <p>
                <Link to="/wiki">Ir a la wiki →</Link>
              </p>
            </div>
          </div>
        </div>
      </section>

      <section>
        <div className="wrap">
          <p className="eyebrow">Cómo se trabaja</p>
          <h2>Lo que el municipio puede esperar</h2>
          <div className="cols-2">
            <div className="card">
              <h3>Funciona con el sistema que el municipio ya tiene</h3>
              <p>
                Da lo mismo si el municipio armó el suyo o lo compró. Lo que se pide es que el sistema
                cumpla lo que está publicado.
              </p>
            </div>
            <div className="card">
              <h3>La misma información que ya entrega</h3>
              <p>Lo que cambia es cuántas veces la prepara y saber de antemano si está bien.</p>
            </div>
            <div className="card">
              <h3>Abierto a cualquier proveedor</h3>
              <p>
                Lo publicado es público. Cualquier proveedor puede construir contra el estándar con
                datos de práctica, sin pedirle permiso a nadie y sin aceptar términos y condiciones.
              </p>
              <p className="alt">
                (Pendiente de decidir: si la zona de práctica queda totalmente abierta o pide algún
                registro. Aunque use datos inventados, hará falta seguridad y control de uso para que el
                volumen de llamadas no sature los servidores.)
              </p>
            </div>
            <div className="card">
              <h3>SUBDERE interopera con el resto del Estado</h3>
              <p>
                SUBDERE facilita a las municipalidades la entrega y la recopilación de información,
                encargándose de la interoperabilidad con el resto del Estado a través de sus nodos de la
                Red de Interoperabilidad y de los convenios que ya tiene vigentes.
              </p>
              <p className="alt">
                (Redacción pendiente de zanjar con la jefatura: cuánto se compromete del lado de SUBDERE
                hacia el resto del Estado. Lo que las municipalidades envían a otros organismos del
                Estado todavía no está levantado.)
              </p>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
