import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import type { Timeframe } from '../types'

const STORAGE_KEY = 'bitjournal:signal-stats-ui'

interface PersistedState {
  timeframe: Timeframe
  chartType: 'bar' | 'line'
}

function readPersisted(): Partial<PersistedState> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : {}
  } catch {
    return {}
  }
}

export const useSignalStatsUiStore = defineStore('signal-stats-ui', () => {
  const persisted = readPersisted()
  const timeframe = ref<Timeframe>(persisted.timeframe ?? 'week')
  const chartType = ref<'bar' | 'line'>(persisted.chartType ?? 'bar')

  watch([timeframe, chartType], ([newTimeframe, newChartType]) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ timeframe: newTimeframe, chartType: newChartType }))
    } catch {
    }
  })

  return { timeframe, chartType }
})
