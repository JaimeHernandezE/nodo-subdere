# Pauta — reunión con el jefe de la Secretaría de Gobierno Digital

**14 de octubre de 2026** · Jaime Hernández, División de Políticas y Estudios, SUBDERE
Para llenar durante la reunión. Cada respuesta cierra un pendiente identificado; están mapeados al final.

---

## Antes de entrar

**El encuadre.** Las fichas EGD 2030 del Nodo SUBDERE y del JPL Virtual ya están en SGD, y el 22 de octubre el Ministro presenta la Estrategia en el seminario «Estado Digital». La conversación es **cómo se cumple lo comprometido**, no pedir permiso.

**Lo que conviene decir primero**, porque cambia la posición en la mesa: SUBDERE tiene **un** servicio publicado en el Catálogo —el de información de permisos de circulación por patente— y la intención es publicar más, partiendo por los flujos donde SUBDERE tiene mandato para recibir, procesar y entregar. Es una brecha de ejecución y reconocerla primero deja la conversación en cómo avanzar.

**Lo que no se pregunta.** No preguntar si se puede intercambiar por fuera de la Red. La pregunta 1, bien respondida, hace innecesaria esa discusión, y una pregunta así hecha a este nivel obliga a una respuesta formal que después pesa. Si él menciona por su cuenta que hay flexibilidad o alternativas: escuchar, y **pedir que quede por escrito**.

---

## 1. El nodo de un municipio alojado por un tercero

> «El artículo 6 describe el nodo como un componente alojado en la infraestructura informática de un órgano. ¿Cuenta como infraestructura del municipio la que le provee o le contrata un tercero —su proveedor de software, u otro órgano— cuando el certificado se emite a nombre del municipio y la responsabilidad sigue siendo suya?
>
> Y la segunda mitad: ¿se necesita un nodo por municipio, o una misma instalación puede alojar los nodos de varios, cada uno con su propio certificado?»

**Cómo plantearla.** Genérica: «un sistema de gestión municipal operado por un tercero». No «para el SGM». La respuesta sirve igual para nosotros y para cualquier proveedor privado, y así no se lee como que SUBDERE pide trato especial.

**El argumento, que es operacional y no interpretativo.** Si el nodo tiene que estar instalado dentro del municipio, un sistema que corre en infraestructura central tendría que alcanzar un nodo dentro de la red de cada municipio: un túnel por municipio, hacia 345 redes, mantenido por alguien. En la práctica, o el nodo está junto al sistema que lo usa, o ese sistema no puede interoperar.

**Qué cambia.** Un sí desbloquea la arquitectura completa y saca la pregunta de la ruta crítica del SGM. Un no obliga a un plan B — y conviene que el no venga con su consecuencia dicha en voz alta: el piloto no podría hacerse con un municipio del SGM.

**Dato de apoyo, con cuidado.** La Guía Técnica vigente parece admitir un nodo propio, uno desarrollado por terceros o uno provisto por un proveedor externo. Esa lectura es nuestra y con herramienta de extracción, no cotejada: mencionarla como pregunta («¿lo estamos leyendo bien?»), no como cita.

**Respuesta:**



---

## 2. Uso efectivo, por municipio

> «¿Cuántos municipios usan hoy efectivamente la Red, más allá de tener acceso? ¿SGD tiene ese dato por municipio? ¿Y lo equivalente de DocDigital?»

**Por qué.** Es el único lugar donde existe ese número y es la línea base de todo el diagnóstico municipal. Hoy lo que tenemos es que los 345 tienen acceso y casi no la usan, como información del equipo, no como medición.

**Qué cambia.** Con el dato por municipio, la incorporación se puede planificar por grupos y medir. Si la respuesta es que no se mide así, eso también es un hallazgo: es lo que justifica adoptar la métrica de **consumo habilitado contra consumo efectivo** que usa el Nodo Laboral y Previsional.

**Respuesta:**



---

## 3. Entrega con acuse: quién publica el servicio

> «La Red funciona con consulta y respuesta. Para una entrega periódica con acuse —la nómina mensual de un bono, por ejemplo—, ¿es correcto que SUBDERE publique un servicio de recepción y el municipio lo consuma enviando la nómina en la consulta? ¿O SGD prefiere que el municipio sea el proveedor?»

**Por qué.** Decide el diseño de todos los flujos donde SUBDERE es ventanilla. Si el municipio tiene que **proveer**, son 345 municipios publicando servicios, que es lo más difícil de montar. Si solo **consume** un servicio nuestro, es una integración.

**Qué cambia.** Define el primer servicio de entrada que vamos a publicar, y con eso el segundo servicio de SUBDERE en el Catálogo.

**Respuesta:**



---

## Si hay tiempo

### 4. La ficha municipal consolidada

> «¿Ve SGD una ficha municipal consolidada, publicada por SUBDERE en la Red como proveedora, como un caso comparable al Nodo Laboral y Previsional? ¿Y qué base normativa cree que eso requiere? SICEX tiene su propio decreto.»

Es la validación institucional del concepto completo del nodo. La segunda parte importa igual o más: es jurídica antes que técnica.

**Respuesta:**



### 5. Los esquemas del dominio municipal

> «¿Pueden los esquemas del dominio municipal, escritos en OpenAPI o JSON Schema, proponerse al Catálogo de Esquemas? ¿Es ese el camino para incorporarlos al compendio de estándares?»

Barata de responder y habilita la pata de los estándares, que es la que podemos avanzar solos. Pregunta pegada: cómo se relaciona el Gestor de Códigos del Estado con el servicio de códigos únicos territoriales.

**Respuesta:**



### 6. Gestor de Solicitudes y los convenios

> «¿En qué estado está el Gestor de Solicitudes? Y los términos y condiciones que introdujo el Decreto 876, ¿reemplazan los convenios de interoperabilidad que SUBDERE ya tiene firmados?»

El artículo quinto transitorio del Decreto 876 deja sin efecto los convenios incompatibles con la norma. Si aplica, hay cosas que no hay que redactar porque ya están resueltas.

**Respuesta:**



---

## Qué llevarse de la reunión

No buena voluntad: dos cosas concretas.

1. **El dato de uso efectivo por municipio**, o el compromiso de buscarlo con fecha.
2. **Una respuesta escrita a la pregunta 1**, aunque sea un correo.

Si no quieren pronunciarse en abstracto, la salida barata es **pedir que se formalice como piloto, con alcance y plazo**. El piloto natural es permisos de circulación: SUBDERE publica el servicio y SUBDERE aloja el sistema que lo consume, así que si el camino por la Red no funciona cuando los dos extremos son de la casa, no va a funcionar con nadie.

Y una tercera, si la conversación lo permite: **ofrecer que SGD revise el conector de referencia** cuando exista. Posiciona a SUBDERE como quien aporta al ecosistema y no solo como quien pide.

---

## Qué pendiente cierra cada respuesta

| Pregunta | Pendiente |
|---|---|
| 1 | **HR-26** — nodo alojado por un tercero, y varios en una instalación |
| 2 | **HR-03** — indicadores del nodo: consumo habilitado contra efectivo |
| 3 | Diseño de los flujos de tipo B · hitos de la Etapa 1 |
| 4 | **HR-15** y la pregunta jurídica del mandato de ventanilla |
| 5 | **X-108** y el camino del estándar al Catálogo de Esquemas |
| 6 | **HR-07** — términos y condiciones, y la credencial del municipio |

**Después de la reunión:** las respuestas van a la Parte III de `docs/hoja-de-ruta.md`, y lo que quede por escrito se guarda en `insumos/` — que no se versiona — o se cita en el documento que corresponda.
