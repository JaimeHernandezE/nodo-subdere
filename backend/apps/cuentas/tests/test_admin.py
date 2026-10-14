import pytest
from django.contrib.auth import get_user_model

from apps.cuentas.models import Bitacora, Perfil

pytestmark = pytest.mark.django_db

URL = "/admin/cuentas/perfil/add/"


@pytest.fixture
def superusuario(client):
    usuario = get_user_model().objects.create_superuser("raiz", password="clave-de-prueba")
    client.force_login(usuario)
    return client


def crear(cliente, **cambios):
    datos = {"run_texto": "12.345.678-5", "nombre": "Ana Pérez", "rol": "administrador"}
    datos.update(cambios)
    if datos.pop("activo", True):
        datos["activo"] = "on"
    return cliente.post(URL, datos)


def test_un_superusuario_crea_el_primer_administrador(superusuario):
    respuesta = crear(superusuario)

    assert respuesta.status_code == 302
    perfil = Perfil.objects.get()
    assert (perfil.run_numero, perfil.run_dv, perfil.rol) == (12345678, "5", "administrador")
    assert Bitacora.objects.filter(accion="crear_perfil").exists()


@pytest.mark.parametrize("texto", ["12345678-9", "abc", "1"])
def test_un_run_invalido_se_muestra_en_el_formulario_y_no_da_500(superusuario, texto):
    respuesta = crear(superusuario, run_texto=texto)

    assert respuesta.status_code == 200
    assert "run_texto" in respuesta.context["adminform"].form.errors
    assert not Perfil.objects.exists()


def test_un_run_repetido_se_muestra_en_el_formulario_y_no_da_500(superusuario):
    crear(superusuario)

    respuesta = crear(superusuario, run_texto="12345678-5", nombre="Otra")

    assert respuesta.status_code == 200
    errores = respuesta.context["adminform"].form.errors["run_texto"]
    assert "Ya existe un perfil con ese RUN." in errores
    assert Perfil.objects.count() == 1
