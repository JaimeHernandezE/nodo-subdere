## El municipio entrega o pregunta, y siempre sabe qué pasó

Un intercambio es cualquier dato que pasa entre el municipio y otra institución. Pasa de dos maneras:

- **Entrega:** el municipio envía algo que le piden, como un informe de fin de mes.
- **Pregunta:** el municipio consulta algo que necesita, como el código de una comuna o el permiso de un vehículo.

Para cada intercambio publicamos de antemano qué se entrega y en qué forma. Eso es el [estándar](/wiki/glosario#estandar), y está escrito para que lo entienda tanto una persona como un programa.

## Cuatro pasos, y el envío lo decide el municipio

Da lo mismo quién hizo el sistema del municipio —el [SGM](/wiki/glosario#sgm), uno propio o uno comprado a un proveedor—: el camino es el mismo para todos.

::::: tarjetas
:::: tarjeta
**01**

### Publicamos el estándar de antemano

Decimos cómo debe venir cada informe y qué reglas le aplicamos, con un número de versión. Si una regla cambia, publicamos una versión nueva y queda claro cuál rige.
::::

:::: tarjeta
**02**

### Revisar es gratis y se puede repetir

El sistema del municipio revisa su informe las veces que quiera, y los errores aparecen en la misma pantalla donde trabaja el funcionario. En este paso no sale nada del municipio.
::::

:::: tarjeta
**03**

### Enviar lo decide el municipio

Solo cuando el informe está limpio, el funcionario responsable autoriza el envío. Entregar sigue siendo una decisión del municipio, no algo que ocurre solo.
::::

:::: tarjeta
**04**

### Y queda comprobante

Un [comprobante](/wiki/glosario#comprobante) dice qué se envió, cuándo, a quién y con qué versión de las reglas se revisó. Se consulta después en el mismo lugar para todos los intercambios.
::::
:::::

**Cuando el municipio pregunta**, no hay nada que autorizar: el sistema pregunta, el servicio responde y queda anotado quién preguntó qué.

## Cada entrega dice qué se revisó y qué no

Antes de que un informe salga del municipio, lo revisamos de dos formas:

| Con qué revisamos | Qué hacemos |
|---|---|
| **Con nuestras reglas** | Comparamos el informe con el estándar que publicamos para ese intercambio. |
| **Con las reglas de la norma** | Aplicamos lo que dice la norma que obliga la entrega, escrito como regla y mantenido al día. |

::: aviso
Pendiente de definir: qué hace el nodo con lo que las municipalidades envían a otros organismos del Estado. Todavía no está levantado qué se envía, a quién ni por qué canal.
:::

## Una sola puerta, y queda registro de quién entró

Detrás de cada API hay un [servicio](/wiki/glosario#servicio): el sistema que atiende ese intercambio. Revisa el informe, devuelve las observaciones, recibe el envío y emite el comprobante; o, si le preguntan, responde.

Todos los sistemas llegan a los servicios por la [misma puerta](/wiki/glosario#puerta-de-acceso), que comprueba quién pide y deja constancia.

1. **El sistema del municipio** — Entrega o pregunta
1. **Pide un permiso** — Con la credencial del municipio
1. **La puerta** — Comprueba quién es y qué puede pedir
1. **El servicio** — Responde o recibe
1. **Queda registro** — Quién pidió qué, y cuándo

- **Nadie tiene atajos.** La pantalla del propio SGM entra por esta misma puerta, igual que el sistema de cualquier municipio o proveedor.
- **Quitarle el acceso a alguien es inmediato.** El permiso de entrada dura poco y se pide cada vez, así que no depende de avisarle a nadie.
- **La puerta no decide sobre el contenido.** Una parte sabe quién es cada municipio o sistema y le entrega su permiso; la otra revisa ese permiso en cada pedido, limita cuánto se puede pedir y lo anota. Revisar el informe y emitir el comprobante lo hace cada servicio.

::: aviso
Todavía no está construida: es el diseño que proponemos. El detalle técnico está en la [nota de la plataforma de control](https://github.com/JaimeHernandezE/nodo-subdere/blob/main/docs/plataforma-control.md).
:::

## Y ahora, ¿qué hago?

- Para pedirle datos a una API: [cómo se usa una API](/wiki/consumir).
- Para conectar el sistema de tu municipio: [conectar un sistema](/wiki/conectar).
