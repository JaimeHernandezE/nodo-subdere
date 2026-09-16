# Plataforma de Control — producción

Diagrama de referencia de la **Plataforma Institucional de Gestión de APIs** (Plataforma de Control) con separación de zonas de red. Vista de producción.

Base técnica: [`plataforma-control.md`](plataforma-control.md). Vista de demo en un servidor: [`flujo_1.md`](flujo_1.md).

Los nombres de producto (API7, Keycloak, LogTank) son arquitectura de referencia, no vinculante. Las rutas `/patentes`, `/gastos` y `/contabilidad` son marcadores: en el catálogo equivalen a las fichas publicadas; las primeras de SGM son `/plataforma` (core) y `/adquisiciones`.

```mermaid
flowchart LR

    subgraph EXTERNO["Red externa / Municipalidad"]
        CLIENTE["Aplicación municipal<br/>Cliente OAuth"]
        ADMIN["Administrador técnico"]
    end

    INTERNET(("Internet o red de pruebas"))

    subgraph PERIMETRO["Perímetro institucional"]
        FW["Firewall<br/>NAT y reglas de acceso"]
    end

    subgraph DMZ["DMZ / Red de API Management"]
        API7["API7 Gateway<br/>HTTPS 443"]
        API7_ADMIN["Consola API7<br/>Acceso restringido"]
        KEYCLOAK["Keycloak<br/>OAuth 2.0 / OIDC"]
    end

    subgraph RED_INTERNA["Red interna"]
        API_PAT["API Patentes"]
        API_GAS["API Gastos"]
        API_CONT["API Contabilidad"]
        KC_DB[("PostgreSQL<br/>Keycloak")]
    end

    subgraph MONITOREO["Monitoreo"]
        LOGS["LogTank / Logs centralizados"]
    end

    CLIENTE --> INTERNET
    ADMIN --> INTERNET
    INTERNET --> FW

    FW -->|"HTTPS 443<br/>Consumo de API"| API7
    FW -->|"HTTPS 443<br/>Solicitud de token"| KEYCLOAK
    FW -->|"HTTPS 443<br/>Solo IP/VPN administrativa"| API7_ADMIN

    API7_ADMIN --> API7

    KEYCLOAK -->|"TCP 5432"| KC_DB

    API7 -->|"HTTPS<br/>Ruta /patentes"| API_PAT
    API7 -->|"HTTPS<br/>Ruta /gastos"| API_GAS
    API7 -->|"HTTPS<br/>Ruta /contabilidad"| API_CONT

    API7 --> LOGS
    KEYCLOAK --> LOGS

    DESC["Descripción:
    1. Aplicación municipal → Keycloak
    Solicita token OAuth mediante HTTPS.

    2. Keycloak → Aplicación municipal
    Entrega un access token JWT.

    3. Aplicación municipal → API7
    Invoca la API usando el JWT.

    4. API7
    Valida el token, permisos y límites.

    5. API7 → API interna
    Reenvía la solicitud al sistema correspondiente.

    6. API interna → API7 → Aplicación municipal
    Devuelve la respuesta
    ."]
