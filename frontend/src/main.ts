import './shared/ui/tokens.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { useAuthStore } from '@/modules/authentication/store'
import { setupApiInterceptors } from '@/shared/api'


const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

setupApiInterceptors()

const auth = useAuthStore()

app.mount('#app')
