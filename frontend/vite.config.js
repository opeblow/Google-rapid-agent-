import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  // Default base matches the GitHub Pages project path. Override with VITE_BASE
  // at build time — e.g. set VITE_BASE=/ on Vercel (served at the domain root).
  base: process.env.VITE_BASE || '/Google-rapid-agent-/',
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8002',
        changeOrigin: true,
      },
    },
  },
})
