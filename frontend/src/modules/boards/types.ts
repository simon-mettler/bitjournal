import type { Signal } from '@/modules/signals/types'

export interface BoardSignal {
  signal: Signal
  order: number
}

export interface Board {
  id: string
  name: string
  order: number
  board_signals: BoardSignal[]
  created_at: string
}
