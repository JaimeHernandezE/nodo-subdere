# 2026-09 — El estándar de cada nodo se publica como especificación legible por máquina

**Estado:** Propuesta
**Fecha:** 15 de septiembre de 2026
**Origen:** Discusión sobre cómo mostrar las operaciones de un nodo en el catálogo, a propósito del primer nodo con implementación existente
**Relacionada con:** `adr-2026-08-portabilidad-y-conformidad.md` §1.3, §3.1, §3.6 · `nodo-lp-precedente.md` §3.4 · `maqueta.md`

---

## 1. Contexto

### 1.1 El catálogo empezó transcribiendo

La ficha del nodo de división político-administrativa lista once operaciones. Están escritas a mano en el archivo de datos del catálogo, copiadas desde el código del servicio.

Con un nodo eso funciona. El problema aparece al segundo: **nadie le avisa al catálogo cuando el servicio cambia.** El proveedor agrega un campo, corrige una ruta, cambia un código de error — y la ficha sigue describiendo la versión anterior. No por descuido: porque la ficha es una copia, y las copias divergen.

El resultado es la peor combinación posible. Un catálogo que describe mal un servicio es más dañino que uno que no lo describe, porque quien construye contra él descubre el error después de haber construido.

### 1.2 Pero el problema de fondo no es el catálogo, es la conformidad

El ADR de portabilidad decide que un sistema es conforme cuando su exportación, cargada en la implementación de referencia, reproduce los mismos productos regulatorios (§3.1), y advierte que **validar el esquema no basta** (§1.3): una exportación puede pasar una validación formal y ser inservible.

Todo eso supone algo que hasta ahora no estaba dicho: **que existe un criterio contra el cual una máquina pueda verificar.** Si el estándar de un nodo vive en un documento de Word, en una minuta o en campos que alguien llenó en un formulario, entonces verificar la conformidad es un acto humano. Alguien lee, alguien interpreta, alguien opina. Y un régimen de conformidad que depende de opiniones es exactamente lo que §3.6 de ese ADR intenta evitar cuando exige que la prueba sea **no discrecional**.

**Un estándar que no es legible por máquina no se puede verificar automáticamente. Y si no se puede verificar automáticamente, la conformidad se vuelve un trámite.**

### 1.3 Los dos precedentes empujan en la misma dirección

El Nodo Laboral y Previsional formaliza **en el anexo técnico y ex ante** qué atributos de cada conjunto de datos puede consumir cada institución, bajo un principio de necesidad y minimización. Ese anexo no puede ser prosa: es la parametrización que la plataforma aplica.

La CMF, en el Sistema de Finanzas Abiertas, provee un ambiente de pruebas centralizado donde el participante verifica su implementación **antes** de inscribirse. Un ambiente de pruebas solo puede existir si hay un contrato ejecutable contra el cual probar.

Ninguno de los dos habría podido construir lo que construyó con un estándar narrativo.

### 1.4 Y el primer nodo ya cumple el requisito, sin que se lo pidiéramos

El servicio de división político-administrativa del equipo SEM publica su contrato como OpenAPI 3.0.3: rutas, parámetros, esquemas de respuesta y treinta y un valores de ejemplo, uno por campo. Nadie lo exigió; es la práctica normal de quien construye una API.

Eso importa para la teoría de adopción de este ADR: **no se está pidiendo un esfuerzo nuevo, se está pidiendo que no se descarte lo que ya se hace.** La transcripción a mano es trabajo *adicional* que además degrada el resultado.

---

## 2. Alternativas consideradas

