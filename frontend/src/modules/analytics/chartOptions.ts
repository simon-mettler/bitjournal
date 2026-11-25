import type { EChartsOption } from 'echarts'
import type { Signal } from '@/modules/signals/types'
import { formatStatValue, formatDurationAxisLabel, durationAxisScale } from './format'
import { tooltipBesidePointer } from './tooltipPosition'
import { chartColors } from './chartColors'

export const DAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

export const tooltipStyle = {
  get backgroundColor() {
    return chartColors.tooltipBackground
  },
  borderWidth: 0,
  borderRadius: 8,
  padding: [6, 10],
  get textStyle() {
    return { color: chartColors.tooltipText, fontSize: 12 }
  },
}

// Options shared by the bar/line charts.
export function valueTooltip(signal: Signal): EChartsOption['tooltip'] {
  return {
    trigger: 'axis',
    position: tooltipBesidePointer,
    valueFormatter: (value) =>
      value == null || value === '-' ? '-' : formatStatValue(signal, Number(value)),
    ...tooltipStyle,
  }
}

export function categoryAxis(
  data: string[],
  labelAt?: (index: number) => string,
): EChartsOption['xAxis'] {
  return {
    type: 'category',
    data,
    axisLine: { lineStyle: { color: chartColors.gridLine } },
    axisLabel: {
      color: chartColors.axisLabel,
      formatter: labelAt && ((_: string, index: number) => labelAt(index)),
    },
    axisTick: { show: false },
  }
}

// Bounds of the y-axis. Sums and bars start at zero. Averages of range signals use the
// configured scale, line charts of averaged measurements fit the data.
export function valueAxisBounds(
  signal: Signal,
  values: (number | null)[],
  chartType: 'bar' | 'line',
): { min?: number; max?: number; scale?: boolean } {
  if (signal.summary_method !== 'average') return {}
  if (signal.type === 'range' && signal.range_config) {
    // values logged before the range was changed can lie outside of it
    const present = values.filter((v) => v !== null)
    const min = Math.min(Number(signal.range_config.min_value), ...present)
    const max = Math.max(Number(signal.range_config.max_value), ...present)
    return { min: chartType === 'bar' ? Math.min(0, min) : min, max }
  }
  return signal.type === 'value' && chartType === 'line' ? { scale: true } : {}
}

// Durations axis snaps to whole seconds/minutes/hours.
export function valueYAxis(
  signal: Signal,
  values: (number | null)[],
  chartType: 'bar' | 'line' = 'bar',
): EChartsOption['yAxis'] {
  const scale =
    signal.type === 'duration' ? durationAxisScale(Math.max(0, ...values.map((v) => v ?? 0))) : null
  return {
    type: 'value',
    ...valueAxisBounds(signal, values, chartType),
    splitLine: { lineStyle: { color: chartColors.gridLine } },
    axisLabel: {
      color: chartColors.axisLabel,
      formatter: scale ? (value: number) => formatDurationAxisLabel(value) : undefined,
    },
    ...(scale && { max: scale.max, interval: scale.interval }),
  }
}
