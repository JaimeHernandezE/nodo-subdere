import pytest

from apps.catalogo.models import Nodo, Visibilidad
from apps.cuentas.models import Bitacora
from apps.registro.models import Fuente, Lectura
from apps.registro.sincronizacion import sincronizar

from .conftest import COMMIT_1, URL

pytestmark = pytest.mark.django_db

NUEVA = "https://gitlab.prueba/sem/cut"


def error(respuesta) -> str:
    return respuesta.json()["error"]["codigo"]


# Registrar


def test_registrar_una_fuente_la_lee_en_el_acto(como, administrador, repositorio):
    respuesta = como(administrador).post("/api/v1/fuentes", {"url": URL}, format="json")

    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert (datos["rama"], datos["ruta_ficha"], datos["activa"]) == (
        "main",
        "nodo/ficha.yaml",
        True,
    )
    assert datos["nodo_identificador"] == "cut"
    assert datos["ultima_lectura"]["valida"] is True
    assert datos["ultima_lectura"]["commit"] == COMMIT_1
    administrador.refresh_from_db()
    assert datos["ultima_lectura"]["perfil"] == administrador.nombre

    registro = Bitacora.objects.get(accion="registrar_fuente")
    assert registro.perfil == administrador
    assert registro.objeto == f"registro.Fuente:{datos['id']}"
    assert Bitacora.objects.get(accion="sincronizar_nodo").perfil == administrador


def test_la_fuente_se_crea_aunque_la_lectura_falle(como, administrador, repositorio):
    repositorio.falla = "GitLab no respondió."

    respuesta = como(administrador).post("/api/v1/fuentes", {"url": URL}, format="json")

    assert respuesta.status_code == 201
    assert respuesta.json()["nodo_identificador"] == ""
    assert respuesta.json()["ultima_lectura"]["motivo"] == "GitLab no respondió."
    assert Fuente.objects.count() == 1
    assert not Nodo.objects.exists()


@pytest.mark.parametrize(
    "url",
    ["https://github.com/modernizacion/cut", "http://gitlab.prueba/modernizacion/cut"],
)
def test_una_direccion_fuera_del_gitlab_del_nodo_se_rechaza(como, administrador, url):
    respuesta = como(administrador).post("/api/v1/fuentes", {"url": url}, format="json")

    assert respuesta.status_code == 400
    assert respuesta.json()["error"]["detalles"][0]["campo"] == "url"


def test_la_misma_direccion_rama_y_ruta_no_se_registra_dos_veces(como, administrador, fuente):
    respuesta = como(administrador).post("/api/v1/fuentes", {"url": f"{URL}/"}, format="json")

    assert respuesta.status_code == 400
    assert "Ya hay una fuente" in respuesta.json()["error"]["detalles"][0]["mensaje"]


def test_tipo_y_nodo_identificador_no_se_escriben(como, administrador, repositorio):
    respuesta = como(administrador).post(
        "/api/v1/fuentes",
        {"url": URL, "tipo": "carga_manual", "nodo_identificador": "otro"},
        format="json",
    )

    assert respuesta.status_code == 201
    assert (respuesta.json()["tipo"], respuesta.json()["nodo_identificador"]) == (
        "repositorio",
        "cut",
    )


@pytest.mark.parametrize("quien", ["lector", "curador"])
def test_solo_un_administrador_registra_fuentes(como, request, quien):
    respuesta = como(request.getfixturevalue(quien)).post(
        "/api/v1/fuentes", {"url": URL}, format="json"
    )
    assert respuesta.status_code == 403


def test_sin_sesion_no_se_ven_las_fuentes(client, fuente):
    assert client.get("/api/v1/fuentes").status_code == 401


def test_un_lector_lista_las_fuentes_con_su_ultima_lectura(como, lector, fuente, repositorio):
    sincronizar(fuente)

    datos = como(lector).get("/api/v1/fuentes").json()

    assert [f["nodo_identificador"] for f in datos] == ["cut"]
    assert datos[0]["ultima_lectura"]["valida"] is True
    assert datos[0]["ultima_lectura"]["perfil"] is None


# Modificar (prueba 7)


