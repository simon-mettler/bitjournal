import type { EChartsOption } from 'echarts'
import type { Signal } from '@/modules/signals/types'
import { formatStatValue, formatDurationAxisLabel, durationAxisScale } from './format'
import { tooltipBesidePointer } from './tooltipPosition'
import { chartColors } from './chartColors'

export const DAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

export const tooltipStyle = {
  backgroundColor: chartColors.tooltipBackground,
  borderWidth: 0,
  borderRadius: 8,
  padding: [6, 10],
  textStyle: { color: chartColors.tooltipText, fontSize: 12 },
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

export function categoryAxis(data: string[], labelAt?: (index: number) => string): EChartsOption['xAxis'] {
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

// Durations axis that snaps to whole seconds/minutes/hours.
export function valueYAxis(signal: Signal, values: (number | null)[]): EChartsOption['yAxis'] {
  const scale =
    signal.type === 'duration' ? durationAxisScale(Math.max(0, ...values.map((v) => v ?? 0))) : null
  return {
    type: 'value',
    splitLine: { lineStyle: { color: chartColors.gridLine } },
    axisLabel: {
      color: chartColors.axisLabel,
      formatter: scale ? (value: number) => formatDurationAxisLabel(value) : undefined,
    },
    max: scale?.max,
    interval: scale?.interval,
  }
}
