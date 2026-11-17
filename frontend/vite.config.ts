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

// Unique per build. Baked into the bundle and emitted as /version.json so a running
// app can tell whether the server has a newer build (see shared/lib/appUpdate.ts).
const buildId = `${appVersion}-${Date.now().toString(36)}`

// https://vite.dev/config/
export default defineConfig({
  define: {
    __APP_VERSION__: JSON.stringify(appVersion),
    __BUILD_ID__: JSON.stringify(buildId),
  },
  plugins: [
    {
      name: 'bitjournal-version-json',
      apply: 'build',
      generateBundle() {
        this.emitFile({
          type: 'asset',
          fileName: 'version.json',
          source: JSON.stringify({ buildId }),
        })
      },
    },
    vue(),
    //    vueDevTools(),
    VitePWA({
      registerType: 'prompt',
      injectRegister: false,

      manifest: {
        name: 'bitjournal',
        short_name: 'bitjournal',
        description: 'Track anything. See the patterns.',
        id: '/',
        start_url: '/',
        scope: '/',
        display: 'standalone',
        theme_color: '#eef2f9',
        background_color: '#069dc0',

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
          {
            src: '/pwa-maskable-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable',
          },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,woff2}'],
        navigateFallbackDenylist: [/^\/api\//, /^\/admin(\/|$)/, /^\/static\//],
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
