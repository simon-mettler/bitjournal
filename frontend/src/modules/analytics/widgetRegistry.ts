import type { Component } from 'vue'
import type { WidgetConfigByType, WidgetTimeframe, WidgetType } from './types'
import ValuePreview from './components/previews/ValuePreview.vue'
import TimeseriesPreview from './components/previews/TimeseriesPreview.vue'
import ValueSettings from './components/settings/ValueSettings.vue'
import TimeseriesSettings from './components/settings/TimeseriesSettings.vue'
import ValueDisplay from './components/display/ValueDisplay.vue'
import TimeseriesDisplay from './components/display/TimeseriesDisplay.vue'

// Everything the app knows about one widget type. The backend counterpart is
// apps/analytics/widget_types.py.
export interface WidgetDefinition<T extends WidgetType = WidgetType> {
  type: T
  name: string
  description: string
  preview: Component
  defaultConfig: () => WidgetConfigByType[T]
  // form fields for the config: v-model, prop `signal`
  settings: Component
  // card content on the dashboard: props `widget` and `data`
  display: Component
  wide: boolean // takes more columns on the dashboard
  excludedTimeframes: WidgetTimeframe[]
}

const DEFINITIONS: { [T in WidgetType]: WidgetDefinition<T> } = {
  value: {
    type: 'value',
    name: 'Value',
    description: 'A single number for one signal, such as the total coffees or the average mood.',
    preview: ValuePreview,
    defaultConfig: () => ({ aggregation: 'total' }),
    settings: ValueSettings,
    display: ValueDisplay,
    wide: false,
    excludedTimeframes: [],
  },
  timeseries: {
    type: 'timeseries',
    name: 'Timeseries',
    description: 'A bar or line chart showing how a signal develops over a period.',
    preview: TimeseriesPreview,
    defaultConfig: () => ({ chart_type: 'bar', show_average: true }),
    settings: TimeseriesSettings,
    display: TimeseriesDisplay,
    wide: true,
    // a single day has nothing to plot over time
    excludedTimeframes: ['today', 'yesterday'],
  },
}

// The widgets offered in the gallery, in display order.
export const WIDGET_DEFINITIONS: WidgetDefinition[] = Object.values(DEFINITIONS)

export function widgetDefinition<T extends WidgetType>(type: T): WidgetDefinition<T> {
  return DEFINITIONS[type]
}

export function findWidgetDefinition(type: unknown): WidgetDefinition | undefined {
  return WIDGET_DEFINITIONS.find((definition) => definition.type === type)
}
