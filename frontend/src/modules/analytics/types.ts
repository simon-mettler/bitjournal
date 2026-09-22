export type Timeframe = 'week' | 'month' | 'quarter' | 'year'

export interface SignalStatsPeriod {
  start: string
  end: string
  timeframe: Timeframe
}

export interface SignalStatsTimeseriesPoint {
  date: string
  value: number | null
}

export interface SignalStatsDayOfWeekPoint {
  dow: number
  value: number | null
}

// value is the sum or average based on signal summary_method of the entries in the bin.
export interface SignalStatsHeatmapPoint {
  dow: number
  hour: number
  count: number
  value: number
}

export interface SignalStats {
  signal: {
    id: string
    summary_method: 'total' | 'average'
  }
  period: SignalStatsPeriod
  total: number
  average: number
  count: number
  timeseries: SignalStatsTimeseriesPoint[]
  day_of_week: SignalStatsDayOfWeekPoint[]
  heatmap: SignalStatsHeatmapPoint[]
}
