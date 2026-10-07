import pytest

from apps.core.models import Municipio

pytestmark = pytest.mark.django_db


def test_la_migracion_carga_las_346_comunas_en_forma_canonica():
    cuts = list(Municipio.objects.values_list("cut", flat=True))

    assert len(cuts) == 346
    assert len(set(cuts)) == 346
    assert all(len(cut) == 5 and cut.isdigit() for cut in cuts)


def test_los_codigos_de_una_cifra_de_region_quedan_con_cero():
    iquique = Municipio.objects.get(cut="01101")

    assert iquique.nombre == "Iquique"
    assert iquique.region == "01"
    assert iquique.provincia == "011"


def test_la_jerarquia_se_deduce_del_codigo():
    assert Municipio.objects.filter(cut__startswith="13").count() == 52
    assert Municipio.objects.get(cut="16101").nombre == "Chillán"
