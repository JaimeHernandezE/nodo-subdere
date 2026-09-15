# Plataforma Institucional de Gestión de APIs — Plataforma de Control

**Estado:** Propuesta  
**Fecha:** 15 de septiembre de 2026  
**Nombre formal:** Plataforma Institucional de Gestión de APIs  
**Nombre corto:** Plataforma de Control  
**Diagramas de referencia:** [`flujo_1.md`](flujo_1.md) (demo) · [`flujo_2.md`](flujo_2.md) (producción)  
**Relacionada con:** [`adr-2026-09-estandar-legible-por-maquina.md`](adr-2026-09-estandar-legible-por-maquina.md) · [`nodo-lp-precedente.md`](nodo-lp-precedente.md) · corpus SGM `nodo-integracion-subdere.md` §8–§14 · pendientes **X-02**, **X-48**, **X-82…X-89**

---

## 1. Qué es y qué no es

La Plataforma de Control es la capa compartida de **publicación y gobierno de acceso** del Nodo SUBDERE: gateway, identidad de llamada y logs. Es el único camino por el que un consumidor alcanza una API publicada en el catálogo.

| Pieza | Qué es | ¿Nodo del catálogo? | ¿Consumo por módulo? |
|---|---|---|---|
| **Plataforma de Control** | Cómo se llega (gateway, token, cuota, log) | No. Es el frente del catálogo | No aplica |
| **Core SGM** (C1–C11) | Identidad de funcionario, tenants, RBAC, parámetros, auditoría de negocio, documentos, adaptadores (Mercado Público, FirmaGob, DocDigital) | Sí, clase `plataforma` | **No.** Condición de cualquier módulo SGM |
| **Módulo de negocio** (p. ej. Adquisiciones) | Dominio funcional con OpenAPI propio | Sí, clase `intercambio` | Sí, con el core detrás |

**Regla.** Usar cualquier API del Nodo SUBDERE pasa por acá. Las APIs internas no se exponen a Internet.

**Paridad.** El frontend de SGM es un consumidor más, sin canal interno ni privilegios (principio no negociable n.° 1 del corpus SGM). Si el front habla con Adquisiciones por un camino distinto al de un municipio en consumo por módulo, la paridad se rompe.

Esta capa **no** define el negocio de ningún nodo. El contrato de cada nodo sigue siendo su especificación legible por máquina (OpenAPI, JSON Schema o AsyncAPI), según el ADR de septiembre de 2026. Sin control y sin logs, publicar una API no constituye nodo.

---

## 2. El producto son el control y los logs

| Capacidad | Qué garantiza |
|---|---|
| Punto único de entrada | El consumidor ve rutas del gateway; las APIs internas no tienen nombre público |
| Validación de token | Cada llamada porta un JWT emitido por el IdP (OAuth 2.0 / OIDC) |
| Permisos y límites | Scopes y cuotas se aplican en el gateway antes de llegar al servicio |
| Logs centralizados | Observabilidad operacional: quién llamó, a qué ruta, con qué resultado |
| Auditoría de llamada | Exigencia distinta de los logs: traza inmutable de acceso (quién, a qué, bajo qué autorización). Complementa, no reemplaza, la auditoría de negocio del core (C5) |

**Distinción.** La Plataforma de Control registra la **llamada**. El core de SGM registra el **acto** de negocio. No se duplica la función.

---

## 3. Arquitectura

Los diagramas canónicos viven en [`flujo_2.md`](flujo_2.md) (zonas de red: perímetro, DMZ, red interna, monitoreo) y [`flujo_1.md`](flujo_1.md) (demo en un solo servidor).

Secuencia:

1. El cliente solicita un token al IdP.
2. El IdP entrega un access token JWT.
3. El cliente invoca el gateway con el JWT.
4. El gateway valida token, permisos y límites.
5. El gateway reenvía a la API interna correspondiente.
6. La respuesta vuelve por el mismo camino.

Las rutas de ejemplo `/patentes`, `/gastos` y `/contabilidad` en los diagramas son **marcadores**. En este catálogo equivalen a las fichas publicadas; las primeras de SGM son `/plataforma` (core) y `/adquisiciones`.

Componentes de la arquitectura de referencia (API7, Keycloak, LogTank): ver §5. No van a las bases como marcas.

---

## 4. Dos planos de autenticación

Ambos atraviesan la Plataforma de Control. La plataforma **no sustituye** Clave Única.

| Plano | Mecanismo | Quién | Uso |
|---|---|---|---|
| **Personas** | Clave Única (vía C1 del core: SGM no es IdP de personas) | Funcionario en el frontend SGM | Operación humana |
| **Sistemas** | OAuth 2.0 client credentials (o equivalente) | Sistema municipal en consumo por módulo, integrador en convenio | Máquina a máquina (**X-02**) |

Clave Única autentica a la persona. La Plataforma de Control autentica **la llamada** (token, scope, municipio, cuota, log). El plano M2M se resuelve aquí, no dentro de cada módulo.

---

## 5. Propiedades para licitar, no marcas

La licitación de esta capa es **aparte** de la de SGM (Opción B del documento de nodo de integración SUBDERE). SGM es el primer consumidor, no el dueño.

API7 y Keycloak son **arquitectura de referencia, no vinculante**. SUBDERE especifica propiedades; el oferente propone producto. Mención de marca en bases tensiona la Ley 19.886.

