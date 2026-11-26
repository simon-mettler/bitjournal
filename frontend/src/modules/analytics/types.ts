import type { Signal } from '@/modules/signals/types'

export type Timeframe = 'week' | 'month' | 'quarter' | 'year'

export interface SignalStatsPeriod {
  start: string
  end: string
  timeframe: Timeframe
}

export interface SignalStatsTimeseriesPoint {
  start: string // first and last day of the step, inclusive
  end: string
  value: number | null
  trend: number | null // moving average
  partial: boolean // the sum doesn't cover the full step
}

export interface SignalStatsTimeseries {
  step: 'day' | 'week'
  points: SignalStatsTimeseriesPoint[]
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
  timeseries: SignalStatsTimeseries
  day_of_week: SignalStatsDayOfWeekPoint[]
  heatmap: SignalStatsHeatmapPoint[]
}

export type WidgetChartType = 'bar' | 'line'
export type WidgetAggregation = 'total' | 'average' | 'per_event'
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

export interface ValueWidgetConfig {
  aggregation: WidgetAggregation
}

export interface TimeseriesWidgetConfig {
  chart_type: WidgetChartType
  show_average: boolean
}

// The settings of each widget type. A new type starts here.
export interface WidgetConfigByType {
  value: ValueWidgetConfig
  timeseries: TimeseriesWidgetConfig
}

export type WidgetType = keyof WidgetConfigByType
export type WidgetConfig = WidgetConfigByType[WidgetType]

interface AnalyticsWidgetBase {
  id: string
  order: number
  title: string
  signal: Signal
  timeframe: WidgetTimeframe
  period_start: string | null
  days: number | null
}

export type AnalyticsWidgetOf<T extends WidgetType> = AnalyticsWidgetBase & {
  type: T
  config: WidgetConfigByType[T]
}

export type AnalyticsWidget = { [T in WidgetType]: AnalyticsWidgetOf<T> }[WidgetType]

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
  timeseries: SignalStatsTimeseries | null
}
