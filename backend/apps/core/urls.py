from django.urls import include, path

urlpatterns = [
    path("", include("apps.core.api.v1.routers")),
]
