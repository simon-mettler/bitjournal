import { defineStore } from 'pinia'
import axios from 'axios'

const authApi = axios.create({
  baseURL: 'http://localhost:8000/api/',
  withCredentials: true,
})

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
      await authApi.post('register/', payload)
      await this.login({ username: payload.username, password: payload.password })
    },

    async login(payload: { username: string; password: string }) {
      const { data } = await authApi.post<{ access: string }>('token/', payload)
      this.accessToken = data.access
    },

    async refreshAccessToken(): Promise<string> {
      const { data } = await authApi.post<{ access: string }>('token/refresh/')
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
        await authApi.post('logout/')
      } finally {
        this.accessToken = ''
      }
    },
  },
})
