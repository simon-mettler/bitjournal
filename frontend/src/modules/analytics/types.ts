import type { Signal } from '@/modules/signals/types'

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

export type WidgetType = 'value' | 'timeseries'
export type WidgetChartType = 'bar' | 'line'
export type WidgetAggregation = 'total' | 'average'
export type WidgetTimeframe =
  | 'today'
  | 'yesterday'
  | 'this_week'
  | 'last_week'
  | 'this_month'
  | 'last_month'
  | 'this_quarter'
  | 'quarter'
  | 'this_year'
  | 'year'
  | 'last_days'

export interface AnalyticsWidget {
  id: string
  order: number
  type: WidgetType
  title: string
  signal: Signal
  aggregation: WidgetAggregation
  chart_type: WidgetChartType
  show_average: boolean
  timeframe: WidgetTimeframe
  period_start: string | null
  days: number | null
}

export interface AnalyticsBoard {
  id: string
  name: string
  order: number
  widgets: AnalyticsWidget[]
  created_at: string
}

export interface AnalyticsWidgetValue {
  widget_id: string
  value: number | null
  count: number
  period: {
    start: string
    end: string
  }
  timeseries: SignalStatsTimeseriesPoint[] | null
}
