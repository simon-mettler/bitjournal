<script setup lang="ts">
import { computed } from 'vue'
import Chart from '@/shared/ui/components/Chart.vue'
import { binTimeseriesByWeek, WEEKLY_BIN_TIMEFRAMES } from '@/modules/analytics/timeseriesBins'
import { chartColors, signalColor } from '@/modules/analytics/chartColors'
import { categoryAxis, valueTooltip, valueYAxis } from '@/modules/analytics/chartOptions'
import { parseIsoDate } from '@/modules/analytics/format'
import type { EChartsOption } from 'echarts'
import type { Signal } from '@/modules/signals/types'
import type { SignalStatsTimeseriesPoint, Timeframe } from '@/modules/analytics/types'

const props = withDefaults(defineProps<{
  signal: Signal
  timeseries: SignalStatsTimeseriesPoint[]
  timeframe?: Timeframe
  chartType: 'bar' | 'line'
  showAverage?: boolean
  weekly?: boolean
  height?: number
}>(), {
  showAverage: true,
  weekly: undefined,
})

const shortDateFormat = new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric' })

function formatShortDate(value: string): string {
  return shortDateFormat.format(parseIsoDate(value))
}

const isWeekly = computed(() => props.weekly ?? (props.timeframe !== undefined && WEEKLY_BIN_TIMEFRAMES.has(props.timeframe)))

const points = computed(() => {
  if (!isWeekly.value) {
    return props.timeseries.map((p) => ({ label: p.date, axisLabel: formatShortDate(p.date), value: p.value }))
  }
  return binTimeseriesByWeek(props.timeseries, props.signal.summary_method).map((bin) => ({
    label: `${formatShortDate(bin.start)} - ${formatShortDate(bin.end)}`,
    axisLabel: formatShortDate(bin.start),
    value: bin.value,
  }))
})

// Days without data (null) are skipped, not counted as zero.
function rollingAverage(values: (number | null)[], window: number): (number | null)[] {
  return values.map((_, i) => {
    const present = values.slice(Math.max(0, i - window + 1), i + 1).filter((v): v is number => v !== null)
    if (present.length === 0) return null
    return present.reduce((sum, v) => sum + v, 0) / present.length
  })
}

const rollingAverageWindow = computed(() => (isWeekly.value ? 4 : 7))
const rollingAverageName = computed(() => (isWeekly.value ? '4-week avg' : '7-day avg'))
const rollingAverageValues = computed(() =>
  rollingAverage(points.value.map((p) => p.value), rollingAverageWindow.value),
)

const option = computed<EChartsOption>(() => ({
  tooltip: valueTooltip(props.signal),
  legend: {
    data: [
      {
        name: props.signal.name,
        itemStyle: props.chartType === 'line' ? { opacity: 0 } : undefined, // hide legend dot
      },
      ...(props.showAverage ? [{ name: rollingAverageName.value, itemStyle: { opacity: 0 } }] : []),
    ],
    bottom: 0,
    left: 'center',
    textStyle: { color: chartColors.axisLabel },
  },
  grid: { left: 0, right: 16, top: 16, bottom: 32, outerBoundsMode: 'same', outerBoundsContain: 'axisLabel' },
  xAxis: categoryAxis(points.value.map((p) => p.label), (index) => points.value[index].axisLabel),
  yAxis: valueYAxis(props.signal, points.value.map((p) => p.value)),
  series: [
    {
      name: props.signal.name,
      type: props.chartType,
      data: points.value.map((p) => p.value),
      barMaxWidth: 24,
      itemStyle: props.chartType === 'bar' ? { color: signalColor(props.signal), borderRadius: [8, 8, 0, 0] } : { color: signalColor(props.signal) },
      lineStyle: props.chartType === 'line' ? { width: 2, color: signalColor(props.signal) } : undefined,
      areaStyle: props.chartType === 'line' ? { color: signalColor(props.signal), opacity: 0.1 } : undefined,
      symbol: props.chartType === 'line' ? 'circle' : 'none',
      symbolSize: 8,
      showSymbol: false,
    },
    ...(props.showAverage
      ? [
        {
          name: rollingAverageName.value,
          type: 'line' as const,
          data: rollingAverageValues.value,
          symbol: 'none',
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
