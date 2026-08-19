import { api } from '@/shared/api'
import type { CreateEventPayload, Event } from './types'

export function createEvent(payload: CreateEventPayload) {
  return api.post<Event>('events/', payload)
}
