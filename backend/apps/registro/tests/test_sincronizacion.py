import pytest
from django.core.management import call_command

from apps.catalogo.models import Alias, Especificacion, Formato, Nodo, Visibilidad, huella
from apps.core import run
from apps.cuentas.models import Bitacora, RegistroInmutable
from apps.registro.errores import FuenteDeNodoRetirado, FuenteInactiva
from apps.registro.models import Fuente, Lectura
from apps.registro.sincronizacion import sincronizar

from .conftest import (
    COMMIT_1,
    COMMIT_2,
    QUITAR,
    RUTA_CONTRATO,
    RUTA_FICHA,
    URL,
    contrato,
    ficha,
)

pytestmark = pytest.mark.django_db


def sincronizaciones():
    return Bitacora.objects.filter(accion="sincronizar_nodo")


def rechazada(fuente, repositorio, **cambios) -> Lectura:
    repositorio.archivos[RUTA_FICHA] = ficha(**cambios)
    lectura = sincronizar(fuente)
    assert not lectura.valida
    return lectura


# Prueba 1


def test_una_ficha_valida_crea_el_nodo_oculto_con_su_especificacion_vigente(fuente, repositorio):
    lectura = sincronizar(fuente)

    assert lectura.valida, lectura.motivo
    nodo = Nodo.objects.get(identificador="cut")
    assert nodo.visibilidad == Visibilidad.OCULTO
    assert nodo.ambito.nombre == "Transversal"
    assert nodo.instituciones == ["SUBDERE", "Municipalidades"]
    assert nodo.procedencia_copia == "exacta"
    vigente = nodo.especificacion_vigente
    assert (vigente.version, vigente.formato) == ("1.0.0", Formato.OPENAPI_30)
    assert vigente.huella == huella(contrato())
    assert vigente.publicada.isoformat() == "2026-09-15"
    fuente.refresh_from_db()
    assert fuente.nodo_identificador == "cut"


def test_la_tarea_programada_deja_bitacora_sin_perfil_con_nota(fuente, repositorio):
    sincronizar(fuente)

    entrada = sincronizaciones().get()
    assert entrada.perfil is None
    assert entrada.objeto == "catalogo.Nodo:cut"
    assert entrada.nota == f"Sincronización programada: fuente {fuente.pk}, commit {COMMIT_1}"
    assert entrada.antes == {}
    assert entrada.despues["especificacion"]["version"] == "1.0.0"


# Prueba 2


def test_una_version_del_estandar_desconocida_se_rechaza_sin_tocar_la_proyeccion(
    fuente, repositorio
):
    sincronizar(fuente)
    antes = Nodo.objects.get().leido_en

    lectura = rechazada(fuente, repositorio, ficha=2, nombre="Otro nombre")

    assert "versión del estándar desconocida" in lectura.motivo
    nodo = Nodo.objects.get()
    assert (nodo.nombre, nodo.leido_en) == ("Códigos Únicos Territoriales", antes)


@pytest.mark.parametrize("contenido", ["ficha: [1", "- una lista", ""])
def test_un_yaml_roto_o_que_no_es_un_grupo_se_rechaza(fuente, repositorio, contenido):
    repositorio.archivos[RUTA_FICHA] = contenido
    lectura = sincronizar(fuente)

    assert not lectura.valida
    assert lectura.contenido == contenido
    assert not Nodo.objects.exists()


# Prueba 3


def test_una_version_que_no_coincide_con_la_del_archivo_se_rechaza_nombrando_las_dos(
    fuente, repositorio
):
    repositorio.archivos[RUTA_CONTRATO] = contrato(version="1.1.0")
    lectura = sincronizar(fuente)

    assert not lectura.valida
    assert "«1.0.0»" in lectura.motivo and "«1.1.0»" in lectura.motivo


def test_el_formato_tiene_que_calzar_con_la_version_de_openapi(fuente, repositorio):
    repositorio.archivos[RUTA_CONTRATO] = contrato(openapi="3.1.0")
    lectura = sincronizar(fuente)

    assert not lectura.valida
    assert lectura.motivo.startswith("especificacion.formato:")


def test_un_archivo_declarado_que_no_existe_se_rechaza(fuente, repositorio):
    del repositorio.archivos[RUTA_CONTRATO]
    lectura = sincronizar(fuente)

    assert not lectura.valida
    assert lectura.motivo.startswith("especificacion.archivo:")


