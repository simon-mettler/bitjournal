import '@fontsource-variable/figtree'
import './shared/ui/tokens.css'
import './shared/ui/base.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { registerSW } from 'virtual:pwa-register'

import App from './App.vue'
import router from './router'
import { useAuthStore } from '@/modules/authentication/store'
import { setupApiInterceptors } from '@/shared/api'
import { initTheme } from '@/shared/lib/useTheme'
import { useToast } from '@/shared/lib/useToast'

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

const UPDATE_CHECK_MS = 60 * 60 * 1000

const updateSW = registerSW({
  onNeedRefresh() {
    useToast().toast({
      title: 'Update available',
      description: 'A new version of Bitjournal is ready.',
      duration: Infinity,
      actionLabel: 'Reload',
      actionAltText: 'Reload to update',
      onAction: () => void updateSW(true),
    })
  },
  onRegisteredSW(_url, registration) {
    if (!registration) return
    const check = () => void registration.update().catch(() => {})
    setInterval(check, UPDATE_CHECK_MS)
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') check()
    })
  },
})
