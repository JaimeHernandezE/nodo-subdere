FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# "[dev]" en local para tener pytest y ruff; vacío en producción.
ARG EXTRAS=""

COPY . .
RUN pip install -e ".${EXTRAS}"

# Valores de relleno: collectstatic carga la configuración, pero no usa la base ni la clave.
RUN DJANGO_SETTINGS_MODULE=config.settings.prod \
    SECRET_KEY=solo-para-collectstatic \
    DATABASE_URL=postgres://x:x@localhost:5432/x \
    ALLOWED_HOSTS=localhost \
    CSRF_TRUSTED_ORIGINS=https://localhost \
    python manage.py collectstatic --noinput

# Fuera de /app para que el volumen de desarrollo no lo reemplace por una copia con CRLF de Windows.
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN sed -i 's/\r$//' /usr/local/bin/entrypoint.sh && chmod +x /usr/local/bin/entrypoint.sh

RUN useradd --create-home --uid 1000 nodo
USER nodo

EXPOSE 8000
ENTRYPOINT ["entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-"]