# Prueba 4


def test_un_id_de_otra_fuente_se_rechaza(fuente, repositorio):
    Fuente.objects.create(url=f"{URL}-viejo", nodo_identificador="cut")
    lectura = sincronizar(fuente)

    assert not lectura.valida
    assert "ya es el de otro nodo" in lectura.motivo


def test_un_id_que_es_un_alias_se_rechaza(fuente, repositorio):
    Alias.objects.create(identificador="cut", destino="codigos-territoriales")
    lectura = sincronizar(fuente)

    assert not lectura.valida
    assert "nombre antiguo de «codigos-territoriales»" in lectura.motivo


def test_un_id_distinto_del_que_proyecta_la_fuente_es_un_servicio_nuevo(fuente, repositorio):
    sincronizar(fuente)
    lectura = rechazada(fuente, repositorio, id="cut-2")

    assert "inmutable" in lectura.motivo
    assert not Nodo.objects.filter(identificador="cut-2").exists()


@pytest.mark.parametrize("identificador", ["CUT", "cut_2", "-cut", "cut-"])
def test_el_id_usa_solo_minusculas_numeros_y_guiones(fuente, repositorio, identificador):
    lectura = rechazada(fuente, repositorio, id=identificador)
    assert lectura.motivo.startswith("id:")


# Prueba 5


def test_un_fallo_de_red_deja_lectura_invalida_y_no_toca_el_nodo_publicado(fuente, repositorio):
    sincronizar(fuente)
    Nodo.objects.filter(identificador="cut").update(visibilidad=Visibilidad.PUBLICADO)
    antes = Nodo.objects.get()

    repositorio.falla = "GitLab no respondió."
    lectura = sincronizar(fuente)

    assert not lectura.valida
    assert (lectura.motivo, lectura.commit, lectura.contenido) == ("GitLab no respondió.", "", "")
    nodo = Nodo.objects.get()
    assert nodo.visibilidad == Visibilidad.PUBLICADO
    assert (nodo.leido_en, nodo.commit) == (antes.leido_en, antes.commit)
    assert nodo.especificacion_vigente is not None


# Prueba 6


def test_el_mismo_contenido_con_otro_commit_solo_actualiza_leido_en_y_commit(fuente, repositorio):
    sincronizar(fuente)
    primero = Nodo.objects.get()

    repositorio.commit = COMMIT_2
    lectura = sincronizar(fuente)

    assert lectura.valida
    nodo = Nodo.objects.get()
    assert nodo.commit == COMMIT_2
    assert nodo.leido_en > primero.leido_en
    assert sincronizaciones().count() == 1
    assert Especificacion.objects.count() == 1


# Prueba 9


def test_la_misma_version_con_otro_contenido_se_rechaza_nombrando_la_version(fuente, repositorio):
    sincronizar(fuente)
    repositorio.archivos[RUTA_CONTRATO] = contrato(extra="paths: {}\n")

    lectura = sincronizar(fuente)

    assert not lectura.valida
    assert "la versión 1.0.0 ya está registrada" in lectura.motivo
    assert Especificacion.objects.get().huella == huella(contrato())


# Prueba 10


def test_una_plataforma_sin_archivo_se_proyecta_como_solo_metadato(fuente, repositorio):
    repositorio.archivos[RUTA_FICHA] = ficha(
        clase="plataforma",
        intercambio=QUITAR,
        especificacion__archivo=QUITAR,
        especificacion__formato="descripcion",
    )
    lectura = sincronizar(fuente)

    assert lectura.valida, lectura.motivo
    nodo = Nodo.objects.get()
    assert (nodo.clase, nodo.intercambio) == ("plataforma", "")
    vigente = nodo.especificacion_vigente
    assert (vigente.formato, vigente.ruta, vigente.contenido) == (Formato.DESCRIPCION, "", "")
    assert repositorio.pedidos == [("main", RUTA_FICHA)]


def test_una_plataforma_no_lleva_intercambio(fuente, repositorio):
    lectura = rechazada(fuente, repositorio, clase="plataforma")
    assert lectura.motivo.startswith("intercambio:")


def test_sin_archivo_el_formato_es_descripcion(fuente, repositorio):
    lectura = rechazada(fuente, repositorio, especificacion__archivo=QUITAR)
    assert lectura.motivo.startswith("especificacion.formato:")


