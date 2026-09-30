import { defineStore } from 'pinia'

export const useDashboardUiStore = defineStore('dashboard-ui', {
  state: () => ({
    activeBoardId: null as string | null,
    editing: false,
  }),
})
