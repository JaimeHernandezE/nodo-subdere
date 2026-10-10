/// <reference types="vitest/config" />
import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, ".", "");
  return {
    base: env.VITE_BASE_PATH || "/",
    plugins: [react()],
    server: {
      host: true,
      port: 5173,
      // En Docker sobre Windows los cambios del volumen no llegan como eventos.
      watch: env.VITE_SONDEAR_CAMBIOS ? { usePolling: true, interval: 300 } : undefined,
    },
    test: {
      environment: "jsdom",
      globals: true,
      setupFiles: ["src/pruebas/preparar.ts"],
      css: false,
    },
  };
});
