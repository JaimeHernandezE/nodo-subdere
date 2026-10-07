# Estándar de la ficha de servicio

**Versión del estándar:** 1
**Estado:** propuesta
**Fecha:** 6 de octubre de 2026
**Relacionados:** [`adr-2026-10-estructura-de-repositorios.md`](adr-2026-10-estructura-de-repositorios.md), [`adr-2026-09-estandar-legible-por-maquina.md`](adr-2026-09-estandar-legible-por-maquina.md), [`hoja-de-ruta.md`](hoja-de-ruta.md) §10, [`plantillas.md`](plantillas.md)

Este documento define el archivo con que un servicio se describe ante el Nodo SUBDERE. Es lo que un responsable de servicio tiene que escribir, y es el contrato contra el cual se construye el backend del nodo.

---

## 1. Dónde vive

Cada repositorio de servicio lleva una carpeta `nodo/` en su raíz:

```
nodo/
├── ficha.yaml              La descripción del servicio
└── <nombre>.openapi.yaml   Su contrato técnico
```

Que la carpeta se llame así tiene una ventaja práctica: cualquiera que abra el repositorio ve de inmediato qué le entrega ese servicio al nodo, y qué pasa a ser público.

La aplicación del nodo lee `nodo/ficha.yaml` con un token de solo lectura y **guarda el *commit* del que lo leyó**, de modo que cada ficha publicada se puede rastrear hasta una versión exacta del repositorio. Cuando el repositorio no responde, el catálogo muestra la última lectura buena diciendo de cuándo es.

## 2. Qué campo es de quién

La ficha la escribe el servicio. Lo que es decisión editorial del nodo **no va en la ficha**, va en el registro. Mezclarlas produce la falla clásica: alguien edita el catálogo a mano y la siguiente sincronización le pasa por encima.

| Campo | Dueño |
|---|---|
| Identificador, nombre, ámbito, clase, función, descripción | Ficha del servicio |
| Madurez, responsable, instituciones | Ficha del servicio |
| Especificación, versión y ambientes | Ficha del servicio |
| Origen del dato y la norma que lo respalda | Ficha del servicio |
| Visibilidad: publicado, oculto o retirado | Registro del nodo |
| Entrada de wiki y observaciones sobre el contrato | Registro del nodo |
| Aplicación de uso humano, cuando la construye el nodo | Registro del nodo |
| Disponibilidad | **Ninguno de los dos.** La mide el monitor |

Esa tabla es lo que hace cumplir dos reglas que ya están escritas. **La crítica va en la wiki, no en el catálogo**: la ficha no tiene campo de observaciones, así que no hay dónde escribirla. Y **madurez no es lo mismo que visibilidad**: la primera es un hecho del servicio, la segunda una decisión nuestra.

## 3. El archivo

```yaml
ficha: 1                              # versión de este estándar

id: cut                               # minúsculas, números y guiones; inmutable
nombre: Códigos Únicos Territoriales
sigla: CUT                            # opcional

ambito: Transversal                   # Transversal | SGM
clase: intercambio                    # intercambio | plataforma
intercambio: consulta                 # consulta | entrega

funcion: >
  Entrega el código único territorial de cada región, provincia y comuna,
  y permite obtener la unidad territorial a partir de su código.

descripcion: >
  Los códigos únicos territoriales son el identificador con que el Estado
  nombra regiones, provincias y comunas. El servicio los expone para que
  cualquier sistema use los mismos códigos sin mantener su propia tabla.

madurez: En desarrollo                # Deseable | En evaluación | En desarrollo | Operativo

responsable:
  organismo: SUBDERE
  equipo: Equipo SEM
  correo: nombre.apellido@subdere.gov.cl

instituciones:
  - SUBDERE
  - Municipalidades

especificacion:
  archivo: nodo/cut.openapi.yaml      # ruta dentro de este mismo repositorio
  formato: openapi-3.0
  version: 1.0.0                      # debe coincidir con info.version del archivo
  publicada: 2026-09-15

ambientes:
  - nombre: pruebas
    base: https://ejemplo.subdere.gov.cl/gescod/api/v1
    datos: inventados                 # inventados | reales
  - nombre: produccion
    base: https://ejemplo.subdere.gov.cl/gescod/api/v1
    datos: reales

origen:
  norma: Decreto Exento N° 1.115, de 2018, del Ministerio del Interior
  nota: >
    Los códigos los fija el decreto. El servicio los publica en forma
    legible por máquina; no constituye una fuente nueva.
```

