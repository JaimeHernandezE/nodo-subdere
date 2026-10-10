import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router";

import { crearClienteDeConsultas, Proveedores, RutasDelSitio } from "./app/App";
import "./estilos/maqueta.css";
import "./estilos/sitio.css";

const base = (import.meta.env.VITE_BASE_PATH ?? "/").replace(/\/+$/, "") || "/";

createRoot(document.getElementById("raiz")!).render(
  <StrictMode>
    <BrowserRouter basename={base}>
      <Proveedores cliente={crearClienteDeConsultas()}>
        <RutasDelSitio />
      </Proveedores>
    </BrowserRouter>
  </StrictMode>,
);
