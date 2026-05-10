import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://165.245.138.122:8000',
        changeOrigin: true,
        rewrite: path => path.replace(/^\/api/, ''),
        ws: true,
      },
    },
  },
})
