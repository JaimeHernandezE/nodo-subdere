import hashlib

import pytest
from django.db import IntegrityError, transaction

from apps.catalogo.errores import CampoDeFicha
from apps.catalogo.models import (
    CAMPOS_DE_FICHA,
    CAMPOS_EDITORIALES,
    Alias,
    Ambiente,
    Ambito,
    Especificacion,
    Nodo,
    Visibilidad,
)
from apps.core.models import ModeloBase

from .conftest import crear_nodo, especificar

pytestmark = pytest.mark.django_db


class TestCamposDeFicha:
    def test_cambiar_el_identificador_falla_incluso_desde_la_sincronizacion(self):
        nodo = crear_nodo()
        nodo.identificador = "otro"

        with pytest.raises(CampoDeFicha):
            nodo.save(desde_sincronizacion=True)

    def test_save_sin_sincronizacion_no_escribe_un_campo_de_ficha(self):
        nodo = crear_nodo()
        nodo.funcion = "Escrita a mano"

        with pytest.raises(CampoDeFicha) as error:
            nodo.save()
        assert error.value.detalles == [
            {"campo": "funcion", "mensaje": "Viene de la ficha del servicio."}
        ]

    def test_la_sincronizacion_si_escribe_un_campo_de_ficha(self):
        nodo = crear_nodo()
        nodo.funcion = "Leída de una ficha nueva"
        nodo.save(desde_sincronizacion=True)

        assert Nodo.objects.get(pk=nodo.pk).funcion == "Leída de una ficha nueva"

    def test_save_sin_sincronizacion_si_escribe_los_editoriales(self):
        nodo = crear_nodo()
        nodo.orden, nodo.nota_editorial = 3, "Demostración con datos inventados."
        nodo.save()

        assert Nodo.objects.get(pk=nodo.pk).orden == 3

    @pytest.mark.parametrize("campo", ["funcion", "ambito", "ambito_id", "leido_en"])
    def test_update_no_escribe_campos_de_ficha(self, campo):
        nodo = crear_nodo()
        sgm = Ambito.objects.get(nombre="SGM")
        valor = {"ambito": sgm, "ambito_id": sgm.pk}.get(campo, "x")

        with pytest.raises(CampoDeFicha):
            Nodo.objects.filter(pk=nodo.pk).update(**{campo: valor})

    def test_update_si_escribe_los_editoriales(self):
        nodo = crear_nodo()

        Nodo.objects.filter(pk=nodo.pk).update(orden=5)

        assert Nodo.objects.get(pk=nodo.pk).orden == 5

    def test_bulk_update_no_escribe_campos_de_ficha(self):
        nodo = crear_nodo()
        nodo.funcion = "x"

        with pytest.raises(CampoDeFicha):
            Nodo.objects.bulk_update([nodo], ["funcion"])

    def test_un_nodo_no_se_crea_a_mano(self):
        with pytest.raises(CampoDeFicha):
            Nodo.objects.create(identificador="nuevo", nombre="A mano")
        with pytest.raises(CampoDeFicha):
            Nodo.objects.bulk_create([Nodo(identificador="nuevo")])

    def test_la_constante_cubre_todos_los_campos_salvo_editoriales_y_de_modelo_base(self):
        """Un campo de ficha nuevo que no se agregue a la constante quedaría editable a mano."""
        propios = {campo.name for campo in Nodo._meta.concrete_fields}
        comunes = {campo.name for campo in ModeloBase._meta.fields} | {"id"}

        assert set(CAMPOS_DE_FICHA) == propios - comunes - set(CAMPOS_EDITORIALES)