# Prueba 11


def test_una_fuente_cuyo_nodo_esta_retirado_no_se_lee(fuente, repositorio):
    sincronizar(fuente)
    Nodo.objects.filter(identificador="cut").update(visibilidad=Visibilidad.RETIRADO)
    repositorio.pedidos.clear()

    call_command("sincronizar_fuentes")

    assert repositorio.pedidos == []
    assert Lectura.objects.count() == 1
    with pytest.raises(FuenteDeNodoRetirado):
        sincronizar(fuente)


def test_una_fuente_inactiva_no_se_lee(fuente, repositorio):
    Fuente.objects.filter(pk=fuente.pk).update(activa=False)

    call_command("sincronizar_fuentes")

    assert repositorio.pedidos == []
    with pytest.raises(FuenteInactiva):
        sincronizar(fuente)


def test_el_comando_lee_todas_las_fuentes_activas(fuente, repositorio, capsys):
    call_command("sincronizar_fuentes")

    assert Lectura.objects.get().valida
    assert "1 válidas, 0 inválidas." in capsys.readouterr().out


# Prueba 12


def test_la_proyeccion_deja_leido_en_y_commit_y_el_contrato_se_lee_en_ese_commit(
    fuente, repositorio
):
    lectura = sincronizar(fuente)

    nodo = Nodo.objects.get()
    assert nodo.commit == lectura.commit == COMMIT_1
    assert nodo.leido_en >= lectura.creado_en.replace(microsecond=0)
    assert nodo.especificacion_vigente.commit == COMMIT_1
    assert repositorio.pedidos == [("main", RUTA_FICHA), (COMMIT_1, RUTA_CONTRATO)]


# Prueba 13


@pytest.mark.parametrize(
    ("cambios", "campo"),
    [
        ({"sigla": "S" * 31}, "sigla:"),
        ({"nombre": "N" * 201}, "nombre:"),
        ({"especificacion__version": "1." * 26}, "especificacion.version:"),
        ({"responsable__correo": "no-es-un-correo"}, "responsable.correo:"),
    ],
)
def test_un_campo_demasiado_largo_o_mal_formado_deja_un_motivo(fuente, repositorio, cambios, campo):
    lectura = rechazada(fuente, repositorio, **cambios)
    assert lectura.motivo.startswith(campo)


@pytest.mark.parametrize("version", [1.1, 1])
def test_una_version_numerica_pide_comillas(fuente, repositorio, version):
    lectura = rechazada(fuente, repositorio, especificacion__version=version)

    assert lectura.motivo.startswith("especificacion.version:")
    assert "comillas" in lectura.motivo


def test_la_version_numerica_del_contrato_tambien_pide_comillas(fuente, repositorio):
    repositorio.archivos[RUTA_FICHA] = ficha(especificacion__version="1.1")
    repositorio.archivos[RUTA_CONTRATO] = contrato(version="1.1")
    lectura = sincronizar(fuente)

    assert not lectura.valida
    assert "info.version del archivo" in lectura.motivo


@pytest.mark.parametrize(
    ("cambios", "inicio"),
    [
        ({"clase": "servicio"}, "clase:"),
        ({"madurez": "Beta"}, "madurez:"),
        ({"ambito": "Salud"}, "ambito:"),
        ({"funcion": QUITAR}, "funcion:"),
        ({"instituciones": []}, "instituciones:"),
        ({"acceso__tipo": "libre"}, "acceso.tipo:"),
        ({"responsable": "SUBDERE"}, "responsable:"),
        ({"especificacion__publicada": "ayer"}, "especificacion.publicada:"),
        ({"ambientes": [{"nombre": "pruebas", "base": "ftp://x", "datos": "reales"}]}, "amb"),
    ],
)
def test_campos_obligatorios_tipos_y_listas_cerradas(fuente, repositorio, cambios, inicio):
    lectura = rechazada(fuente, repositorio, **cambios)
    assert lectura.motivo.startswith(inicio)


def test_un_campo_que_el_estandar_no_define_se_rechaza(fuente, repositorio):
    lectura = rechazada(fuente, repositorio, procedenica={"copia": "exacta"})
    assert "procedenica" in lectura.motivo


# Prueba 14


