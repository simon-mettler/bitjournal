import { api } from '@/shared/api'
import type { SignalStats, Timeframe } from './types'

export interface GetSignalStatsParams {
  timeframe: Timeframe
  periodStart: string // YYYY-MM-DD, local calendar date
}

export function getSignalStats(signalId: string, params: GetSignalStatsParams) {
  return api.get<SignalStats>(`analytics/signals/${signalId}/stats/`, {
    params: {
      timeframe: params.timeframe,
      period_start: params.periodStart,
      tz: Intl.DateTimeFormat().resolvedOptions().timeZone,
    },
  })
}
