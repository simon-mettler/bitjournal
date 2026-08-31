import { defineStore } from 'pinia'
import { api } from '@/shared/api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: '' as string,
    initialized: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
  },

  actions: {
    async register(payload: { username: string; email: string; password: string }) {
      await api.post('register/', payload)
      await this.login({
        username: payload.username,
        password: payload.password,
      })
    },

    async login(payload: { username: string; password: string }) {
      const { data } = await api.post<{ access: string }>('token/', payload)
      this.accessToken = data.access
    },

    async refreshAccessToken(): Promise<string> {
      const { data } = await api.post<{ access: string }>('token/refresh/')
      this.accessToken = data.access
      return data.access
    },

    async tryRefresh() {
      try {
        await this.refreshAccessToken()
      } catch {
        this.accessToken = ''
      } finally {
        this.initialized = true
      }
    },

    async logout() {
      try {
        await api.post('logout/')
      } finally {
        this.accessToken = ''
      }
    },
  },
})
