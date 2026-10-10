::: aviso
**Demostración.** La especificación que se comenta acá es una propuesta reconstruida por el equipo del Nodo, no el contrato del servicio.
:::

## Saber si un vehículo tiene su permiso al día, sin importar dónde lo pagó

El permiso de circulación lo cobra cada municipio y es uno de sus ingresos propios. Pero quien necesita comprobar que un vehículo lo tiene al día casi nunca es el municipio que lo cobró: es otro municipio, una institución que fiscaliza en la calle, o el propio dueño.

Ese desajuste —el que cobra y el que consulta no son el mismo— es lo que hace del permiso de circulación un buen ejemplo de por qué conviene que los sistemas se hablen, y no solo un trámite municipal más.

[Abrir la consulta](/servicios/consulta-permiso-circulacion) · [Ver la especificación](/apis/permisos-de-circulacion)

## Tres formas de patente, las tres aceptadas

Toda la consulta parte de la patente, así que el contrato tiene que decir exactamente qué acepta. Hoy conviven dos formatos, más el de las patentes provisorias.

| Formato | Estructura | Ejemplo | Cuándo aparece |
|---|---|---|---|
| **Antiguo** | Dos letras y cuatro dígitos | `AB0251` | Vehículos inscritos hasta el cambio de formato. Siguen circulando |
| **Actual** | Cuatro letras y dos dígitos | `BDPF18` | Inscripciones recientes |
| **Provisoria** | `PR` y cuatro dígitos | `PR0909` | Vehículos sin inscripción definitiva, en poder de una automotora |

Con la regla escrita en el contrato, un sistema puede revisar la patente antes de preguntar, y si está mal escrita el servicio responde con un mensaje claro en vez de una respuesta vacía. La colección de referencia traía ejemplos de los tres tipos, pero no decía en ninguna parte cuál era la regla.

::: tecnico
**Para quien programa:** la regla queda como expresión regular en el propio parámetro.
:::

## Un vehículo, varios permisos, una comuna por permiso

La forma de los datos es simple, y conviene tenerla presente porque es lo que ordena el contrato.

::::: tarjetas
:::: tarjeta
**01**

### El vehículo no cambia

Marca, modelo, color, año y tipo van con la patente, no con el permiso. Por eso se piden por separado: quien solo quiere identificar el vehículo no necesita traerse todo el historial de pagos.
::::

:::: tarjeta
**02**

### El permiso es anual y puede cambiar de comuna

Cada año se paga un permiso, y no necesariamente en la misma comuna: el dueño puede cambiarse de domicilio. El historial muestra esos cambios, que le sirven al propio municipio.
::::

:::: tarjeta
**03**

### El pago puede venir en cuotas

Un permiso se paga en una o dos cuotas, cada una con su fecha y su medio de pago. Si el permiso está vigente o vencido no se calcula a partir de las cuotas: viene dicho.
::::
:::::

## La comuna viaja como código, no como nombre

En la colección de referencia, la municipalidad que cobró venía escrita a mano: `NUNOA`, `SAN FELIPE`, `LA REINA`, `MARCHIHUE`. Sin tildes y sin código.

Eso obliga a cada sistema a adivinar. *Nunoa* y *Ñuñoa* son la misma comuna para una persona y dos palabras distintas para un programa. Además hay nombres de comuna repetidos en distintas regiones, así que ni siquiera un nombre bien escrito identifica un lugar.

En la propuesta de contrato, la comuna va con su **Código Único Territorial** y su nombre. El código identifica; el nombre va solo para que una persona pueda leer la respuesta.

::: aviso
Es la primera vez que un estándar publicado por el Nodo se usa dentro de otro intercambio. Esa es justamente la razón de tener un catálogo: si cada servicio inventa su propia forma de nombrar una comuna, el catálogo es una lista de servicios y no un estándar. Más en la entrada de los [Códigos Únicos Territoriales](/wiki/cut).
:::

## De la colección de referencia a la propuesta de contrato

La colección que entregó el equipo de Servicios Municipales es un registro de las consultas que alguien hizo para probar el servicio. Sirve muy bien para eso, pero no para publicarse como estándar. Estas son las diferencias, y también la agenda de la conversación.

| Qué mejora | En la colección de referencia | En la propuesta de contrato |
|---|---|---|
| **Una sola forma de preguntar por cualquier vehículo** | La patente va dentro de la ruta: cuatro direcciones fijas, una por cada vehículo consultado | La patente es un parámetro, con su formato declarado. Una sola operación sirve para cualquier vehículo |
| **Las respuestas se parecen entre sí** | Dos envoltorios distintos: un objeto con `data` para unas operaciones, un arreglo pelado para otras | Una sola forma de respuesta por tipo de recurso |
| **Cuando algo sale mal, se sabe qué fue** | Solo se declara la respuesta correcta. No hay errores | Tres errores declarados —patente inválida, sin autorización y no encontrado— con una forma común de `codigo` y `mensaje` |
| **Queda claro quién puede entrar** | Sin esquema de autenticación | Credencial de corta duración entregada por la [puerta de acceso](/wiki/glosario#puerta-de-acceso), declarada en el contrato |
| **Las fechas no se malinterpretan** | Fechas como texto en formato local | Fechas ISO 8601. La conversión al formato que lee una persona la hace la pantalla, no el contrato |
| **La comuna se identifica sin adivinar** | La comuna como nombre escrito a mano | La comuna con su Código Único Territorial |
| **El contrato sirve en cualquier servidor** | El servidor de pruebas queda escrito dentro del contrato | Ruta base relativa. Dónde vive el servicio lo decide quien lo despliega |
| **No circulan datos de personas reales** | Los ejemplos incluyen el nombre y el RUT del representante de una automotora | La respuesta entrega la persona jurídica titular y no los datos de su representante. Todos los ejemplos son inventados |

::: aviso
**La última fila es la que conviene resolver primero.** Una especificación viaja por correo, se sube a repositorios y se publica en catálogos, y los datos personales de sus ejemplos viajan con ella. Para que un contrato se pueda publicar sin que nadie tenga que revisarlo antes, sus ejemplos tienen que ser inventados desde el principio.
:::

## Preguntas para el equipo de Servicios Municipales

Escribimos la propuesta desde fuera, mirando las respuestas de ejemplo. Hay cosas que no se pueden deducir de ahí y que tenemos que preguntar.

1. ¿Qué parte de este registro es de acceso público y qué parte exige acreditar un interés? Hoy la propuesta trata todo igual, y probablemente no corresponda.
1. ¿El servicio conoce los permisos de todos los municipios, o solo de los que usan la plataforma de Servicios Municipales? De eso depende qué significa que una patente no aparezca.
1. ¿Con qué frecuencia se actualiza? Un permiso pagado hoy, ¿está disponible hoy o mañana?
1. ¿Existe el caso de un mismo año con permisos en dos comunas distintas, y qué significa cuando ocurre?
1. ¿Qué hace falta para que el registro entregue el código de comuna en vez del nombre?

*Propuesta de contrato escrita por el equipo del Nodo a partir de una colección de referencia de Servicios Municipales.*
