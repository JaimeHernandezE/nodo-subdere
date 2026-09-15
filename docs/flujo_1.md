# Plataforma de Control — demo

Diagrama de referencia de la **Plataforma Institucional de Gestión de APIs** (Plataforma de Control) en un solo servidor (Docker o Kubernetes). Vista mínima para prueba de concepto.

Base técnica: [`plataforma-control.md`](plataforma-control.md). Vista de producción con zonas de red: [`flujo_2.md`](flujo_2.md).

Los nombres de producto (API7, Keycloak) son arquitectura de referencia, no vinculante.

```mermaid
flowchart LR

    CLIENTE["Aplicación municipal"]

    FW["Firewall / NAT"]

    subgraph SERVIDOR["Servidor demo Docker o Kubernetes"]
        API7["API7 Gateway<br/>api-demo.institucion.cl"]
        KEYCLOAK["Keycloak<br/>auth-demo.institucion.cl"]
        POSTGRES[("PostgreSQL")]
    end

    API["API interna 1 SEM
    API interna 2 SIM
    (solo ejemplo)
    
    "]

    CLIENTE -->|"1. Solicita token HTTPS"| FW
    FW --> KEYCLOAK

    KEYCLOAK -->|"2. Lee clientes y permisos"| POSTGRES
    KEYCLOAK -->|"3. Entrega JWT"| CLIENTE

    CLIENTE -->|"4. Invoca API con JWT"| FW
    FW --> API7

    API7 -->|"5. Valida JWT y enruta"| API
    API -->|"6. Respuesta"| API7
    API7 --> CLIENTE


    DESC["Descripción:
1. Se obtiene el token en Keycloak.
2. API7 valida JWT.
3. Se enruta la petición.
4. La API responde."]
