<script setup lang="ts">
import { computed } from 'vue'
import TimeseriesChart from '@/modules/analytics/components/TimeseriesChart.vue'
import WidgetMeta from '@/modules/analytics/components/WidgetMeta.vue'
import { CALCULATION_LABELS, showsEmptyDaysAsZero } from '@/modules/analytics/calculations'
import { formatWidgetTimeframe } from '@/modules/analytics/format'
import type { AnalyticsWidgetOf, AnalyticsWidgetValue } from '@/modules/analytics/types'

const props = defineProps<{
  widget: AnalyticsWidgetOf<'timeseries'>
  data?: AnalyticsWidgetValue // undefined while loading
}>()

const hasNoEntries = computed(
  () =>
    props.data?.count === 0 &&
    !(
      showsEmptyDaysAsZero(props.widget.signal, props.widget.config.calculation) &&
      props.data.timeseries?.points.some((point) => point.value !== null)
    ),
)
</script>

<template>
  <p v-if="hasNoEntries" class="widget-chart-placeholder">No entries in this period</p>
  <p v-else-if="!data?.timeseries" class="widget-chart-placeholder">…</p>
  <TimeseriesChart
    v-else
    :signal="widget.signal"
    :timeseries="data.timeseries"
    :calculation="widget.config.calculation"
    :chart-type="widget.config.chart_type"
    :show-average="widget.config.show_average"
    :height="220"
  />
  <WidgetMeta>
    {{ CALCULATION_LABELS[widget.config.calculation] }} · {{ formatWidgetTimeframe(widget) }}
  </WidgetMeta>
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
