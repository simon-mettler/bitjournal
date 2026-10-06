<script setup lang="ts">
import { computed } from 'vue'
import Chart from '@/shared/ui/components/Chart.vue'
import { signalColor } from '@/modules/analytics/chartColors'
import {
  DAY_LABELS,
  categoryAxis,
  valueTooltip,
  valueYAxis,
} from '@/modules/analytics/chartOptions'
import type { EChartsOption } from 'echarts'
import type { Signal } from '@/modules/signals/types'
import type { SignalStatsDayOfWeekPoint } from '@/modules/analytics/types'

const props = defineProps<{
  signal: Signal
  dayOfWeek: SignalStatsDayOfWeekPoint[]
}>()

const values = computed(() => {
  const byDow = new Map(props.dayOfWeek.map((p) => [p.dow, p.value]))
  return DAY_LABELS.map((_, dow) => byDow.get(dow) ?? null)
})

const option = computed<EChartsOption>(() => ({
  tooltip: valueTooltip(props.signal),
  grid: {
    left: 0,
    right: 16,
    top: 16,
    bottom: 0,
    outerBoundsMode: 'same',
    outerBoundsContain: 'axisLabel',
  },
  xAxis: categoryAxis(DAY_LABELS),
  yAxis: valueYAxis(props.signal, values.value),
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
