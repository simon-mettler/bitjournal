import { AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { api } from './axios'
import { useAuthStore } from '@/modules/authentication/store'

let isRefreshing = false
let queue: Array<(token: string) => void> = []
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

      const isAuthEndpoint = originalRequest.url?.includes('token/refresh')
        || originalRequest.url?.includes('logout')

      if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
        if (isRefreshing) {
          return new Promise((resolve) => {
            queue.push((token: string) => {
              originalRequest.headers.Authorization = `Bearer ${token}`
              resolve(api(originalRequest))
            })
          })
        }

        originalRequest._retry = true
        isRefreshing = true

        try {
          const newAccess = await auth.refreshAccessToken()
          queue.forEach((cb) => cb(newAccess))
          queue = []
          originalRequest.headers.Authorization = `Bearer ${newAccess}`
          return api(originalRequest)
        } catch (refreshError) {
          queue = []
          auth.logout()
          return Promise.reject(refreshError)
        } finally {
          isRefreshing = false
        }
      }

      return Promise.reject(error)
    }
  )

}
