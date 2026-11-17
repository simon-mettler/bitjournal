import '@fontsource-variable/figtree'
import './shared/ui/tokens.css'
import './shared/ui/base.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { useAuthStore } from '@/modules/authentication/store'
import { setupApiInterceptors } from '@/shared/api'
import { initTheme } from '@/shared/lib/useTheme'
import { installAppUpdate } from '@/shared/lib/appUpdate'

initTheme()

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

setupApiInterceptors()

useAuthStore()

void router.isReady().then(
  () => app.mount('#app'),
  () => app.mount('#app'),
)

installAppUpdate(router)