| Propiedad | Criterio de recepción (cumple / no cumple) |
|---|---|
| OAuth 2.0 / OIDC estándar | Emisión y validación de JWT interoperable |
| Punto único de entrada | Toda API del catálogo solo alcanzable por el gateway |
| Aislamiento por municipio | Credencial del municipio A no lee datos del B |
| Cuotas y límites | Exceso → rechazo demostrable |
| Revocación | Credencial revocada denegada dentro del plazo comprometido |
| Logs sin secretos | Cero tokens ni cabeceras `Authorization` en log |
| Configuración exportable | Exportar gateway e IdP, reimportar en instancia limpia, equivalencia funcional |
| Portabilidad | Sin lenguaje propietario obligatorio para reglas de enrutamiento |

Construir y operar son capacidades distintas (**X-84** abierto): conviene licitarlas como ítems separables, con traspaso operativo demostrable.

---

## 6. Casos de uso

Cada caso: actor, qué pide, qué garantiza la Plataforma de Control, qué sigue siendo del nodo, qué queda pendiente.

### UC-0 — Plano abierto (división territorial)

| | |
|---|---|
| **Actor** | Cualquier sistema que necesite códigos de región, provincia o comuna |
| **Qué pide** | Consulta de solo lectura, dato público |
| **Qué garantiza el Control** | URL pública, cuota, log; auth opcional |
| **Qué sigue siendo del nodo** | El OpenAPI y el servicio (hoy solo en red SEM) |
| **Pendiente** | Exponer el servicio fuera de SEM; ambiente de pruebas abierto |

### UC-1 — Frontend SGM → Control → core y Adquisiciones

| | |
|---|---|
| **Actor** | Frontend base de SGM (funcionario con Clave Única) |
| **Qué pide** | Operar compras y capacidades de plataforma (identidad, roles, documentos) |
| **Qué garantiza el Control** | Toda llamada pasa por el gateway; mismos contratos que vería un tercero; traza y cuotas |
| **Qué sigue siendo del nodo** | Contratos del core y de Adquisiciones; reglas de negocio |
| **Pendiente** | Servicio en ejecución; plano persona cableado (C1); **X-02** formalizado |

Es el caso que demuestra paridad **sin** esperar un municipio en consumo por módulo ni el resto del ERP. Si el front no puede operar Adquisiciones salvo pasando por el gateway, la plataforma hace su trabajo.

### UC-1b — Cliente M2M → Control → core (obligatorio) + Adquisiciones (elegido)

| | |
|---|---|
| **Actor** | Sistema municipal propio (consumo por módulo) o integrador autorizado |
| **Qué pide** | Consumir el OpenAPI de Adquisiciones (y el del core) |
| **Qué garantiza el Control** | Client credentials, scopes por módulo y municipio, aislamiento, revocación |
| **Qué sigue siendo del nodo** | Adquisiciones declara contratos de proveedor (Presupuestos, Contabilidad); el core no se sustituye |
| **Pendiente** | Título jurídico de acceso de privados (**X-87**); taxonomía de scopes (**X-89**) |

### UC-2 — Catálogo JPL y afines

Una fila por nodo del mapeo (pagos/tesorería, índice de expedientes, notificador, DOM, estándares de Gobierno Digital como restricción sobre la capa, Correos, inspección, direcciones que remiten, entre juzgados).

| | |
|---|---|
| **Actor** | Según el nodo: municipio, tribunal, Correos, etc. |
| **Qué pide** | Consulta, entrega o intercambio bidireccional |
| **Qué garantiza el Control** | Autenticación de la llamada, cuota, constancia |
| **Qué sigue siendo del nodo** | El sentido del intercambio y el contrato de negocio |
| **Pendiente** | Spec de cada nodo; factibilidad del mapeo |

### UC-3 — Etapa posterior: más módulos SGM

Presupuestos, Contabilidad, Tesorería y RRHH entran al catálogo cuando tengan especificación comparable a Adquisiciones. El municipio habilita uno o varios **sobre** el core. La Plataforma de Control no orquesta el negocio; solo publica, autoriza y deja constancia.

---

## 7. Fuera de alcance

- Tráfico OAE ↔ OAE que corresponde a la red de interoperabilidad / PISEE (NTI, D.S. N° 12/2023).
- Motor de integración / ESB hacia sistemas sin API (**X-83** decide si hace falta).
- Título jurídico de acceso de privados, acreditación y tarifa (**X-87**, **X-88**).
- Publicar la propia Plataforma de Control como ficha del catálogo (sería el frente listándose a sí mismo).

Clave Única **no** está fuera de alcance: es el plano persona que la plataforma transporta; no es un producto que la plataforma reemplace.

---

## 8. Relación con el precedente

Del Nodo Laboral y Previsional se copia la idea de **plataforma compartida** y de anexo técnico ejecutable (scopes, minimización). No se copia PISEE como transporte: esta licitación **sí** construye el frente de acceso, porque el consumidor privado o municipal en consumo por módulo no entra a la red de interoperabilidad por diseño normativo.

Detalle del precedente: [`nodo-lp-precedente.md`](nodo-lp-precedente.md). Delimitación frente a la red de interoperabilidad: corpus SGM, `nodo-integracion-subdere.md` §2.

---

## Registro de cambios

| Versión | Fecha | Cambio |
|---|---|---|
| v1 | 15 de septiembre de 2026 | Creación. Nombre formal y corto; deslinde frente a core y módulos; producto = control y logs; dos planos; propiedades licitables; UC-0 a UC-3 |
