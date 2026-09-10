import { defineStore } from 'pinia';

export const useLogEventsUiStore = defineStore('log-events-ui', {
  state: () => ({
    activeTab: 'all' as string
  }),
})

