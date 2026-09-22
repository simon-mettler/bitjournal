<script setup lang="ts">
import { computed } from 'vue'
import Chart from '@/shared/ui/components/Chart.vue'
import { formatStatValue } from '@/modules/analytics/format'
import { HEATMAP_COLORS, heatmapLevel } from '@/modules/analytics/heatmapScale'
import type { EChartsOption } from 'echarts'
import type { Signal } from '@/modules/signals/types'
import type { SignalStatsHeatmapPoint } from '@/modules/analytics/types'

// TODO: get color tokens
const SURFACE = '#ffffff'
const DAY_LABEL = '#6B7280'
const HOUR_LABEL = '#9AA1A9'
const TOOLTIP_BG = '#1F2937'
const MONO = 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace'

const HOURS = Array.from({ length: 24 }, (_, h) => String(h))
const DAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

const props = defineProps<{
  signal: Signal
  heatmap: SignalStatsHeatmapPoint[]
}>()

const byBin = computed(() => new Map(props.heatmap.map((p) => [`${p.dow}-${p.hour}`, p])))

const maxValue = computed(() => Math.max(0, ...props.heatmap.map((p) => p.value)))

const gridData = computed(() => {
  const data: [number, number, number][] = []
  for (let dow = 0; dow < 7; dow++) {
    for (let hour = 0; hour < 24; hour++) {
      const bin = byBin.value.get(`${dow}-${hour}`)
      data.push([hour, dow, bin ? heatmapLevel(bin.value, maxValue.value) : 0])
    }
  }
  return data
})

function tooltipText(dow: number, hour: number): string {
  const label = `${DAY_LABELS[dow]} ${hour}:00`
  const bin = byBin.value.get(`${dow}-${hour}`)
  if (!bin) return `${label} - no entries`

  const entries = `${bin.count} ${bin.count === 1 ? 'entry' : 'entries'}`
  // For tallies the value is the entry count, so don't repeat it.
  if (props.signal.type === 'tally' && props.signal.summary_method === 'total') {
    return `${label} - ${entries}`
  }
  const prefix = props.signal.summary_method === 'average' ? 'avg ' : ''
  return `${label} - ${prefix}${formatStatValue(props.signal, bin.value)} (${entries})`
}

const option = computed<EChartsOption>(() => ({
  tooltip: {
    position: 'top',
    formatter: (params: any) => {
      const [hour, dow] = params.value as [number, number, number]
      return tooltipText(dow, hour)
    },
    backgroundColor: TOOLTIP_BG,
    borderWidth: 0,
    borderRadius: 8,
    padding: [6, 10],
    textStyle: { color: '#ffffff', fontSize: 12 },
  },
  grid: { left: 40, right: 4, top: 4, bottom: 26 },
  xAxis: {
    type: 'category',
    data: HOURS,
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: {
      color: HOUR_LABEL,
      interval: 3,
      fontFamily: MONO,
      fontSize: 11,
      formatter: (hour: string) => `${hour}h`,
    },
    splitArea: {
      show: true,
      areaStyle: {
        color: [SURFACE, SURFACE],
      },
    },
  },
  yAxis: {
    type: 'category',
    data: DAY_LABELS,
    inverse: true,
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: {
      margin: 10,
      color: DAY_LABEL,
      fontWeight: 'bold',
      fontSize: 12,
    },
    splitArea: {
      show: true,
      areaStyle: {
        color: [SURFACE, SURFACE],
      },
    },
  },
  visualMap: {
    type: 'piecewise',
    show: false,
    dimension: 2,
    pieces: HEATMAP_COLORS.map((color, level) => ({ value: level, color })),
  },
  series: [
    {
      name: 'Entries',
      type: 'heatmap',
      data: gridData.value,
      itemStyle: {
        borderColor: SURFACE,
        borderWidth: 3,
        borderRadius: 6,
      },
      emphasis: {
        itemStyle: {
          borderWidth: 0,
          color: 'inherit',
          shadowColor: 'rgba(15, 142, 128, 0.5)',
        },
      },
    },
  ],
}))
</script>

<template>
  <Chart :option="option" :height="190" />
</template>
