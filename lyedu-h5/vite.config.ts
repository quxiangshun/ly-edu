import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 9801,
    proxy: {
      '/api': {
        target: 'http://localhost:9700',
        changeOrigin: true
      },
      '/uploads': {
        target: 'http://localhost:9700',
        changeOrigin: true,
        rewrite: (path) => '/api' + path
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false
  }
})
