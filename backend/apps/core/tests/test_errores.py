import pytest
from django.http import Http404
from rest_framework import serializers
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from apps.core.errores import ErrorNodo

fabrica = APIRequestFactory()


def responder_con(excepcion):
    class Vista(APIView):
        authentication_classes = []
        permission_classes = [AllowAny]

        def get(self, request):
            raise excepcion

    return Vista.as_view()(fabrica.get("/"))


def test_validacion_fallida_devuelve_el_sobre_con_detalles():
    respuesta = responder_con(
        serializers.ValidationError(
            {"patente": ["Formato inválido."], "contexto": {"procedimiento": ["Requerido."]}}
        )
    )

    assert respuesta.status_code == 400
    error = respuesta.data["error"]
    assert set(error) == {"codigo", "mensaje", "detalles"}
    assert error["codigo"] == "VALIDACION_FALLIDA"
    assert error["mensaje"]
    assert {"campo": "patente", "mensaje": "Formato inválido."} in error["detalles"]
    assert {"campo": "contexto.procedimiento", "mensaje": "Requerido."} in error["detalles"]


@pytest.mark.parametrize(
    ("excepcion", "status", "codigo"),
    [
        (Http404(), 404, "NO_ENCONTRADO"),
        (PermissionDenied(), 403, "PERMISO_DENEGADO"),
        (NotAuthenticated(), 403, "NO_AUTENTICADO"),
    ],
)
def test_excepciones_conocidas_se_traducen_a_codigos(excepcion, status, codigo):
    respuesta = responder_con(excepcion)

    assert respuesta.status_code == status
    assert respuesta.data["error"]["codigo"] == codigo
    assert respuesta.data["error"]["detalles"] == []


def test_las_excepciones_propias_conservan_codigo_mensaje_y_estado():
    class PatenteInvalida(ErrorNodo):
        codigo = "PATENTE_INVALIDA"
        mensaje = "La patente no tiene un formato válido."

    respuesta = responder_con(PatenteInvalida())

    assert respuesta.status_code == 400
    assert respuesta.data == {
        "error": {
            "codigo": "PATENTE_INVALIDA",
            "mensaje": "La patente no tiene un formato válido.",
            "detalles": [],
        }
    }


def test_una_excepcion_no_prevista_no_filtra_traza_ni_mensaje(caplog):
    respuesta = responder_con(RuntimeError("contraseña=secreta en db-interna:5432"))
    respuesta.render()
    cuerpo = respuesta.content.decode()

    assert respuesta.status_code == 500
    assert respuesta.data["error"]["codigo"] == "ERROR_INTERNO"
    assert "secreta" not in cuerpo
    assert "db-interna" not in cuerpo
    assert "Traceback" not in cuerpo
    assert "RuntimeError" not in cuerpo
    assert "contraseña=secreta" in caplog.text


def test_ruta_inexistente_responde_con_el_sobre(client, settings):
    settings.DEBUG = False

    respuesta = client.get("/api/v1/no-existe")

    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == "NO_ENCONTRADO"
