import type { Signal } from '@/modules/signals/types'

export interface SignalEntryInput {
  signal_id: string
  value?: number
  duration?: string // "HH:MM:SS"
}

export interface CreateEventPayload {
  date: string // YYYY-MM-DD
  time: string // HH:MM:SS
  note?: string
  entries: SignalEntryInput[]
}

export interface SignalEventEntry {
  signal: Signal
  value: string | null
  duration: string | null
}

export interface Event {
  id: string
  date: string
  time: string
  note: string
  entries: SignalEventEntry[]
  created_at: string
  updated_at: string
}

// A value staged in the draft bar before the event is actually saved.
export interface DraftEntry {
  id: string
  signal: Signal
  value?: number
  duration?: string // "HH:MM:SS"
}