| Opción | Por qué se descarta o se adopta |
|---|---|
| **A. Campos en el modelo del catálogo** — una tabla de operaciones que alguien llena | Es lo que hay hoy en la maqueta. Funciona para mostrar, y falla en todo lo demás: diverge del servicio, no permite diferenciar versiones, no sirve para generar pruebas, y convierte cada cambio del proveedor en trabajo manual de SUBDERE. Descartada como mecanismo permanente |
| **B. Documento adjunto** — el nodo sube un PDF o un Word con su especificación | Resuelve la autoría —el documento es del proveedor— y no resuelve nada más. No es procesable, no es comparable entre versiones y reproduce el modo de falla de §1.2: la conformidad pasa a depender de que alguien lea. Descartada |
| **C. Especificación legible por máquina registrada por el nodo, renderizada por el catálogo** | **Adoptada.** El contrato es un archivo con formato conocido; la ficha es una proyección de ese archivo |
| **D. El catálogo genera la especificación a partir de sus campos** | Invierte la responsabilidad: haría a SUBDERE autora del contrato de un servicio que no opera. Además reproduce A con más pasos. Descartada |

---

## 3. Decisión

> **El estándar de un nodo se publica como especificación legible por máquina.**
>
> El catálogo la **almacena versionada y la renderiza**; no la transcribe. La ficha del nodo es una proyección de ese archivo, nunca una segunda fuente de verdad.

### 3.1 Qué cuenta como especificación legible por máquina

No se fija un formato único, porque los nodos no son todos del mismo tipo. Se fija el requisito y se declara el formato:

| Tipo de nodo | Formato | Ejemplo |
|---|---|---|
| Intercambio por HTTP | **OpenAPI 3.x** | División político-administrativa |
| Contenido de un documento o reporte | **JSON Schema** | El reporte que un municipio entrega |
| Eventos y notificaciones | **AsyncAPI** | Un mecanismo de publicación y suscripción |

El registro declara cuál formato usa. Lo que **no** se acepta es un contrato cuyo formato no tenga un validador público disponible: ese es el corte, y es el que hace ejecutable todo lo que sigue.

### 3.2 La especificación se versiona aparte de la ficha

Son dos historias distintas y conviene que lo sean desde el primer día. La descripción de un nodo puede mejorar sin que cambie su contrato, y el contrato puede cambiar sin que la descripción se mueva. Confundirlas obliga a elegir entre no poder corregir una redacción y falsificar un cambio de versión.

Cada versión registrada queda disponible. Una versión anterior **no se borra ni se corrige**: se registra una nueva.

### 3.3 El catálogo no edita la especificación

SUBDERE no es autora del contrato de un servicio que no opera. Puede rechazar un registro que no cumpla los requisitos mínimos de §3.5, y no puede modificarlo. Corregir el archivo de un tercero sería asumir responsabilidad sobre su comportamiento.

### 3.4 Qué habilita esto, que con campos transcritos no se puede hacer

Es la razón entera de la decisión, así que conviene enumerarla:

1. **Renderizar la ficha** sin que nadie transcriba nada.
2. **Diferenciar dos versiones** y decir con precisión qué cambió entre ellas.
3. **Detectar cambios incompatibles** —un campo obligatorio nuevo, un tipo que cambia, una ruta que desaparece— y avisar antes de que rompan a alguien.
4. **Validar un ejemplo** contra el contrato, que es la verificación mínima de §1.3 del ADR de portabilidad: el detector del cascarón.
5. **Generar el esqueleto de la suite de conformidad** en vez de escribirla a mano para cada nodo.
6. **Levantar un ambiente de pruebas** contra el cual un tercero construya sin convenio, que es el plano abierto de §3.6 de ese mismo ADR.

Los puntos 4, 5 y 6 son requisitos ya comprometidos en el ADR de portabilidad. **Esta decisión es lo que los vuelve realizables**, y esa es su justificación principal: no es una mejora del catálogo, es el habilitante de la conformidad.

### 3.5 Requisitos mínimos de una especificación registrada

Tres, y ninguno es exigente:

- **Valida contra el esquema de su propio formato.** Un OpenAPI que no es un OpenAPI válido no se registra.
- **Trae ejemplos.** Al menos uno por respuesta. Sin ejemplo, el contrato describe la forma y no el contenido, y quien construye igual tiene que preguntar.
- **Declara su versión.** Si el formato no la contempla, se declara en el registro.

### 3.6 Si un nodo no tiene especificación, la ficha lo dice

