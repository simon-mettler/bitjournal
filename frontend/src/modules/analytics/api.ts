import { api } from '@/shared/api'
import type {
  AnalyticsBoard,
  AnalyticsWidget,
  AnalyticsWidgetValue,
  SignalStats,
  Timeframe,
} from './types'

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

export type CreateAnalyticsBoardPayload = Pick<AnalyticsBoard, 'name'>

export type AnalyticsWidgetPayload = Omit<AnalyticsWidget, 'id' | 'order' | 'signal'> & {
  signal_id: string
}

export type CreateAnalyticsWidgetPayload = AnalyticsWidgetPayload & {
  board_id: AnalyticsBoard['id']
}

export type UpdateAnalyticsBoardPayload = {
  name: AnalyticsBoard['name']
  widget_ids: AnalyticsWidget['id'][]
}

export type ReorderAnalyticsBoardsPayload = {
  board_ids: AnalyticsBoard['id'][]
}

export function getAnalyticsBoards() {
  return api.get<AnalyticsBoard[]>('analytics-boards/')
}

export function getAnalyticsBoard(id: string) {
  return api.get<AnalyticsBoard>(`analytics-boards/${id}/`)
}

export function createAnalyticsBoard(payload: CreateAnalyticsBoardPayload) {
  return api.post<AnalyticsBoard>('analytics-boards/', payload)
}

export function updateAnalyticsBoard(id: string, payload: UpdateAnalyticsBoardPayload) {
  return api.put<AnalyticsBoard>(`analytics-boards/${id}/`, payload)
}

export function deleteAnalyticsBoard(id: string) {
  return api.delete(`analytics-boards/${id}/`)
}

export function reorderAnalyticsBoards(payload: ReorderAnalyticsBoardsPayload) {
  return api.post<AnalyticsBoard[]>('analytics-boards/reorder/', payload)
}

export function getAnalyticsBoardValues(id: string) {
  return api.get<AnalyticsWidgetValue[]>(`analytics-boards/${id}/values/`, {
    params: { tz: Intl.DateTimeFormat().resolvedOptions().timeZone },
  })
}

export function getAnalyticsWidget(id: string) {
  return api.get<AnalyticsWidget>(`analytics-widgets/${id}/`)
}

export function createAnalyticsWidget(payload: CreateAnalyticsWidgetPayload) {
  return api.post<AnalyticsWidget>('analytics-widgets/', payload)
}

export function updateAnalyticsWidget(id: string, payload: AnalyticsWidgetPayload) {
  return api.put<AnalyticsWidget>(`analytics-widgets/${id}/`, payload)
}

export function deleteAnalyticsWidget(id: string) {
  return api.delete(`analytics-widgets/${id}/`)
}
