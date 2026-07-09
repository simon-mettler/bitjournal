export interface TrackerCategory {
  id: number
  name: string
  icon: string
  color: string
}

export interface Tracker {
  id: number
  category: number
  name: string
  type: 'range' | 'value'
  icon: string
  color: string
  summary_method: string
  is_archived: boolean
  range_config?: TrackerRangeConfig
  value_config?: TrackerValueConfig
  created_at: string
  updated_at: string
}

export interface TrackerRangeConfig {
  min_value: number
  max_value: number
  min_label: string
  max_label: string
}

export interface TrackerValueConfig {
  unit: string
}
