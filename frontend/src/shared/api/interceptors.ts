import { AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { api } from './axios'
import { useAuthStore } from '@/modules/authentication/store'

let refreshing: Promise<string> | null = null
let initialized = false;

export function setupApiInterceptors() {
  if (initialized) return;
  initialized = true;

  api.interceptors.request.use((config) => {
    const auth = useAuthStore()

    if (auth.accessToken) {
      config.headers.Authorization = `Bearer ${auth.accessToken}`
    }

    return config
  })

  api.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
      const auth = useAuthStore()

      const isAuthEndpoint = /^(token|register|logout)\//.test(originalRequest.url ?? '')

      if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
        originalRequest._retry = true
        refreshing ??= auth.refreshAccessToken()
          .catch((refreshError) => {
            auth.logout()
            throw refreshError
          })
          .finally(() => (refreshing = null))

        await refreshing
        return api(originalRequest)
      }

      return Promise.reject(error)
    }
  )

}
