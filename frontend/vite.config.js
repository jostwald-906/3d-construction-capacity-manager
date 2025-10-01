import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: { port: 5173 },
  define: { __BACKEND_URL__: JSON.stringify(process.env.VITE_BACKEND_URL || "http://localhost:8000") }
});
