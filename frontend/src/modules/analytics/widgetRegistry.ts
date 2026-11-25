import type { Component } from 'vue'
import type { WidgetType } from './types'
import ValuePreview from './components/previews/ValuePreview.vue'
import TimeseriesPreview from './components/previews/TimeseriesPreview.vue'

export interface WidgetDefinition {
  type: WidgetType
  name: string
  description: string
  preview: Component
}

// The widgets offered in the gallery, in display order.
export const WIDGET_DEFINITIONS: WidgetDefinition[] = [
  {
    type: 'value',
    name: 'Value',
    description: 'A single number for one signal, such as the total coffees this week.',
    preview: ValuePreview,
  },
  {
    type: 'timeseries',
    name: 'Timeseries',
    description: 'A bar or line chart showing how a signal develops over a period.',
    preview: TimeseriesPreview,
  },
]

export function findWidgetDefinition(type: unknown): WidgetDefinition | undefined {
  return WIDGET_DEFINITIONS.find((definition) => definition.type === type)
}
