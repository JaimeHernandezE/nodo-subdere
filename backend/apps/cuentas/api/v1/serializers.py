from django.db import IntegrityError
from rest_framework import exceptions, serializers

from apps.core import run
from apps.core.models import Municipio
from apps.cuentas.errores import PerfilExistente
from apps.cuentas.models import Perfil, Rol
from apps.cuentas.permisos import puede_ver_run


def instantanea(perfil: Perfil) -> dict:
    """Lo que queda en la bitácora como antes y después de un cambio."""
    return {
        "run": perfil.run,
        "nombre": perfil.nombre,
        "rol": perfil.rol,
        "municipio": perfil.municipio.cut if perfil.municipio else None,
        "es_encargado": perfil.es_encargado,
        "activo": perfil.activo,
    }


class MunicipioResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipio
        fields = ["cut", "nombre"]


class YoSerializer(serializers.ModelSerializer):
    municipio = MunicipioResumenSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Perfil
        fields = ["id", "nombre", "rol", "municipio", "es_encargado"]
        read_only_fields = fields


class PerfilSerializer(serializers.ModelSerializer):
    run = serializers.CharField(
        help_text="Con o sin puntos y guion. No se cambia después de crear."
    )
    municipio = serializers.SlugRelatedField(
        slug_field="cut",
        queryset=Municipio.objects.all(),
        allow_null=True,
        required=False,
        help_text="Código CUT de la comuna. Vacío: persona de SUBDERE.",
    )

    class Meta:
        model = Perfil
        fields = [
            "id",
            "run",
            "nombre",
            "rol",
            "municipio",
            "es_encargado",
            "activo",
            "creado_en",
            "actualizado_en",
        ]
        read_only_fields = ["id", "es_encargado", "creado_en", "actualizado_en"]
        # DRF deduce validadores de las restricciones únicas del modelo y, por la del
        # encargado, volvería obligatorio `municipio`. La unicidad del RUN la revisa
        # `create`, y la del encargado no se escribe por acá.
        validators = []

    def get_fields(self):
        campos = super().get_fields()
        if isinstance(self.instance, Perfil):
            campos["run"].read_only = True
        return campos

    def validate_run(self, valor):
        try:
            return run.leer(valor)
        except ValueError as error:
            raise serializers.ValidationError("El RUN no es válido.") from error

    def validate(self, datos):
        actor = self.context["request"].user
        if actor.es_administrador:
            return datos

        if self.instance is None:
            if datos.get("municipio", actor.municipio) != actor.municipio:
                raise exceptions.PermissionDenied()
            if datos.get("rol", Rol.LECTOR) != Rol.LECTOR:
                raise exceptions.PermissionDenied()
            datos["municipio"] = actor.municipio
            datos["rol"] = Rol.LECTOR
        else:
            if "municipio" in datos and datos["municipio"] != self.instance.municipio:
                raise exceptions.PermissionDenied()
            if "rol" in datos and datos["rol"] != self.instance.rol:
                raise exceptions.PermissionDenied()
        return datos

    def create(self, datos):
        numero, dv = datos.pop("run")
        if Perfil.objects.filter(run_tipo="RUN", run_numero=numero).exists():
            raise PerfilExistente()
        try:
            return Perfil.objects.create(run_numero=numero, run_dv=dv, **datos)
        except IntegrityError as error:
            raise PerfilExistente() from error

    def update(self, instancia, datos):
        if "municipio" in datos and datos["municipio"] != instancia.municipio:
            instancia.es_encargado = False
        return super().update(instancia, datos)


class IntegranteSerializer(serializers.ModelSerializer):
    run = serializers.CharField(read_only=True)

    class Meta:
        model = Perfil
        fields = ["id", "run", "nombre", "rol", "es_encargado", "activo"]
        read_only_fields = fields

    def to_representation(self, perfil):
        datos = super().to_representation(perfil)
        if not puede_ver_run(self.context["request"].user, perfil.municipio_id):
            datos.pop("run")
        return datos


class DesignarEncargadoSerializer(serializers.Serializer):
    perfil = serializers.IntegerField(help_text="Perfil activo de este municipio.")
