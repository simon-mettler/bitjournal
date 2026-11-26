import type { AnalyticsWidget, WidgetConfig, WidgetTimeframe, WidgetType } from './types'
import type { AnalyticsWidgetPayload } from './api'
import { widgetDefinition } from './widgetRegistry'

export interface WidgetFormState {
  type: WidgetType
  title: string
  signalId: string | undefined
  config: WidgetConfig
  timeframe: WidgetTimeframe
  periodStart: string | undefined
  days: number
}

export function defaultWidgetFormState(type: WidgetType = 'value'): WidgetFormState {
  return {
    type,
    title: '',
    signalId: undefined,
    config: widgetDefinition(type).defaultConfig(),
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
    config: { ...widget.config },
    timeframe: widget.timeframe,
    periodStart: widget.period_start ?? undefined,
    days: widget.days ?? 7,
  }
}

export function formStateToPayload(
  state: WidgetFormState,
  signalId: string,
): AnalyticsWidgetPayload {
  return {
    type: state.type,
    title: state.title.trim(),
    signal_id: signalId,
    config: state.config,
    timeframe: state.timeframe,
    period_start: state.periodStart ?? null,
    days: state.days ?? null,
  } as AnalyticsWidgetPayload
}