def test_cambiar_la_url_conserva_el_nodo_y_su_identificador(
    como, administrador, fuente, repositorio
):
    sincronizar(fuente)
    nodo = Nodo.objects.get()

    respuesta = como(administrador).patch(
        f"/api/v1/fuentes/{fuente.pk}", {"url": NUEVA}, format="json"
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["url"] == NUEVA
    assert respuesta.json()["nodo_identificador"] == "cut"
    assert sincronizar(fuente).valida
    assert Nodo.objects.get().pk == nodo.pk
    entrada = Bitacora.objects.get(accion="modificar_fuente")
    assert (entrada.antes["url"], entrada.despues["url"]) == (URL, NUEVA)


def test_dar_de_baja_una_fuente_no_retira_el_nodo(como, administrador, fuente, repositorio):
    sincronizar(fuente)

    respuesta = como(administrador).patch(
        f"/api/v1/fuentes/{fuente.pk}", {"activa": False}, format="json"
    )

    assert respuesta.status_code == 200
    assert Nodo.objects.get().visibilidad == Visibilidad.OCULTO


def test_una_modificacion_sin_cambios_no_deja_bitacora(como, administrador, fuente):
    como(administrador).patch(f"/api/v1/fuentes/{fuente.pk}", {"rama": "main"}, format="json")
    assert not Bitacora.objects.filter(accion="modificar_fuente").exists()


def test_un_curador_no_modifica_fuentes(como, curador, fuente):
    respuesta = como(curador).patch(
        f"/api/v1/fuentes/{fuente.pk}", {"activa": False}, format="json"
    )
    assert respuesta.status_code == 403


def test_una_fuente_no_se_borra_por_la_api(como, administrador, fuente):
    assert como(administrador).delete(f"/api/v1/fuentes/{fuente.pk}").status_code == 405


# Sincronizar


def test_un_curador_resincroniza_y_recibe_la_lectura(como, curador, fuente, repositorio):
    respuesta = como(curador).post(f"/api/v1/fuentes/{fuente.pk}/sincronizar")

    assert respuesta.status_code == 200
    assert respuesta.json()["valida"] is True
    curador.refresh_from_db()
    assert respuesta.json()["perfil"] == curador.nombre
    assert Lectura.objects.get().perfil == curador


def test_una_lectura_invalida_tambien_es_una_respuesta_200(como, curador, fuente, repositorio):
    repositorio.falla = "GitLab no respondió."

    respuesta = como(curador).post(f"/api/v1/fuentes/{fuente.pk}/sincronizar")

    assert respuesta.status_code == 200
    assert respuesta.json()["valida"] is False


def test_resincronizar_un_nodo_retirado_es_409(como, curador, fuente, repositorio):
    sincronizar(fuente)
    Nodo.objects.filter(identificador="cut").update(visibilidad=Visibilidad.RETIRADO)

    respuesta = como(curador).post(f"/api/v1/fuentes/{fuente.pk}/sincronizar")

    assert respuesta.status_code == 409
    assert error(respuesta) == "FUENTE_DE_NODO_RETIRADO"


def test_resincronizar_una_fuente_inactiva_es_409(como, curador, fuente, repositorio):
    Fuente.objects.filter(pk=fuente.pk).update(activa=False)

    respuesta = como(curador).post(f"/api/v1/fuentes/{fuente.pk}/sincronizar")

    assert respuesta.status_code == 409
    assert error(respuesta) == "FUENTE_INACTIVA"


def test_un_lector_no_resincroniza(como, lector, fuente):
    assert como(lector).post(f"/api/v1/fuentes/{fuente.pk}/sincronizar").status_code == 403


def test_resincronizar_una_fuente_que_no_existe_es_404(como, curador):
    respuesta = como(curador).post("/api/v1/fuentes/999/sincronizar")
    assert (respuesta.status_code, error(respuesta)) == (404, "NO_ENCONTRADO")


# Lecturas


def test_el_historial_de_lecturas_va_de_la_mas_reciente_a_la_mas_antigua(
    como, lector, fuente, repositorio
):
    sincronizar(fuente)
    repositorio.falla = "GitLab no respondió."
    sincronizar(fuente)

    datos = como(lector).get(f"/api/v1/fuentes/{fuente.pk}/lecturas").json()

    assert [lectura["valida"] for lectura in datos] == [False, True]
    assert datos[1]["commit"] == COMMIT_1
    assert datos[1]["contenido"].startswith("ficha: 1")


def test_las_lecturas_de_una_fuente_que_no_existe_son_404(como, lector):
    assert como(lector).get("/api/v1/fuentes/999/lecturas").status_code == 404


# De punta a punta con el catálogo


def test_un_nodo_registrado_aparece_oculto_en_el_catalogo(como, administrador, repositorio):
    como(administrador).post("/api/v1/fuentes", {"url": URL}, format="json")
    cliente = como(administrador)

    todas = cliente.get("/api/v1/nodos?visibilidad=todas").json()
    publicos = cliente.get("/api/v1/nodos").json()

    assert [(n["identificador"], n["visibilidad"]) for n in todas] == [("cut", "oculto")]
    assert publicos == []
