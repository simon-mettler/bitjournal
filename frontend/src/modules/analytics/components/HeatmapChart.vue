<script setup lang="ts">
import { computed } from 'vue'
import Chart from '@/shared/ui/components/Chart.vue'
import { formatStatValue } from '@/modules/analytics/format'
import { HEATMAP_EMPTY_COLOR, HEATMAP_SCALE_COLORS } from '@/modules/analytics/heatmapScale'
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

// Scale spans only the bins with entries (not 0 to max)
const scale = computed(() => {
  const values = props.heatmap.map((p) => p.value)
  if (values.length === 0) return { min: 0, max: 1 }
  const min = Math.min(...values)
  const max = Math.max(...values)
  if (min < max) return { min, max }
  return { min: max - (Math.abs(max) || 1), max }
})

const emptyBinValue = computed(() => scale.value.min - 1)

const gridData = computed(() => {
  const data: [number, number, number][] = []
  for (let dow = 0; dow < 7; dow++) {
    for (let hour = 0; hour < 24; hour++) {
      const bin = byBin.value.get(`${dow}-${hour}`)
      data.push([hour, dow, bin ? bin.value : emptyBinValue.value])
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
    confine: true,
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
  grid: { left: 40, right: 4, top: 4, bottom: 80 },
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
    type: 'continuous',
    dimension: 2,
    unboundedRange: false,
    calculable: true,
    orient: 'horizontal',
    left: 'center',
    bottom: 0,
    itemWidth: 12,
    itemHeight: 160,
    text: ['More', 'Less'],
    textGap: 12,
    textStyle: { color: HOUR_LABEL, fontSize: 12 },
    formatter: (value: unknown) => formatStatValue(props.signal, Number(value)),
    min: scale.value.min,
    max: scale.value.max,
    inRange: { color: [...HEATMAP_SCALE_COLORS] },
    outOfRange: { color: HEATMAP_EMPTY_COLOR },
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
  <Chart :option="option" :height="244" />
</template>
