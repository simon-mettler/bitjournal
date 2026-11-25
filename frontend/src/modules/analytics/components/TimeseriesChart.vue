<script setup lang="ts">
import { computed } from 'vue'
import Chart from '@/shared/ui/components/Chart.vue'
import { chartColors, signalColor } from '@/modules/analytics/chartColors'
import {
  categoryAxis,
  valueAxisBounds,
  valueTooltip,
  valueYAxis,
} from '@/modules/analytics/chartOptions'
import { lineData, lineSymbolOptions } from '@/modules/analytics/lineSymbols'
import { parseIsoDate } from '@/modules/analytics/format'
import type { EChartsOption } from 'echarts'
import type { Signal } from '@/modules/signals/types'
import type { SignalStatsTimeseries } from '@/modules/analytics/types'

const props = withDefaults(
  defineProps<{
    signal: Signal
    timeseries: SignalStatsTimeseries
    chartType: 'bar' | 'line'
    showAverage?: boolean
    height?: number
  }>(),
  {
    showAverage: true,
  },
)

const shortDateFormat = new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric' })

function formatShortDate(value: string): string {
  return shortDateFormat.format(parseIsoDate(value))
}

const isWeekly = computed(() => props.timeseries.step === 'week')

const points = computed(() =>
  props.timeseries.points.map((p) => {
    const range = isWeekly.value
      ? `${formatShortDate(p.start)} - ${formatShortDate(p.end)}`
      : p.start
    return {
      ...p,
      label: p.partial ? `${range} (incomplete)` : range,
      axisLabel: formatShortDate(p.start),
    }
  }),
)

const values = computed(() => points.value.map((p) => p.value))
const trendValues = computed(() => points.value.map((p) => p.trend))
const trendName = computed(() => (isWeekly.value ? '4-week avg' : '7-day avg'))
const axisValues = computed(() =>
  props.showAverage ? [...values.value, ...trendValues.value] : values.value,
)
const hasZeroBaseline = computed(() => {
  const bounds = valueAxisBounds(props.signal, axisValues.value, props.chartType)
  return !bounds.scale && (bounds.min ?? 0) === 0
})

const connectsGaps = computed(() => props.signal.summary_method === 'average')

const mainSeries = computed(() => {
  const color = signalColor(props.signal)
  if (props.chartType === 'bar') {
    return {
      name: props.signal.name,
      type: 'bar' as const,
      data: points.value.map((p) => ({
        value: p.value,
        itemStyle: p.partial ? { opacity: 0.45 } : undefined,
      })),
      barMaxWidth: 24,
      itemStyle: { color, borderRadius: [8, 8, 0, 0] },
    }
  }
  return {
    name: props.signal.name,
    type: 'line' as const,
    data: lineData(values.value, connectsGaps.value),
    ...lineSymbolOptions,
    connectNulls: connectsGaps.value,
    // smaller when every value is marked, to keep long periods readable
    symbolSize: connectsGaps.value ? 6 : 8,
    itemStyle: { color },
    lineStyle: { width: 2, color },
    areaStyle: hasZeroBaseline.value ? { color, opacity: 0.1 } : undefined,
  }
})

const option = computed<EChartsOption>(() => ({
  tooltip: valueTooltip(props.signal),
  legend: {
    data: [
      {
        name: props.signal.name,
        itemStyle: props.chartType === 'line' ? { opacity: 0 } : undefined, // hide legend dot
      },
      ...(props.showAverage ? [{ name: trendName.value, itemStyle: { opacity: 0 } }] : []),
    ],
    bottom: 0,
    left: 'center',
    textStyle: { color: chartColors.axisLabel },
  },
  grid: {
    left: 0,
    right: 16,
    top: 16,
    bottom: 32,
    outerBoundsMode: 'same',
    outerBoundsContain: 'axisLabel',
  },
  xAxis: categoryAxis(
    points.value.map((p) => p.label),
    (index) => points.value[index].axisLabel,
  ),
  yAxis: valueYAxis(props.signal, axisValues.value, props.chartType),
  series: [
    mainSeries.value,
    ...(props.showAverage
      ? [
          {
            name: trendName.value,
            type: 'line' as const,
            data: lineData(trendValues.value),
            ...lineSymbolOptions,
            connectNulls: connectsGaps.value,
            symbolSize: 5,
            itemStyle: { color: chartColors.primary },
            lineStyle: { width: 2, color: chartColors.primary, type: 'dashed' as const },
          },
        ]
      : []),
  ],
}))
</script>

<template>
  <Chart :option="option" :height="height" />
</template>
