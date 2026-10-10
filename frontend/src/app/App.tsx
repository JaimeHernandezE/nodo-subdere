import { MutationCache, QueryCache, QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect, type ReactNode } from "react";
import { Outlet, Route, Routes, useLocation, useNavigate } from "react-router";

import { ErrorApi, esError } from "../api/cliente";
import { Apis } from "../paginas/Apis";
import { Entrar } from "../paginas/Entrar";
import { Ficha } from "../paginas/Ficha";
import { NoEncontrada } from "../paginas/NoEncontrada";
import { Participar } from "../paginas/Participar";
import { Portada } from "../paginas/Portada";
import { QueEs } from "../paginas/QueEs";
import { Servicio } from "../paginas/Servicio";
import { Servicios } from "../paginas/Servicios";
import { SinPerfil } from "../paginas/SinPerfil";
import { WikiEntrada, WikiPortada } from "../paginas/Wiki";
import { ProveedorDeSesion } from "../sesion/Sesion";
import { Barra } from "./Barra";
import { Pie } from "./Pie";

const SIN_PERFIL = "nodo:sin-perfil";

function avisarSinPerfil(error: unknown) {
  if (esError(error, "SIN_PERFIL")) window.dispatchEvent(new Event(SIN_PERFIL));
}

export function crearClienteDeConsultas() {
  return new QueryClient({
    queryCache: new QueryCache({ onError: avisarSinPerfil }),
    mutationCache: new MutationCache({ onError: avisarSinPerfil }),
    defaultOptions: {
      queries: {
        staleTime: 60_000,
        refetchOnWindowFocus: false,
        // Un 4xx es una respuesta, no una falla de red: no se reintenta.
        retry: (intentos, error) =>
          !(error instanceof ErrorApi && error.status >= 400 && error.status < 500) && intentos < 2,
      },
    },
  });
}

/** Un 403 SIN_PERFIL, venga de la consulta que venga, lleva a su propia pantalla. */
function VigiaSinPerfil() {
  const navegar = useNavigate();
  useEffect(() => {
    const ir = () => navegar("/sin-perfil");
    window.addEventListener(SIN_PERFIL, ir);
    return () => window.removeEventListener(SIN_PERFIL, ir);
  }, [navegar]);
  return null;
}

/** Al cambiar de página se parte desde arriba; un ancla la resuelve la página cuando ya pintó. */
function SubirAlCambiar() {
  const { pathname, hash } = useLocation();
  useEffect(() => {
    if (!hash) window.scrollTo?.(0, 0);
  }, [pathname]);
  return null;
}

function Marco() {
  return (
    <>
      <SubirAlCambiar />
      <VigiaSinPerfil />
      <Barra />
      <Outlet />
      <Pie />
    </>
  );
}

export function RutasDelSitio() {
  return (
    <Routes>
      <Route element={<Marco />}>
        <Route index element={<Portada />} />
        <Route path="que-es" element={<QueEs />} />
        <Route path="apis" element={<Apis />} />
        <Route path="apis/:id" element={<Ficha />} />
        <Route path="servicios" element={<Servicios />} />
        <Route path="servicios/:slug" element={<Servicio />} />
        <Route path="wiki" element={<WikiPortada />} />
        <Route path="wiki/:slug" element={<WikiEntrada />} />
        <Route path="participar" element={<Participar />} />
        <Route path="entrar" element={<Entrar />} />
        <Route path="sin-perfil" element={<SinPerfil />} />
        <Route path="*" element={<NoEncontrada />} />
      </Route>
    </Routes>
  );
}

export function Proveedores({ cliente, children }: { cliente: QueryClient; children: ReactNode }) {
  return (
    <QueryClientProvider client={cliente}>
      <ProveedorDeSesion>{children}</ProveedorDeSesion>
    </QueryClientProvider>
  );
}
