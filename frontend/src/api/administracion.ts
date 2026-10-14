// Las consultas y escrituras de /admin. Cada escritura invalida lo que cambia, incluido el
// catálogo público cuando cambia la visibilidad de un nodo.
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type {
  Fuente,
  Lectura,
  MunicipioResumen,
  Nodo,
  NodoResumen,
  Perfil,
  Rol,
  Visibilidad,
} from "../tipos";
import { pedir } from "./cliente";

export function useFuentes() {
  return useQuery({ queryKey: ["admin", "fuentes"], queryFn: () => pedir<Fuente[]>("/fuentes") });
}

export function useLecturas(id: number, habilitado: boolean) {
  return useQuery({
    queryKey: ["admin", "lecturas", id],
    queryFn: () => pedir<Lectura[]>(`/fuentes/${id}/lecturas`),
    enabled: habilitado,
  });
}

export function useNodosTodos() {
  return useQuery({
    queryKey: ["admin", "nodos"],
    queryFn: () => pedir<NodoResumen[]>("/nodos", { params: { visibilidad: "todas" } }),
  });
}

export type FiltroPerfiles = { rol?: Rol | ""; municipio?: string; activo?: "" | "true" | "false" };

export function usePerfiles(filtro: FiltroPerfiles, habilitado = true) {
  return useQuery({
    queryKey: ["admin", "perfiles", filtro],
    queryFn: () => pedir<Perfil[]>("/perfiles", { params: filtro }),
    enabled: habilitado,
  });
}

export function useMunicipios(habilitado = true) {
  return useQuery({
    queryKey: ["municipios"],
    queryFn: () => pedir<MunicipioResumen[]>("/municipios"),
    staleTime: Infinity,
    enabled: habilitado,
  });
}

/** Invalidar todo lo de /admin es barato: son pocas listas y cortas. */
function useInvalidar() {
  const cliente = useQueryClient();
  return (...claves: unknown[][]) =>
    Promise.all([["admin"], ...claves].map((queryKey) => cliente.invalidateQueries({ queryKey })));
}

export type DatosFuente = { url: string; rama: string; ruta_ficha: string };

export function useRegistrarFuente() {
  const invalidar = useInvalidar();
  return useMutation({
    mutationFn: (datos: DatosFuente) => pedir<Fuente>("/fuentes", { metodo: "POST", cuerpo: datos }),
    onSuccess: () => invalidar(["nodos"]),
  });
}

export function useModificarFuente() {
  const invalidar = useInvalidar();
  return useMutation({
    mutationFn: ({ id, ...cambios }: Partial<DatosFuente> & { id: number; activa?: boolean }) =>
      pedir<Fuente>(`/fuentes/${id}`, { metodo: "PATCH", cuerpo: cambios }),
    onSuccess: () => invalidar(),
  });
}

export function useSincronizar() {
  const invalidar = useInvalidar();
  return useMutation({
    mutationFn: (id: number) => pedir<Lectura>(`/fuentes/${id}/sincronizar`, { metodo: "POST" }),
    onSuccess: () => invalidar(["nodos"], ["nodo"]),
  });
}

export type CambiosNodo = { visibilidad?: Visibilidad; orden?: number; nota_editorial?: string };

export function useEditarNodo() {
  const invalidar = useInvalidar();
  return useMutation({
    mutationFn: ({ identificador, ...cambios }: CambiosNodo & { identificador: string }) =>
      pedir<Nodo>(`/nodos/${encodeURIComponent(identificador)}`, { metodo: "PATCH", cuerpo: cambios }),
    onSuccess: (_, { identificador }) => invalidar(["nodos"], ["nodo", identificador]),
  });
}

export type DatosPerfil = {
  run?: string;
  nombre?: string;
  rol?: Rol;
  municipio?: string | null;
  activo?: boolean;
};

export function useCrearPerfil() {
  const invalidar = useInvalidar();
  return useMutation({
    mutationFn: (datos: DatosPerfil) => pedir<Perfil>("/perfiles", { metodo: "POST", cuerpo: datos }),
    onSuccess: () => invalidar(),
  });
}

export function useModificarPerfil() {
  const invalidar = useInvalidar();
  return useMutation({
    mutationFn: ({ id, ...cambios }: DatosPerfil & { id: number }) =>
      pedir<Perfil>(`/perfiles/${id}`, { metodo: "PATCH", cuerpo: cambios }),
    onSuccess: () => invalidar(),
  });
}

export function useDesignarEncargado() {
  const invalidar = useInvalidar();
  return useMutation({
    mutationFn: ({ cut, perfil }: { cut: string; perfil: number }) =>
      pedir<Perfil>(`/municipios/${cut}/encargado`, { metodo: "PUT", cuerpo: { perfil } }),
    onSuccess: () => invalidar(),
  });
}
