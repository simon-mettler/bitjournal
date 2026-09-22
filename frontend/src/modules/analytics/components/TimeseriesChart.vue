<script setup lang="ts">
import { computed } from 'vue'
import Chart from '@/shared/ui/components/Chart.vue'
import { formatStatValue } from '@/modules/analytics/format'
import type { EChartsOption } from 'echarts'
import type { Signal } from '@/modules/signals/types'
import type { SignalStatsTimeseriesPoint } from '@/modules/analytics/types'

const PRIMARY = '#0F7A6C'
const TREND = '#9AA1A9'
const GRID_LINE = '#ECEEF1'
const TOOLTIP_BG = '#1F2937'

const props = defineProps<{
  signal: Signal
  timeseries: SignalStatsTimeseriesPoint[]
  chartType: 'bar' | 'line'
}>()

// Days without data (null) are skipped, not counted as zero.
function rollingAverage(values: (number | null)[], window: number): (number | null)[] {
  return values.map((_, i) => {
    const present = values.slice(Math.max(0, i - window + 1), i + 1).filter((v): v is number => v !== null)
    if (present.length === 0) return null
    return present.reduce((sum, v) => sum + v, 0) / present.length
  })
}

const rollingAverageValues = computed(() => rollingAverage(props.timeseries.map((p) => p.value), 7))

const option = computed<EChartsOption>(() => ({
  tooltip: {
    trigger: 'axis',
    valueFormatter: (value) =>
      value == null || value === '-' ? '-' : formatStatValue(props.signal, Number(value)),
    backgroundColor: TOOLTIP_BG,
    borderWidth: 0,
    borderRadius: 8,
    padding: [6, 10],
    textStyle: { color: '#ffffff', fontSize: 12 },
  },
  legend: {
    top: 0,
    right: 0,
    textStyle: { color: TREND },
  },
  grid: { left: 48, right: 16, top: 36, bottom: 28 },
  xAxis: {
    type: 'category',
    data: props.timeseries.map((p) => p.date),
    axisLine: { lineStyle: { color: GRID_LINE } },
    axisLabel: { color: TREND },
    axisTick: { show: false },
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: GRID_LINE } },
    axisLabel: { color: TREND },
  },
  series: [
    {
      name: props.signal.name,
      type: props.chartType,
      data: props.timeseries.map((p) => p.value),
      barMaxWidth: 24,
      itemStyle: props.chartType === 'bar' ? { color: PRIMARY, borderRadius: [8, 8, 0, 0] } : { color: PRIMARY },
      lineStyle: props.chartType === 'line' ? { width: 2, color: PRIMARY } : undefined,
      areaStyle: props.chartType === 'line' ? { color: PRIMARY, opacity: 0.1 } : undefined,
      symbol: props.chartType === 'line' ? 'circle' : 'none',
      symbolSize: 8,
    },
    {
      name: '7-day avg',
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
