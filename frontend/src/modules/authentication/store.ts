import { isAxiosError } from 'axios'
import { defineStore } from 'pinia'
import { api } from '@/shared/api'

let inflightRefresh: Promise<string> | null = null

function withRefreshLock<T>(fn: () => Promise<T>): Promise<T> {
  if (typeof navigator !== 'undefined' && navigator.locks) {
    return navigator.locks.request('bitjournal-refresh', fn)
  }
  return fn()
}

export function isUnauthorized(error: unknown) {
  return isAxiosError(error) && error.response?.status === 401
}

export async function waitForRefresh() {
  try {
    await inflightRefresh
  } catch {}
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: '',
    initialized: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
  },

  actions: {
    async register(payload: { email: string; password: string }) {
      await api.post('register/', payload)
      await this.login(payload)
    },

    async login(payload: { email: string; password: string }) {
      const { data } = await api.post<{ access: string }>('token/', payload)
      this.accessToken = data.access
    },

    refreshAccessToken(): Promise<string> {
      inflightRefresh ??= withRefreshLock(async () => {
        const { data } = await api.post<{ access: string }>('token/refresh/')
        this.accessToken = data.access
        return data.access
      }).finally(() => {
        inflightRefresh = null
      })
      return inflightRefresh
    },

    /** Local-only sign-out: the server session is left untouched. */
    clearSession() {
      this.accessToken = ''
    },

    async tryRefresh() {
      // Only a real 401 means the session is gone. Network errors / 5xx (server
      // restarting, iOS resuming without network) are retried a few times.
      const delays = [1000, 2000, 4000]
      try {
        for (let attempt = 0; ; attempt++) {
          try {
            await this.refreshAccessToken()
            return
          } catch (error) {
            if (isUnauthorized(error) || attempt >= delays.length) {
              this.accessToken = ''
              return
            }
            await new Promise((resolve) => setTimeout(resolve, delays[attempt]))
          }
        }
      } finally {
        this.initialized = true
      }
    },

    async logoutAll() {
      await api.post('users/me/logout-all/')
      this.accessToken = ''
    },

    async deleteAccount(payload: { password: string; email: string }) {
      await api.post('users/me/delete/', payload)
      this.accessToken = ''
    },

    async logout() {
      try {
        await api.post('token/logout/')
      } finally {
        this.accessToken = ''
      }
    },
  },
})
