from django.urls import include, path

urlpatterns = [
    path("", include("apps.wiki.api.v1.routers")),
]
