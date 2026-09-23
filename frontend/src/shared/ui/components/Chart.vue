<script setup lang="ts">
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, HeatmapChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, VisualMapComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import type { EChartsOption } from 'echarts'

use([CanvasRenderer, BarChart, LineChart, HeatmapChart, GridComponent, TooltipComponent, VisualMapComponent, LegendComponent])

defineProps<{
  option: EChartsOption
  height?: number
}>()
</script>

<template>
  <VChart class="chart" :style="height ? { height: `${height}px` } : undefined" :option="option" autoresize />
</template>

<style scoped>
.chart {
  width: 100%;
  height: 300px;
}
</style>
