def test_salud_responde_sin_token(client, settings):
    settings.VERSION_DESPLIEGUE = "v-prueba"

    respuesta = client.get("/api/v1/salud")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok", "version": "v-prueba"}


def test_salud_ignora_un_token_cualquiera(client):
    respuesta = client.get("/api/v1/salud", HTTP_AUTHORIZATION="Bearer inventado")

    assert respuesta.status_code == 200