**No se rellena a mano.** Esta es la parte de la decisión que más fácil se erosiona: aparecerá el caso de un nodo importante sin especificación y la tentación de escribir sus operaciones «mientras tanto». Ese atajo convierte al catálogo en la segunda fuente de verdad que §3 prohíbe, y lo hace justo donde más daño causa.

Un nodo sin especificación muestra un pendiente, y ese pendiente es información: dice que el nodo todavía no tiene contrato publicado, que es un hecho verdadero sobre su estado de madurez.

---

## 4. Consecuencias

1. **El modelo del catálogo cambia antes de escribirse.** `operaciones` deja de ser una tabla de filas y pasa a ser un documento versionado con su metadato de formato. Es una corrección barata hoy y cara después de la primera migración.

2. **El catálogo adquiere una dependencia nueva: un renderizador y un validador por formato.** Es código a mantener, y es la contrapartida honesta de todo lo que §3.4 habilita. No es gratis.

3. **El registro de un nodo pasa a tener un paso de validación.** Alguien —o algo— debe verificar que la especificación cumple §3.5 antes de aceptarla. Automatizable, pero hay que construirlo.

4. **Se refuerza el plano abierto.** Que el contrato sea público y procesable es lo que permite construir contra un nodo sin convenio y sin datos reales. Sin esto, «el estándar es público» significa solamente que alguien puede leerlo.

5. **La ficha deja de funcionar abriendo el archivo con doble clic.** Leer un archivo externo desde una página local está bloqueado por el navegador. Es una molestia de la maqueta, no del producto, y se resuelve sirviendo el sitio.

6. **Aparece una exigencia hacia los proveedores que conviene enunciar temprano.** Registrar un nodo requerirá entregar una especificación válida. Quien ya construye APIs la tiene; quien no, tendrá que producirla. Debe estar en las bases desde la primera versión y no aparecer como sorpresa.

7. **El primer nodo sirve de prueba de la decisión.** La ficha de división político-administrativa se renderiza desde el `openapi.yaml` del equipo SEM, sin transcripción. Si ese camino no funciona ahí, no va a funcionar en ningún otro.

---

## 5. Pendientes derivados

| ID | Pendiente | Dueño | Por qué importa |
|---|---|---|---|
| **X-108** | **Formatos aceptados y su validador de referencia**, por tipo de nodo | Arquitectura | §3.1. Sin la lista cerrada, el requisito de «legible por máquina» no es verificable |
| **X-109** | **Política de versionado de la especificación**: qué cambio obliga a subir versión mayor, cómo se declara un cambio incompatible y con cuánta anticipación | Arquitectura / bases | §3.2 y §3.4.3. Es la pieza que el ADR de portabilidad da por supuesta en su régimen de caducidad por causal |
| **X-110** | **Procedimiento de registro**: quién sube la especificación, contra qué se valida, quién acepta y cómo se rechaza sin discrecionalidad | Arquitectura / jurídica | §3.3 y §3.5. Es donde esta decisión se vuelve operación |
| **X-111** | **Alcance del renderizador del catálogo**: qué se muestra de la especificación y qué queda solo en el archivo | Arquitectura | Consecuencia 2. Define cuánto código hay que mantener |

---

## 6. Qué queda explícitamente fuera

- **No se decide el modelo de datos de ningún nodo.** Se decide en qué forma se publica el que cada uno tenga.
- **No se exige OpenAPI a todos los nodos.** Se exige una especificación en un formato con validador público; OpenAPI es el que corresponde a los nodos sobre HTTP.
- **No se decide si el catálogo aloja la especificación o solo la referencia.** Ambas cumplen la decisión; el registro concreto es parte de X-110.
- **No se crea obligación para servicios existentes.** Rige para el registro de nodos en el catálogo, no hacia atrás.

---

## Registro de cambios

| Versión | Fecha | Cambio |
|---|---|---|
| v1 | 15 de septiembre de 2026 | Creación. El estándar de un nodo se publica como especificación legible por máquina; el catálogo la almacena versionada y la renderiza sin transcribirla. Se descartan la tabla de campos y el documento adjunto. Se enuncia como habilitante de la verificación automática de conformidad comprometida en el ADR de portabilidad |
