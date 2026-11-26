import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import type { Timeframe, WidgetCalculation } from '../types'

const STORAGE_KEY = 'bitjournal:signal-stats-ui'

interface PersistedState {
  timeframe: Timeframe
  chartType: 'bar' | 'line'
  calculations: Record<string, WidgetCalculation> // chosen per signal id
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

  const calculations = ref<Record<string, WidgetCalculation>>(persisted.calculations ?? {})

  watch(
    [timeframe, chartType, calculations],
    () => {
      try {
        localStorage.setItem(
          STORAGE_KEY,
          JSON.stringify({
            timeframe: timeframe.value,
            chartType: chartType.value,
            calculations: calculations.value,
          }),
        )
      } catch {}
    },
    { deep: true },
  )

  return { timeframe, chartType, calculations }
})
