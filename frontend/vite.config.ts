import { readFileSync } from 'node:fs'
import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
//import vueDevTools from 'vite-plugin-vue-devtools'
import { VitePWA } from 'vite-plugin-pwa'

// Release builds pass the git tag version in via APP_VERSION (see Dockerfile).
const appVersion: string =
  process.env.APP_VERSION ||
  (
    JSON.parse(readFileSync(new URL('./package.json', import.meta.url), 'utf8')) as {
      version: string
    }
  ).version

// https://vite.dev/config/
export default defineConfig({
  define: {
    __APP_VERSION__: JSON.stringify(appVersion),
  },
  plugins: [
    vue(),
    //    vueDevTools(),
    VitePWA({
      registerType: 'autoUpdate',

      manifest: {
        name: 'Bitjournal',
        short_name: 'Bitjournal',
        description: 'Log anything and learn',
        id: '/',
        start_url: '/',
        scope: '/',
        display: 'standalone',

        icons: [
          {
            src: '/pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: '/pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
          },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,woff2}'],
      },
      devOptions: {
        enabled: true,
      },
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
