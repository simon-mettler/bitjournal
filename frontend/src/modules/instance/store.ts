import { defineStore } from 'pinia'
import { getInstanceConfig } from './api'
import type { InstanceConfig } from './types'

const defaultConfig: InstanceConfig = {
  registration_enabled: true,
  email_enabled: false,
  notice: '',
  extra: {},
}

export const useInstanceStore = defineStore('instance', {
  state: () => ({
    config: { ...defaultConfig } as InstanceConfig,
    loaded: false,
  }),

  getters: {
    registrationEnabled: (state) => state.config.registration_enabled,
  },

  actions: {
    async load() {
      try {
        const { data } = await getInstanceConfig()
        this.config = data
      } catch {
        this.config = { ...defaultConfig }
      } finally {
        this.loaded = true
      }
    },
  },
})
