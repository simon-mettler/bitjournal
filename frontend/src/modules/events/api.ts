import { api } from '@/shared/api'
import type { CreateEventPayload, UpdateEventPayload, Event } from './types'

export function getEvents() {
  return api.get<Event[]>('events/')
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
