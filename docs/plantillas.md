# Plantillas de API y de servicio

**29 de septiembre de 2026.** Toda API publicada usa la misma plantilla de ficha, y todo servicio usa la misma plantilla de página. Este documento describe las dos: qué secciones tienen, en qué orden, qué campo alimenta cada una y qué pasa cuando falta. Es la especificación del **mantenedor** con que SUBDERE va a agregar y editar ítems del catálogo sin tocar código.

En la maqueta, el modelo es [`prototipos/assets/data.js`](../prototipos/assets/data.js): `NODOS` para las APIs y `SERVICIOS` para los servicios. Cada campo de allí es un campo del formulario del mantenedor y del modelo en Django. La tabla completa de campos de `NODOS` está en [`maqueta.md`](maqueta.md#el-modelo-del-catálogo); aquí se describe cómo se usan en la página.

## Qué edita el mantenedor y qué no

| Lo edita el mantenedor | No lo edita el mantenedor |
|---|---|
| Textos: nombre, función, descripción, nota, acceso, pruebas | **El contrato.** Es un archivo OpenAPI que se registra tal cual; la ficha lo lee y no lo transcribe. Ver [ADR del estándar legible por máquina](adr-2026-09-estandar-legible-por-maquina.md) |
| Clasificación: ámbito, clase, madurez, factibilidad, estado | **La herramienta de un servicio.** El buscador o formulario de cada servicio es código y se despliega como tal |
| Relaciones: instituciones, dependencias, API de un servicio | **La disponibilidad.** La publica un monitor externo en `estado/status.json`; nunca se escribe a mano |
| Procedencia del contrato, fuentes de datos, enlaces a la wiki | **Los datos del ambiente de pruebas.** Son un script por nodo (`sandbox.script`), porque incluyen la lógica que responde |
| Descargables y fecha de actualización | |

### Reglas de redacción

- **Sin marcas de maqueta.** Las páginas se escriben como la versión definitiva. Lo que es propuesta o ejemplo lo dicen los campos que existen para eso (`procedencia.copia`, `nota`, descargables sin `url`), no el texto corrido.
- **Frases que el usuario reconozca.** La función y las tareas describen lo que la persona hace («Escribir una patente y ver…»), no cómo está construido.
- **Una sola advertencia, y solo si cambia lo que el lector haría.** Va en `nota`. Lo que depende de la conexión (datos de prueba o en vivo) lo dice la propia pantalla.
- **Términos del glosario.** En los textos largos, `[[id]]` o `[[id|texto]]` enlaza a la definición en la wiki. Solo la primera mención. El diccionario es `TERMINOS`.
- **No inventar.** Endpoints, campos, normas, fuentes o umbrales que no estén respaldados no se escriben; se deja el campo vacío y la plantilla muestra su bloque «Pendiente».

## Plantilla de API

Página: `nodo.html?id=<id>`. Una sola plantilla sirve a todos los nodos.

### Columna principal, en orden

| Sección | Campos | Si falta |
|---|---|---|
| Cabecera | `clase` (etiqueta «Base» si es `plataforma`), `ambito`, `nombre`, `funcion` | Obligatorios |
| Aviso superior | Se deduce de `espec`, `espec.archivo`, `espec.expuesto` y `sandbox`: si hay contrato, si hay servicio detrás, si se puede probar | Siempre hay uno |
| Para qué sirve | `descripcion`, y debajo `nota` si existe | `descripcion` es obligatoria; `nota` es opcional |
| Aplicaciones que la usan | Los `SERVICIOS` cuyo `nodo` es este. Enlace a cada uno | La sección no aparece |
| Qué entrega, y en qué forma | `espec.formato`, `espec.validador`, `espec.archivo`, `espec.registrada`, `espec.acceso` y el bloque **Procedencia** (`espec.procedencia`: responsable, fuente oficial, qué es lo que se ve acá, observaciones en la wiki) | Sin `espec`: bloque «Todavía no está escrito» |
| Depende de | `dependencias` (`{ nombre, id? }`; con `id` enlaza a la otra ficha) | «No declara dependencias» |
| Qué se le puede pedir | Se lee de `espec.archivo` y se renderiza. Nada se transcribe | Sin archivo: bloque «Pendiente» |
| Probar la API | `pruebas` y, si hay `sandbox`, la consola y los casos de prueba | Sin `pruebas`: bloque «Todavía no existe» |

### Panel lateral

| Bloque | Campos |
|---|---|
| Ficha | Tipo (`clase`), estado (`madurez`), viabilidad (`factibilidad`), dirección (`intercambio`), quiénes participan (`instituciones`), de dónde salió (`origen`), última actualización (`actualizado`) |
| Descargables | `descargables`: con `url` se descarga; con `generar: "sandbox"` se arma con los datos de prueba; sin ninguno se lista como ejemplo |

### En el catálogo de APIs

La tarjeta de `apis.html` usa `nombre`, `funcion`, `ambito`, `clase`, `madurez`, las dos primeras `instituciones`, el contrato (`espec`), `acceso_tipo`, `sandbox` («Se puede probar»), `actualizado` y la disponibilidad del monitor.

## Plantilla de servicio

Página: un archivo por servicio (`url`), porque cada uno trae su herramienta. Lo demás lo arma [`assets/servicio.js`](../prototipos/assets/servicio.js) desde `SERVICIOS`:

```html
<main data-servicio="buscador-cut">
  <div id="herramienta"> … campo, ejemplos, resultados … </div>
</main>
<script src="assets/data.js"></script>
<script src="assets/terminos.js"></script>
<script src="assets/servicio.js"></script>
<script> … lógica de la herramienta … </script>
```

La herramienta debe dejar en `#estado-fuente` una frase sobre de dónde está respondiendo: datos de prueba, muestra o conexión en vivo.

### Columna principal, en orden

| Sección | Campos | Si falta |
|---|---|---|
| Cabecera | `nombre` (miga y título) | Obligatorio |
| Entrada | `descripcion`, y debajo `nota` si existe | `descripcion` es obligatoria; `nota` es opcional |
| Herramienta | El bloque `#herramienta` de la página: campo, ejemplos, resultados | Obligatoria |
| De dónde salen estos datos | `fuentes_intro` y `fuentes` (`[{ dato, origen }]`): qué institución genera cada dato. Debajo, el recuadro `#estado-fuente` | Sin `fuentes` queda solo el recuadro |

### Panel lateral

| Bloque | Campos | Si falta |
|---|---|---|
| Documentación | «La API que usa» → ficha de `nodo`, con su nombre. «Probar la API» → `#probar` de esa ficha, si el nodo tiene `sandbox`. «Entrada de wiki» → `wiki` (`{ texto, url }`) | Sin `wiki` se usa `procedencia.observaciones` del nodo; si tampoco hay, el enlace no aparece |
| Estado | `estado` (Disponible · En construcción · Deseable) y `actualizado` | `actualizado` es opcional |

### En el catálogo de servicios

La tarjeta de `catalogo.html` usa `nombre`, `estado`, `funcion` y `tareas`. El buscador también encuentra el servicio por el nombre de su API, aunque la tarjeta no lo muestre.

## Agregar un ítem

**Una API nueva.** Se crea el registro en `NODOS` con los campos obligatorios de la cabecera y «Para qué sirve». Lo demás puede quedar vacío: la ficha muestra el bloque «Pendiente» que corresponda y no hay que escribir nada más. Cuando llega el contrato, se registra el archivo y se completan `espec` y `espec.procedencia`.

**Un servicio nuevo.** Hace falta que su API ya entregue algo. Se crea el registro en `SERVICIOS` y la página con su herramienta, siguiendo el esqueleto de arriba. La página de la API lo lista sola en «Aplicaciones que la usan».
