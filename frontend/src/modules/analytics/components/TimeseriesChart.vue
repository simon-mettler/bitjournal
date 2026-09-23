<script setup lang="ts">
import { computed } from 'vue'
import Chart from '@/shared/ui/components/Chart.vue'
import {
  formatStatValue,
  formatDurationAxisLabel,
  durationAxisScale,
} from '@/modules/analytics/format'
import { binTimeseriesByWeek, WEEKLY_BIN_TIMEFRAMES } from '@/modules/analytics/timeseriesBins'
import { tooltipBesidePointer } from '@/modules/analytics/tooltipPosition'
import type { EChartsOption } from 'echarts'
import type { Signal } from '@/modules/signals/types'
import type { SignalStatsTimeseriesPoint, Timeframe } from '@/modules/analytics/types'

const PRIMARY = '#0F7A6C'
const TREND = '#9AA1A9'
const GRID_LINE = '#ECEEF1'
const TOOLTIP_BG = '#1F2937'

const props = defineProps<{
  signal: Signal
  timeseries: SignalStatsTimeseriesPoint[]
  timeframe: Timeframe
  chartType: 'bar' | 'line'
}>()

const shortDateFormat = new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric' })

function formatShortDate(value: string): string {
  const [year, month, day] = value.split('-').map(Number)
  return shortDateFormat.format(new Date(year, month - 1, day))
}

const isWeekly = computed(() => WEEKLY_BIN_TIMEFRAMES.has(props.timeframe))

const points = computed(() => {
  if (!isWeekly.value) {
    return props.timeseries.map((p) => ({ label: p.date, axisLabel: p.date, value: p.value }))
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

const durationScale = computed(() => {
  if (props.signal.type !== 'duration') return null
  const max = Math.max(0, ...points.value.map((p) => p.value ?? 0))
  return durationAxisScale(max)
})

const option = computed<EChartsOption>(() => ({
  tooltip: {
    trigger: 'axis',
    position: tooltipBesidePointer,
    valueFormatter: (value) =>
      value == null || value === '-' ? '-' : formatStatValue(props.signal, Number(value)),
    backgroundColor: TOOLTIP_BG,
    borderWidth: 0,
    borderRadius: 8,
    padding: [6, 10],
    textStyle: { color: '#ffffff', fontSize: 12 },
  },
  legend: {
    data: [
      {
        name: props.signal.name,
        itemStyle: props.chartType === 'line' ? { opacity: 0 } : undefined, // hide legend dot
      },
      { name: rollingAverageName.value, itemStyle: { opacity: 0 } },
    ],
    bottom: 0,
    left: 'center',
    textStyle: { color: TREND },
  },
  grid: { left: 0, right: 16, top: 16, bottom: 32, outerBoundsMode: 'same', outerBoundsContain: 'axisLabel' },
  xAxis: {
    type: 'category',
    data: points.value.map((p) => p.label),
    axisLine: { lineStyle: { color: GRID_LINE } },
    axisLabel: { color: TREND, formatter: (_: string, index: number) => points.value[index].axisLabel },
    axisTick: { show: false },
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: GRID_LINE } },
    axisLabel: {
      color: TREND,
      formatter: durationScale.value ? (value: number) => formatDurationAxisLabel(value) : undefined,
    },
    max: durationScale.value?.max,
    interval: durationScale.value?.interval,
  },
  series: [
    {
      name: props.signal.name,
      type: props.chartType,
      data: points.value.map((p) => p.value),
      barMaxWidth: 24,
      itemStyle: props.chartType === 'bar' ? { color: PRIMARY, borderRadius: [8, 8, 0, 0] } : { color: PRIMARY },
      lineStyle: props.chartType === 'line' ? { width: 2, color: PRIMARY } : undefined,
      areaStyle: props.chartType === 'line' ? { color: PRIMARY, opacity: 0.1 } : undefined,
      symbol: props.chartType === 'line' ? 'circle' : 'none',
      symbolSize: 8,
      showSymbol: false,
    },
    {
      name: rollingAverageName.value,
      type: 'line',
      data: rollingAverageValues.value,
      symbol: 'none',
      lineStyle: { width: 2, color: TREND, type: 'dashed' },
    },
  ],
}))
</script>

<template>
  <Chart :option="option" />
</template>