class TestProtegidosEnteros:
    @pytest.fixture
    def nodo(self):
        return crear_nodo()

    def test_especificacion_no_se_crea_modifica_ni_borra_a_mano(self, nodo):
        with pytest.raises(CampoDeFicha):
            Especificacion.objects.create(nodo=nodo, version="1.0.0", formato="descripcion")

        especificacion = especificar(nodo)
        especificacion.publicada = None
        with pytest.raises(CampoDeFicha):
            especificacion.save()
        with pytest.raises(CampoDeFicha):
            especificacion.delete()

    def test_ambiente_no_se_crea_modifica_ni_borra_a_mano(self, nodo):
        datos = {"nodo": nodo, "nombre": "pruebas", "base": "https://x.cl/api", "datos": "reales"}
        with pytest.raises(CampoDeFicha):
            Ambiente.objects.create(**datos)

        ambiente = Ambiente(**datos)
        ambiente.save(desde_sincronizacion=True)
        ambiente.datos = "inventados"
        with pytest.raises(CampoDeFicha):
            ambiente.save()
        with pytest.raises(CampoDeFicha):
            ambiente.delete()
        ambiente.delete(desde_sincronizacion=True)

    @pytest.mark.parametrize("modelo", [Especificacion, Ambiente])
    def test_su_queryset_no_escribe(self, nodo, modelo):
        especificar(nodo)
        consulta = modelo.objects.all()

        with pytest.raises(CampoDeFicha):
            consulta.update(commit="x")
        with pytest.raises(CampoDeFicha):
            consulta.delete()
        with pytest.raises(CampoDeFicha):
            consulta.bulk_update(list(consulta), ["commit"])
        with pytest.raises(CampoDeFicha):
            modelo.objects.bulk_create([modelo(nodo=nodo)])


class TestEspecificacion:
    def test_solo_una_vigente_por_nodo(self):
        nodo = crear_nodo()
        especificar(nodo, version="1.0.0")

        with pytest.raises(IntegrityError), transaction.atomic():
            especificar(nodo, version="1.1.0")

    def test_la_version_es_unica_por_nodo(self):
        nodo = crear_nodo()
        especificar(nodo, version="1.0.0")

        with pytest.raises(IntegrityError), transaction.atomic():
            especificar(nodo, version="1.0.0", vigente=False)

    def test_la_huella_es_el_sha256_del_contenido(self):
        especificacion = especificar(crear_nodo(), contenido="openapi: 3.0.3\n")

        assert especificacion.huella == hashlib.sha256(b"openapi: 3.0.3\n").hexdigest()

    def test_una_version_registrada_no_cambia_de_contenido_ni_desde_la_sincronizacion(self):
        especificacion = especificar(crear_nodo())
        especificacion.contenido += "# corregido\n"

        with pytest.raises(CampoDeFicha):
            especificacion.save(desde_sincronizacion=True)

    def test_la_sincronizacion_si_cambia_cual_rige(self):
        nodo = crear_nodo()
        anterior = especificar(nodo, version="1.0.0")
        anterior.vigente = False
        anterior.save(desde_sincronizacion=True)
        especificar(nodo, version="1.1.0")

        assert nodo.especificacion_vigente.version == "1.1.0"


class TestVisibilidad:
    def test_no_se_publica_sin_especificacion_vigente(self):
        nodo = crear_nodo(visibilidad=Visibilidad.OCULTO)

        assert nodo.impedimento_para(Visibilidad.PUBLICADO)
        especificar(nodo)
        assert nodo.impedimento_para(Visibilidad.PUBLICADO) == ""

    def test_de_retirado_solo_se_pasa_a_oculto(self):
        nodo = crear_nodo(visibilidad=Visibilidad.RETIRADO)
        especificar(nodo)

        assert nodo.impedimento_para(Visibilidad.PUBLICADO)
        assert nodo.impedimento_para(Visibilidad.OCULTO) == ""


def test_la_migracion_carga_los_ambitos_y_el_alias_de_cut():
    assert list(Ambito.objects.values_list("nombre", flat=True)) == ["SGM", "Transversal"]
    assert Alias.objects.get(identificador="division-territorial").destino == "cut"
