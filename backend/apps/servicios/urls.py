from django.urls import include, path

urlpatterns = [
    path("", include("apps.servicios.api.v1.routers")),
]
