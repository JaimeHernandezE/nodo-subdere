from django.urls import include, path

urlpatterns = [
    path("", include("apps.registro.api.v1.routers")),
]
