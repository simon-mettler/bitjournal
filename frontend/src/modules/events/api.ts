import { api } from '@/shared/api'
import type { CreateEventPayload, UpdateEventPayload, Event } from './types'

export interface PaginatedResponse<T> {
  next: string | null
  previous: string | null
  results: T[]
}

export type SignalLogic = 'and' | 'or'

export interface GetEventsParams {
  before?: string
  signalIds?: string[]
  signalLogic?: SignalLogic
  limit?: number
  cursor?: string
}

export function getEvents(params: GetEventsParams = {}) {
  const query: Record<string, string> = {}
  if (params.before) query.before = params.before
  if (params.signalIds?.length) query.signals = params.signalIds.join(',')
  if (params.signalLogic) query.signal_logic = params.signalLogic
  if (params.limit) query.limit = String(params.limit)
  if (params.cursor) query.cursor = params.cursor

  return api.get<PaginatedResponse<Event>>('events/', { params: query })
}

export function cursorOf(nextUrl: string | null) {
  return nextUrl ? new URL(nextUrl).searchParams.get('cursor') : null
}

export function getEvent(id: string) {
  return api.get<Event>(`events/${id}/`)
}

export function updateEvent(id: string, payload: UpdateEventPayload) {
  return api.put<Event>(`events/${id}/`, payload)
}

export function createEvent(payload: CreateEventPayload) {
  return api.post<Event>('events/', payload)
}

export function deleteEvent(id: string) {
  return api.delete<Event>(`events/${id}/`)
}
