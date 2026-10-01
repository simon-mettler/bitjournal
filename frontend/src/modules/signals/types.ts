export interface SignalCategory {
  id: string
  name: string
  icon: string
  color: string
}

export type SignalType = 'tally' | 'range' | 'value' | 'duration'
export type SummaryMethod = 'total' | 'average'

export interface Signal {
  id: string
  category?: string | null
  name: string
  type: SignalType
  icon?: string
  color?: string
  summary_method: SummaryMethod
  is_archived: boolean
  range_config?: SignalRangeConfig | null
  value_config?: SignalValueConfig | null
  created_at: string
  updated_at: string
}

export interface SignalRangeConfig {
  min_value: number
  max_value: number
  min_label?: string
  max_label?: string
}

export interface SignalValueConfig {
  unit: string
}
