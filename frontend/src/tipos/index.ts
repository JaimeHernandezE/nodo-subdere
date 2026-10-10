// Nombres cortos para los esquemas del backend. `api.ts` se genera con `npm run tipos`
// desde `esquema.yaml`; no se edita a mano.
import type { components } from "./api";

type Esquemas = components["schemas"];

export type Yo = Esquemas["Yo"];
export type Ambito = Esquemas["Ambito"];
export type NodoResumen = Esquemas["NodoResumen"];
export type Nodo = Esquemas["Nodo"];
export type Especificacion = Esquemas["Especificacion"];
export type Servicio = Esquemas["Servicio"];
export type EstadoServicio = Esquemas["EstadoEnum"];
export type Origen = Esquemas["OrigenEnum"];
export type UnidadTerritorial = Esquemas["UnidadTerritorial"];
export type CutBusqueda = Esquemas["CutBusqueda"];
export type CutUnidad = Esquemas["CutUnidad"];
export type PermisosRespuesta = Esquemas["PermisosRespuesta"];
export type Permiso = Esquemas["Permiso"];
export type PermisoProvisional = Esquemas["PermisoProvisional"];
export type EntradaResumen = Esquemas["EntradaResumen"];
export type Entrada = Esquemas["Entrada"];
export type Seccion = Esquemas["SeccionEnum"];