def test_volver_a_una_version_anterior_identica_la_hace_regir_otra_vez(fuente, repositorio):
    sincronizar(fuente)
    repositorio.archivos[RUTA_FICHA] = ficha(especificacion__version="1.1.0")
    repositorio.archivos[RUTA_CONTRATO] = contrato(version="1.1.0")
    assert sincronizar(fuente).valida
    assert Nodo.objects.get().especificacion_vigente.version == "1.1.0"

    repositorio.archivos[RUTA_FICHA] = ficha()
    repositorio.archivos[RUTA_CONTRATO] = contrato()
    assert sincronizar(fuente).valida

    assert Nodo.objects.get().especificacion_vigente.version == "1.0.0"
    assert Especificacion.objects.count() == 2
    assert sincronizaciones().count() == 3


# Ambientes


def test_los_ambientes_se_proyectan_y_los_que_ya_no_se_declaran_se_borran(fuente, repositorio):
    pruebas = {"nombre": "pruebas", "base": "https://pruebas.ejemplo.cl/api", "datos": "inventados"}
    produccion = {"nombre": "produccion", "base": "https://ejemplo.cl/api", "datos": "reales"}
    repositorio.archivos[RUTA_FICHA] = ficha(ambientes=[pruebas, produccion])
    sincronizar(fuente)
    assert set(Nodo.objects.get().ambientes.values_list("nombre", flat=True)) == {
        "pruebas",
        "produccion",
    }

    repositorio.archivos[RUTA_FICHA] = ficha(ambientes=[produccion])
    assert sincronizar(fuente).valida

    assert list(Nodo.objects.get().ambientes.values_list("nombre", flat=True)) == ["produccion"]


def test_un_ambiente_repetido_se_rechaza(fuente, repositorio):
    pruebas = {"nombre": "pruebas", "base": "https://ejemplo.cl/api", "datos": "inventados"}
    lectura = rechazada(fuente, repositorio, ambientes=[pruebas, pruebas])
    assert "repetido" in lectura.motivo


# Prueba 16


def test_un_run_valido_en_la_ficha_la_rechaza_y_no_se_archiva(fuente, repositorio):
    un_run = run.formatear(12345678, run.digito_verificador(12345678))
    lectura = rechazada(fuente, repositorio, descripcion=f"Contacto: Juan, RUN {un_run}.")

    assert lectura.motivo.startswith("descripcion:")
    assert "RUN" in lectura.motivo
    assert un_run not in lectura.motivo
    assert lectura.contenido == ""


def test_un_run_con_digito_verificador_invalido_no_la_rechaza(fuente, repositorio):
    dv = "0" if run.digito_verificador(12345678) != "0" else "1"
    repositorio.archivos[RUTA_FICHA] = ficha(descripcion=f"Código interno 12345678-{dv}.")
    assert sincronizar(fuente).valida


def test_un_correo_distinto_del_responsable_la_rechaza(fuente, repositorio):
    lectura = rechazada(fuente, repositorio, procedencia__detalle="Escribir a juan@subdere.gov.cl")

    assert lectura.motivo.startswith("procedencia.detalle:")
    assert lectura.contenido == ""


def test_el_correo_del_responsable_puede_repetirse_en_otro_texto(fuente, repositorio):
    repositorio.archivos[RUTA_FICHA] = ficha(
        acceso__detalle="Consultas a equipo.sem@subdere.gov.cl."
    )
    assert sincronizar(fuente).valida


def test_un_correo_de_un_proveedor_publico_como_responsable_la_rechaza(fuente, repositorio):
    lectura = rechazada(fuente, repositorio, responsable__correo="equipo.sem@Gmail.com")

    assert lectura.motivo.startswith("responsable.correo: gmail.com")


def test_el_contrato_no_se_revisa_por_datos_personales(fuente, repositorio):
    un_run = run.formatear(12345678, run.digito_verificador(12345678))
    repositorio.archivos[RUTA_CONTRATO] = contrato(extra=f"x-ejemplo: {un_run}\n")
    assert sincronizar(fuente).valida


# Lectura solo crece


def test_una_lectura_no_se_edita_ni_se_borra(fuente, repositorio):
    lectura = sincronizar(fuente)

    with pytest.raises(RegistroInmutable):
        lectura.save()
    with pytest.raises(RegistroInmutable):
        lectura.delete()
    with pytest.raises(RegistroInmutable):
        Lectura.objects.update(motivo="otro")
