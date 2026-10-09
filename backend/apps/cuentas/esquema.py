from drf_spectacular.extensions import OpenApiAuthenticationExtension


class AutenticacionRealmEsquema(OpenApiAuthenticationExtension):
    target_class = "apps.cuentas.autenticacion.AutenticacionRealm"
    name = "realm"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Access token del realm de Keycloak que federa Clave Única.",
        }
