// Una función por consulta del backend, para que las claves del caché no se repitan a mano.
import { useQuery } from "@tanstack/react-query";

import type {
  Ambito,
  CutBusqueda,
  CutUnidad,
  Entrada,
  EntradaResumen,
  Nodo,
  NodoResumen,
  Servicio,
} from "../tipos";
import { pedir } from "./cliente";

export function useAmbitos() {
  return useQuery({ queryKey: ["ambitos"], queryFn: () => pedir<Ambito[]>("/ambitos") });
}

export function useNodos() {
  return useQuery({ queryKey: ["nodos"], queryFn: () => pedir<NodoResumen[]>("/nodos") });
}

export function useNodo(identificador: string | undefined) {
  return useQuery({
    queryKey: ["nodo", identificador],
    queryFn: () => pedir<Nodo>(`/nodos/${encodeURIComponent(identificador ?? "")}`),
    enabled: !!identificador,
  });
}

export function useArchivoDeEspecificacion(identificador: string, habilitado: boolean) {
  return useQuery({
    queryKey: ["especificacion", identificador],
    queryFn: () =>
      pedir<string>(`/nodos/${encodeURIComponent(identificador)}/especificacion/archivo`, {
        texto: true,
      }),
    enabled: habilitado,
  });
}

export function useServicios(nodo?: string) {
  return useQuery({
    queryKey: ["servicios", nodo ?? null],
    queryFn: () => pedir<Servicio[]>("/servicios", { params: { nodo } }),
  });
}

export function useServicio(slug: string | undefined) {
  return useQuery({
    queryKey: ["servicio", slug],
    queryFn: () => pedir<Servicio>(`/servicios/${encodeURIComponent(slug ?? "")}`),
    enabled: !!slug,
  });
}

export function useEntradas(nodo?: string) {
  return useQuery({
    queryKey: ["wiki", nodo ?? null],
    queryFn: () => pedir<EntradaResumen[]>("/wiki", { params: { nodo } }),
  });
}

export function useEntrada(slug: string) {
  return useQuery({
    queryKey: ["wiki-entrada", slug],
    queryFn: () => pedir<Entrada>(`/wiki/${encodeURIComponent(slug)}`),
  });
}

export function buscarCut(texto: string, signal?: AbortSignal) {
  if (/^\d+$/.test(texto)) {
    return pedir<CutUnidad>(`/servicios/cut/codigo/${texto}`, { signal }).then(
      (r): CutBusqueda => ({ ...r, datos: [r.datos] }),
    );
  }
  return pedir<CutBusqueda>("/servicios/cut/buscar", { params: { q: texto }, signal });
}
