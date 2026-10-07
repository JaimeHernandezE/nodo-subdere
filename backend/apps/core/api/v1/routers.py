from django.urls import path

from .salud_view import SaludView

urlpatterns = [
    path("salud", SaludView.as_view(), name="salud"),
]