## 4. Los campos

| Campo | Obligatorio | Regla |
|---|---|---|
| `ficha` | Sí | Entero. Versión del estándar. Si la aplicación no la conoce, rechaza la ficha en vez de adivinar |
| `id` | Sí | Minúsculas, números y guiones. Único en el registro y **inmutable**: cambiarlo es un servicio nuevo |
| `nombre` | Sí | Como se muestra en el catálogo |
| `sigla` | No | |
| `ambito` | Sí | De la lista cerrada de ámbitos del nodo |
| `clase` | Sí | `intercambio` o `plataforma` |
| `intercambio` | Sí | Qué hace el municipio: `consulta` o `entrega`. Decide qué capacidades del nodo aplican |
| `funcion` | Sí | Una o dos frases. Es lo que se lee en la tarjeta del catálogo |
| `descripcion` | Sí | Párrafo. Qué resuelve y para quién |
| `madurez` | Sí | De la lista cerrada |
| `responsable` | Sí | Organismo, equipo y correo institucional. Es el registro público de quién responde por el servicio |
| `instituciones` | Sí | Las que participan del intercambio |
| `especificacion` | Sí | Ruta en este repositorio, formato, versión y fecha de publicación |
| `ambientes` | No | Lista. Cada uno declara si entrega datos reales o inventados |
| `origen` | No | La norma que respalda el dato, y una nota. Obligatorio cuando el servicio publica datos que fija una norma |

**`id` inmutable no es una formalidad.** El nodo ya pasó por un renombre —`division-territorial` a `cut`— que obligó a mantener un alias para no romper los enlaces que ya habían circulado. Los identificadores no se corrigen: se crea otro y el nodo guarda el alias.

## 5. Validación

Una ficha se publica solo si pasa todo esto. Si falla, el servicio no entra y el registro guarda el motivo; no se publica nada a medio leer.

1. El archivo es YAML válido y `ficha` es una versión conocida.
2. Están todos los campos obligatorios, y los de lista cerrada traen un valor de la lista.
3. `id` no está tomado por otro servicio del registro.
4. `especificacion.archivo` existe en el mismo repositorio y en el mismo *commit*, y se puede parsear.
5. `especificacion.version` coincide con el `info.version` de ese archivo. Es una comprobación gratis y atrapa el error más común: publicar una versión y declarar otra.
6. `responsable.correo` es una dirección institucional.
7. **La ficha no contiene datos personales** más allá del contacto institucional del responsable. Sin excepciones: ya tuvimos un archivo con nombre y RUT reales versionado en este repositorio.

## 6. Dar de alta, ocultar y retirar

| Acción | Qué ocurre |
|---|---|
| **Alta** | Alguien registra la URL del repositorio. La aplicación lee la ficha, la valida y la deja en el registro como oculta |
| **Publicar** | Decisión editorial, cuando el servicio cumple el criterio de entrada: contrato, pantalla, entrada de wiki y servicio disponible |
| **Ocultar** | Sale de los listados; su ficha sigue alcanzable por enlace directo, diciendo que no está en el catálogo |
| **Retirar** | Deja de leerse el repositorio. La última lectura se conserva, porque el catálogo tiene que poder decir qué publicó y cuándo |
| **Resincronizar** | Vuelve a leer el repositorio. Si la ficha cambió, queda una versión nueva en el registro con su *commit* y su fecha |

Esto es el procedimiento de registro que estaba pendiente, convertido en mecanismo: validar un archivo contra un esquema y comprobar que la especificación que declara se puede parsear.

## 7. Versión de este estándar

`ficha: 1`. Agregar campos opcionales no cambia la versión. Quitar un campo, volverlo obligatorio o cambiar el significado de uno existente sube a `2`, y la aplicación tiene que seguir leyendo las fichas en versión 1 mientras alguna quede.

Es la misma regla que el nodo le pide a los contratos que publica: ninguna versión se corrige.

## 8. Lo que deliberadamente no está

- **Disponibilidad y tiempos de respuesta.** Los mide el monitor. Una ficha que los declara miente la primera vez que el servicio se cae.
- **Observaciones sobre el contrato.** Van en la wiki.
- **Credenciales, URLs internas y nombres de servidores.** La ficha es pública en cuanto el nodo la publica.
- **Cuotas y permisos.** Son de la puerta de acceso, no del catálogo.
