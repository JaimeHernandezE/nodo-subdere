// La sesión: un token en memoria y el perfil que devuelve `GET /yo`.
// La interfaz se arma con `yo`, nunca con los reclamos del token.
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { esError, fijarToken, pedir } from "../api/cliente";
import type { Yo } from "../tipos";
import { gestorOidc, hayKeycloak, salirDeKeycloak } from "./oidc";

type Sesion = {
  token: string | null;
  yo: Yo | null;
  cargando: boolean;
  sinPerfil: boolean;
  entrar: (token: string) => Promise<Yo>;
  salir: () => void;
};

const Contexto = createContext<Sesion | null>(null);

export function ProveedorDeSesion({ children }: { children: ReactNode }) {
  const cliente = useQueryClient();
  const [token, setToken] = useState<string | null>(null);

  const consulta = useQuery({
    queryKey: ["yo", token],
    queryFn: () => pedir<Yo>("/yo"),
    enabled: token !== null,
    retry: false,
  });

  const entrar = useCallback(
    async (nuevo: string) => {
      fijarToken(nuevo);
      setToken(nuevo);
      const yo = await cliente.fetchQuery({
        queryKey: ["yo", nuevo],
        queryFn: () => pedir<Yo>("/yo"),
        retry: false,
      });
      await cliente.resetQueries({ predicate: (q) => q.queryKey[0] !== "yo" });
      return yo;
    },
    [cliente],
  );

  const cerrar = useCallback(() => {
    fijarToken(null);
    setToken(null);
    cliente.clear();
  }, [cliente]);

  const salir = useCallback(() => {
    cerrar();
    if (hayKeycloak()) void salirDeKeycloak();
  }, [cerrar]);

  // El refresco silencioso trae otro token para la misma persona: cambia la cabecera, no la
  // sesión, y `yo` no se vuelve a pedir. Si no se pudo refrescar, la sesión termina.
  useEffect(() => {
    if (!hayKeycloak()) return;
    const eventos = gestorOidc().events;
    const renovado = eventos.addUserLoaded((usuario) => fijarToken(usuario.access_token));
    const vencido = eventos.addAccessTokenExpired(cerrar);
    const fallido = eventos.addSilentRenewError(cerrar);
    return () => {
      renovado();
      vencido();
      fallido();
    };
  }, [cerrar]);

  const valor = useMemo<Sesion>(
    () => ({
      token,
      yo: token ? (consulta.data ?? null) : null,
      cargando: token !== null && consulta.isPending,
      sinPerfil: token !== null && esError(consulta.error, "SIN_PERFIL"),
      entrar,
      salir,
    }),
    [token, consulta.data, consulta.isPending, consulta.error, entrar, salir],
  );

  return <Contexto.Provider value={valor}>{children}</Contexto.Provider>;
}

export function useSesion(): Sesion {
  const sesion = useContext(Contexto);
  if (!sesion) throw new Error("useSesion fuera de ProveedorDeSesion");
  return sesion;
}

export const ROLES: Record<Yo["rol"], string> = {
  lector: "Lector",
  editor: "Editor",
  curador: "Curador",
  administrador: "Administrador",
};
