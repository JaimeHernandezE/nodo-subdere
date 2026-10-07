def test_swagger_se_sirve_sin_depender_de_un_cdn(client):
    respuesta = client.get("/api/v1/schema/swagger-ui/")
    html = respuesta.content.decode()

    assert respuesta.status_code == 200
    assert "cdn.jsdelivr.net" not in html
    assert "/static/drf_spectacular_sidecar/swagger-ui-dist/swagger-ui-bundle.js" in html


def test_el_esquema_openapi_es_publico_y_describe_salud(client):
    respuesta = client.get("/api/v1/schema/", {"format": "json"})

    assert respuesta.status_code == 200
    assert "/api/v1/salud" in respuesta.json()["paths"]
