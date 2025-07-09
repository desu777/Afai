import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import legacy from '@vitejs/plugin-legacy'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    legacy({
      targets: ['defaults', 'not IE 11', 'iOS >= 12', 'Android >= 7']
    })
  ],
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