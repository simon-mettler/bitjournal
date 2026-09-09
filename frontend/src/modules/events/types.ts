import type { Signal } from '@/modules/signals/types'

export interface SignalEntryInput {
  id?: string
  signal_id: string
  value?: number
  duration?: string
}

export interface CreateEventPayload {
  occurred_at: string
  note?: string
  entries: SignalEntryInput[]
}

export interface UpdateEventPayload {
  occurred_at: string
  note?: string
  entries: SignalEntryInput[]
}

export interface SignalEventEntry {
  id: string
  signal: Signal
  value?: number
  duration?: string
}

export interface Event {
  id: string
  occurred_at: string
  note: string
  entries: SignalEventEntry[]
  created_at: string
  updated_at: string
}

// A value staged in the draft bar before the event is actually saved.
export interface DraftEntry {
  id: string // local id for the draft bar, always present
  entryId?: string // server-side id, present in entries that already exist in DB
  signal: Signal
  value?: number
  duration?: string
}
