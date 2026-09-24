<script setup lang="ts">
import { computed } from 'vue'
import Chart from '@/shared/ui/components/Chart.vue'
import {
  formatStatValue,
  formatDurationAxisLabel,
  durationAxisScale,
} from '@/modules/analytics/format'
import { tooltipBesidePointer } from '@/modules/analytics/tooltipPosition'
import { chartColors, signalColor } from '@/modules/analytics/chartColors'
import type { EChartsOption } from 'echarts'
import type { Signal } from '@/modules/signals/types'
import type { SignalStatsDayOfWeekPoint } from '@/modules/analytics/types'

const DAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

const props = defineProps<{
  signal: Signal
  dayOfWeek: SignalStatsDayOfWeekPoint[]
}>()

const values = computed(() => {
  const byDow = new Map(props.dayOfWeek.map((p) => [p.dow, p.value]))
  return DAY_LABELS.map((_, dow) => byDow.get(dow) ?? null)
})

const durationScale = computed(() => {
  if (props.signal.type !== 'duration') return null
  const max = Math.max(0, ...values.value.map((v) => v ?? 0))
  return durationAxisScale(max)
})

const option = computed<EChartsOption>(() => ({
  tooltip: {
    trigger: 'axis',
    position: tooltipBesidePointer,
    valueFormatter: (value) =>
      value == null || value === '-' ? '-' : formatStatValue(props.signal, Number(value)),
    backgroundColor: chartColors.tooltipBackground,
    borderWidth: 0,
    borderRadius: 8,
    padding: [6, 10],
    textStyle: { color: chartColors.tooltipText, fontSize: 12 },
  },
  grid: { left: 0, right: 16, top: 16, bottom: 0, outerBoundsMode: 'same', outerBoundsContain: 'axisLabel' },
  xAxis: {
    type: 'category',
    data: DAY_LABELS,
    axisLine: { lineStyle: { color: chartColors.gridLine } },
    axisLabel: { color: chartColors.axisLabel },
    axisTick: { show: false },
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: chartColors.gridLine } },
    axisLabel: {
      color: chartColors.axisLabel,
      formatter: durationScale.value ? (value: number) => formatDurationAxisLabel(value) : undefined,
    },
    max: durationScale.value?.max,
    interval: durationScale.value?.interval,
  },
  series: [
    {
      name: props.signal.name,
      type: 'bar',
      data: values.value,
      barMaxWidth: 24,
      itemStyle: { color: signalColor(props.signal), borderRadius: [8, 8, 0, 0] },
    },
  ],
}))
</script>

<template>
  <Chart :option="option" />
</template>
