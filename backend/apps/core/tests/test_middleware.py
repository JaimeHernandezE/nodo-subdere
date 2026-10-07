from django.http import HttpResponse
from django.test import RequestFactory

from apps.core.middleware import ContextoMiddleware

ORIGEN = "http://localhost:5173"


def test_con_nodo_oculto_toda_respuesta_lleva_x_robots_tag(client, settings):
    settings.NODO_OCULTO = True

    assert client.get("/api/v1/salud")["X-Robots-Tag"] == "noindex, nofollow"
    assert client.get("/api/v1/no-existe")["X-Robots-Tag"] == "noindex, nofollow"


def test_sin_nodo_oculto_ninguna_respuesta_lleva_x_robots_tag(client, settings):
    settings.NODO_OCULTO = False

    assert "X-Robots-Tag" not in client.get("/api/v1/salud")
    assert "X-Robots-Tag" not in client.get("/api/v1/no-existe")


def test_el_contexto_deja_procedimiento_e_id_de_tramite_en_la_peticion():
    capturada = {}

    def vista(request):
        capturada["request"] = request
        return HttpResponse()

    peticion = RequestFactory().get(
        "/", HTTP_X_PROCEDIMIENTO=" permiso-circulacion ", HTTP_X_ID_TRAMITE="T-123"
    )
    ContextoMiddleware(vista)(peticion)

    assert capturada["request"].procedimiento == "permiso-circulacion"
    assert capturada["request"].id_tramite == "T-123"


def test_el_contexto_deja_cadenas_vacias_si_no_vienen_las_cabeceras():
    capturada = {}

    def vista(request):
        capturada["request"] = request
        return HttpResponse()

    ContextoMiddleware(vista)(RequestFactory().get("/"))

    assert capturada["request"].procedimiento == ""
    assert capturada["request"].id_tramite == ""


def test_cors_acepta_la_peticion_previa_con_x_procedimiento(client, settings):
    settings.CORS_ALLOWED_ORIGINS = [ORIGEN]

    respuesta = client.options(
        "/api/v1/salud",
        HTTP_ORIGIN=ORIGEN,
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
        HTTP_ACCESS_CONTROL_REQUEST_HEADERS="x-procedimiento, x-id-tramite",
    )

    assert respuesta.status_code == 200
    assert respuesta["Access-Control-Allow-Origin"] == ORIGEN
    permitidas = respuesta["Access-Control-Allow-Headers"]
    assert "x-procedimiento" in permitidas
    assert "x-id-tramite" in permitidas


def test_cors_no_responde_a_un_origen_no_permitido(client, settings):
    settings.CORS_ALLOWED_ORIGINS = [ORIGEN]

    respuesta = client.options(
        "/api/v1/salud",
        HTTP_ORIGIN="https://otro.example",
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
        HTTP_ACCESS_CONTROL_REQUEST_HEADERS="x-procedimiento",
    )

    assert "Access-Control-Allow-Origin" not in respuesta
