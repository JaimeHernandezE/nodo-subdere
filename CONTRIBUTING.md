# Cómo contribuir

Gracias por querer aportar al Nodo SUBDERE. Esta guía explica cómo proponer un cambio, qué se revisa antes de integrarlo y qué partes del repositorio tienen reglas propias.

---

## El flujo en una línea

**Nada entra directo a `main`.** Todo cambio —incluidos los del mantenedor— llega por una rama y un Pull Request revisado por otra persona.

`main` es lo que está publicado: cada push que toca `prototipos/` despliega la maqueta en [GitHub Pages](https://jaimehernandeze.github.io/nodo-subdere/). Por eso está protegida.

---

## Antes de empezar

- **Cambios pequeños** (una errata, un enlace roto, una aclaración): abre el Pull Request directamente.
- **Cambios que afectan contenido, diseño o el modelo del catálogo:** abre primero un *issue* y descríbelo. Es más barato discutir una pantalla antes de construirla que después.

Si tienes acceso de escritura al repositorio, trabaja en una rama dentro de él. Si no, haz un *fork* y trabaja en tu copia.

**Se trabaja en GitHub**, en [`JaimeHernandezE/nodo-subdere`](https://github.com/JaimeHernandezE/nodo-subdere). El repositorio en GitLab SUBDERE es un espejo que el job `sync_from_github` de [`.gitlab-ci.yml`](.gitlab-ci.yml) sobrescribe con `git push --mirror`: no hagas push ni abras Merge Requests allá.

---

## Paso a paso

```bash
# 1. Partir de lo último
git switch main
git pull

# 2. Una rama por tarea
git switch -c docs/aclara-composicion-cut

# 3. Editar, revisar y guardar
git add <archivos>
git commit -m "Aclara cómo se compone el CUT en la wiki"

# 4. Subir la rama
git push -u origin docs/aclara-composicion-cut
```

Luego, en GitHub, abre un Pull Request hacia `main` y completa la plantilla. Si te piden cambios, agrégalos como commits nuevos en la misma rama: el Pull Request se actualiza solo.

**Si trabajas desde un fork**, mantén tu copia al día con el repositorio original:

```bash
git remote add upstream https://github.com/JaimeHernandezE/nodo-subdere
git fetch upstream
git rebase upstream/main
```

### Nombres de rama

| Prefijo | Para qué |
|---|---|
| `feat/` | Una pantalla, un servicio o una funcionalidad nueva |
| `fix/` | Corregir algo que no funciona como debe |
| `docs/` | Documentación en `docs/` o contenido de la wiki |
| `estilo/` | Cambios visuales sin cambio de contenido |
| `chore/` | Configuración, workflows, mantenimiento |

### Mensajes de commit

En español, en presente y diciendo qué cambia: *«Agrega la ficha del servicio de fiscalización»*, no *«cambios»* ni *«fix»*. Un commit por idea cuando sea posible.

### Tamaño

Un Pull Request, una tarea. Es preferible abrir tres Pull Requests cortos que uno que mezcle una pantalla nueva, un ajuste de estilos y una corrección de la wiki: se revisan más rápido y, si uno tiene problemas, no frena a los otros.

---

## Reglas por carpeta

### `prototipos/` — la maqueta

- **Sin build ni dependencias.** HTML, CSS y JS a mano. No agregues frameworks, empaquetadores ni librerías por CDN sin discutirlo antes en un *issue*.
- **Pruébala servida, no con doble clic.** `404.html` y las fichas con especificación no funcionan desde el disco:

  ```bash
  python -m http.server 8000 --directory prototipos
  # http://localhost:8000
  ```

- **El catálogo vive en `assets/data.js`.** Es la semilla del modelo que después tendrá el backend: si agregas o cambias un campo, actualiza también [`docs/maqueta.md`](docs/maqueta.md).
- **Los datos de las pantallas de servicio son de demostración** y deben decirlo en pantalla.

### `prototipos/estandares/` — los contratos

**No se editan.** Cada archivo OpenAPI es copia fiel del contrato que entregó su equipo responsable, y su valor es precisamente ser auditable. Si encuentras un error o una ambigüedad en un contrato, la observación va en su entrada de wiki, no en el archivo. Solo se reemplaza un contrato cuando su dueño entrega una versión nueva.

### `docs/` — decisiones y documentación

- Una decisión de arquitectura nueva se escribe como ADR, siguiendo el formato de [`adr-2026-09-estandar-legible-por-maquina.md`](docs/adr-2026-09-estandar-legible-por-maquina.md).
- Si agregas un documento, súmalo a la tabla de [`docs/README.md`](docs/README.md).
- No dupliques una decisión que ya está escrita: enlázala.

### `backend/` y `frontend/`

Todavía están en su estructura inicial. Cada uno tiene su README con cómo levantarlo y qué herramientas usa (`pytest` y `ruff` en el backend; Vitest y Testing Library en el frontend). Cuando haya código, los Pull Requests que lo toquen deben pasar las pruebas y el linter.

---

## Las dos reglas del proyecto

Toda contribución se revisa también contra estas dos, que están explicadas en el [README](README.md):

1. **Nadie tiene atajos.** Ninguna pantalla —tampoco las de SUBDERE— accede a datos que la interfaz pública no expone.
2. **La crítica va en la wiki, no en el catálogo.** El catálogo publica cada contrato tal como se entregó.

---

## Detalles técnicos

- **Finales de línea:** el repositorio los normaliza con [`.gitattributes`](.gitattributes). Si al abrir un Pull Request aparecen archivos modificados cuyo contenido no cambiaste, descártalos con `git checkout -- <archivo>`.
- **Nada de secretos en el repositorio.** Los `.env` reales no se suben; solo los `.env.example`.

---

## Qué pasa después

1. Alguien revisa el Pull Request y comenta.
2. Cuando está aprobado, se integra con **Squash and merge**: queda un solo commit en `main`.
3. Si tocaba `prototipos/`, la maqueta se republica sola en unos minutos.
4. La rama se borra. La réplica a GitLab ocurre en la siguiente sincronización programada.

Dudas o comentarios: jaime.hernandez@subdere.gov.cl — División de Políticas y Estudios, SUBDERE.
