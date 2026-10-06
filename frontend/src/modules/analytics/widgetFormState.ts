import type { AnalyticsWidget, WidgetChartType, WidgetTimeframe, WidgetType } from './types'
import type { AnalyticsWidgetPayload } from './api'

export interface WidgetFormState {
  type: WidgetType
  title: string
  signalId: string | undefined
  aggregation: AnalyticsWidget['aggregation']
  chartType: WidgetChartType
  showAverage: boolean
  timeframe: WidgetTimeframe
  periodStart: string | undefined
  days: number
}

export function defaultWidgetFormState(): WidgetFormState {
  return {
    type: 'value',
    title: '',
    signalId: undefined,
    aggregation: 'total',
    chartType: 'bar',
    showAverage: true,
    timeframe: 'this_week',
    periodStart: undefined,
    days: 7,
  }
}

export function widgetToFormState(widget: AnalyticsWidget): WidgetFormState {
  return {
    type: widget.type,
    title: widget.title,
    signalId: widget.signal.id,
    aggregation: widget.aggregation,
    chartType: widget.chart_type,
    showAverage: widget.show_average,
    timeframe: widget.timeframe,
    periodStart: widget.period_start ?? undefined,
    days: widget.days ?? 7,
  }
}

// Caller makes sure a signal is selected (form validation).
export function formStateToPayload(
  state: WidgetFormState,
  signalId: string,
): AnalyticsWidgetPayload {
  return {
    type: state.type,
    title: state.title.trim(),
    signal_id: signalId,
    aggregation: state.aggregation,
    chart_type: state.chartType,
    show_average: state.showAverage,
    timeframe: state.timeframe,
    period_start: state.periodStart ?? null,
    days: state.days ?? null,
  }
}
