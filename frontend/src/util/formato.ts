import { useEffect } from "react";

const MESES = [
  "enero", "febrero", "marzo", "abril", "mayo", "junio",
  "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
];

/** «9 de octubre de 2026». Una fecha sola (AAAA-MM-DD) se parte a mano: como `Date` es UTC
 * y en Chile retrocede un día. Una fecha con hora se lee en la hora local. */
export function fechaLarga(iso: string | null | undefined): string {
  if (!iso) return "";
  const soloFecha = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
  if (soloFecha) {
    const [, anio, mes, dia] = soloFecha;
    return `${Number(dia)} de ${MESES[Number(mes) - 1]} de ${anio}`;
  }
  const fecha = new Date(iso);
  if (Number.isNaN(fecha.getTime())) return "";
  return `${fecha.getDate()} de ${MESES[fecha.getMonth()]} de ${fecha.getFullYear()}`;
}

export function fechaHora(iso: string | null | undefined): string {
  if (!iso) return "";
  const fecha = new Date(iso);
  if (Number.isNaN(fecha.getTime())) return "";
  return fecha.toLocaleString("es-CL", { dateStyle: "medium", timeStyle: "short" });
}

export function pesos(monto: number): string {
  return `$${String(monto).replace(/\B(?=(\d{3})+(?!\d))/g, ".")}`;
}

export function sinTildes(texto: string): string {
  return texto.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

/** El mismo slug que la maqueta y que el backend: sin tildes, en minúsculas y con guiones. */
export function slug(texto: string): string {
  return sinTildes(texto).replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

export function useTitulo(titulo?: string) {
  useEffect(() => {
    document.title = titulo ? `${titulo} · Nodo SUBDERE` : "Nodo SUBDERE";
  }, [titulo]);
}

/** Cuando el contenido llega después de cargar la página, el navegador no alcanza a saltar al
 * ancla solo. Se llama cuando lo que contiene el ancla ya está pintado. */
export function useIrAlAncla(hash: string, listo: boolean) {
  useEffect(() => {
    if (!listo || !hash) return;
    const destino = document.getElementById(decodeURIComponent(hash.slice(1)));
    destino?.scrollIntoView?.();
  }, [hash, listo]);
}
