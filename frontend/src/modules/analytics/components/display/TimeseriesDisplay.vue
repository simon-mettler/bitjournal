<script setup lang="ts">
import TimeseriesChart from '@/modules/analytics/components/TimeseriesChart.vue'
import WidgetMeta from '@/modules/analytics/components/WidgetMeta.vue'
import { formatWidgetTimeframe } from '@/modules/analytics/format'
import type { AnalyticsWidgetOf, AnalyticsWidgetValue } from '@/modules/analytics/types'

defineProps<{
  widget: AnalyticsWidgetOf<'timeseries'>
  data?: AnalyticsWidgetValue // undefined while loading
}>()
</script>

<template>
  <p v-if="data?.count === 0" class="widget-chart-placeholder">No entries in this period</p>
  <p v-else-if="!data?.timeseries" class="widget-chart-placeholder">…</p>
  <TimeseriesChart
    v-else
    :signal="widget.signal"
    :timeseries="data.timeseries"
    :chart-type="widget.config.chart_type"
    :show-average="widget.config.show_average"
    :height="220"
  />
  <WidgetMeta>{{ formatWidgetTimeframe(widget) }}</WidgetMeta>
</template>

<style scoped>
.widget-chart-placeholder {
  height: 220px;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--input-color-label);
}
</style>
