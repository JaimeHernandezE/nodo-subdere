from django.urls import include, path

urlpatterns = [
    path("", include("apps.catalogo.api.v1.routers")),
]
