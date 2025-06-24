import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/chat': 'http://localhost:2103',
      '/health': 'http://localhost:2103',
      '/feedback': 'http://localhost:2103',
      '/analytics': 'http://localhost:2103'
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
}) 