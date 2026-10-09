from django.urls import include, path

urlpatterns = [
    path("", include("apps.cuentas.api.v1.routers")),
]
