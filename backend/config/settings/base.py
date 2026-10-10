from pathlib import Path

import environ
from corsheaders.defaults import default_headers

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()

# Fuera de contenedores, Django lee el archivo del ambiente. Dentro, las variables ya
# vienen de `env_file` en compose, y read_env no sobrescribe las que existen.
_archivo_env = BASE_DIR / env.str("ARCHIVO_ENV", default=".env.local")
if _archivo_env.is_file():
    environ.Env.read_env(_archivo_env)

SECRET_KEY = env.str("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

NODO_OCULTO = env.bool("NODO_OCULTO", default=True)
VERSION_DESPLIEGUE = env.str("VERSION_DESPLIEGUE", default="desarrollo")

# Adaptadores a las fuentes externas. Ver apps/integraciones/INSTRUCCIONES.md.
CUT_API_URL = env.str("CUT_API_URL", default="")
CUT_CACHE_SEGUNDOS = env.int("CUT_CACHE_SEGUNDOS", default=3600)
PERMISOS_CIRCULACION_API_URL = env.str("PERMISOS_CIRCULACION_API_URL", default="")
PERMISOS_CIRCULACION_CACHE_SEGUNDOS = env.int("PERMISOS_CIRCULACION_CACHE_SEGUNDOS", default=300)
INTEGRACIONES_TIEMPO_ESPERA_SEGUNDOS = env.int("INTEGRACIONES_TIEMPO_ESPERA_SEGUNDOS", default=5)

# Uno por proceso. Con varias instancias, Redis acá; los adaptadores no cambian.
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# Identidad: realm de Keycloak que federa Clave Única. Ver apps/cuentas/INSTRUCCIONES.md §2.
KEYCLOAK_ISSUER = env.str("KEYCLOAK_ISSUER", default="")
KEYCLOAK_AUDIENCE = env.str("KEYCLOAK_AUDIENCE", default="")
KEYCLOAK_JWKS_URL = env.str("KEYCLOAK_JWKS_URL", default="")
KEYCLOAK_JWKS_CACHE_SEGUNDOS = env.int("KEYCLOAK_JWKS_CACHE_SEGUNDOS", default=3600)
# Lectura de los repositorios de servicio. Ver apps/registro/INSTRUCCIONES.md §2.
REGISTRO_GIT_API_URL = env.str("REGISTRO_GIT_API_URL", default="")
REGISTRO_GIT_TOKEN = env.str("REGISTRO_GIT_TOKEN", default="")
REGISTRO_TIEMPO_ESPERA_SEGUNDOS = env.int("REGISTRO_TIEMPO_ESPERA_SEGUNDOS", default=10)
REGISTRO_DOMINIOS_NO_INSTITUCIONALES = env.list(
    "REGISTRO_DOMINIOS_NO_INSTITUCIONALES",
    default=[
        "gmail.com",
        "googlemail.com",
        "hotmail.com",
        "hotmail.cl",
        "outlook.com",
        "outlook.cl",
        "live.com",
        "live.cl",
        "yahoo.com",
        "yahoo.es",
        "icloud.com",
        "me.com",
        "proton.me",
        "protonmail.com",
        "aol.com",
        "gmx.com",
    ],
)

# Solo local.py lo activa; prod.py no arranca si la variable existe.
CUENTAS_EMISOR_LOCAL = False
CUENTAS_CLAVE_LOCAL = BASE_DIR / ".local" / "emisor_local.pem"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "apps.core",
    "apps.cuentas",
    "apps.catalogo",
    "apps.registro",
    "apps.integraciones",
    "apps.servicios",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "apps.core.middleware.RobotsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.core.middleware.ContextoMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {"default": env.db("DATABASE_URL")}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_HEADERS = (*default_headers, "x-procedimiento", "x-id-tramite")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["apps.cuentas.autenticacion.AutenticacionRealm"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "UNAUTHENTICATED_USER": None,
    "EXCEPTION_HANDLER": "apps.core.errores.manejador_de_excepciones",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "API del Nodo SUBDERE",
    "DESCRIPTION": "Catálogo de intercambios del dominio municipal, servicios y wiki.",
    "VERSION": VERSION_DESPLIEGUE,
    "SERVE_INCLUDE_SCHEMA": False,
    # Swagger se sirve desde el propio backend: la producción oculta puede no tener
    # salida a internet, y el CDN por defecto apunta a una versión sin fijar.
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"consola": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["consola"], "level": "INFO"},
}
