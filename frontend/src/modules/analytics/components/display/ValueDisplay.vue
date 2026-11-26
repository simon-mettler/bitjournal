<script setup lang="ts">
import { computed } from 'vue'
import StatValue from '@/modules/analytics/components/StatValue.vue'
import WidgetMeta from '@/modules/analytics/components/WidgetMeta.vue'
import { CALCULATION_LABELS, showsEmptyDaysAsZero } from '@/modules/analytics/calculations'
import { formatStatParts, formatWidgetTimeframe, type StatPart } from '@/modules/analytics/format'
import type { AnalyticsWidgetOf, AnalyticsWidgetValue } from '@/modules/analytics/types'

const props = defineProps<{
  widget: AnalyticsWidgetOf<'value'>
  data?: AnalyticsWidgetValue // undefined while loading
}>()

const hasNoEntries = computed(
  () =>
    props.data?.count === 0 &&
    !(
      showsEmptyDaysAsZero(props.widget.signal, props.widget.config.calculation) &&
      props.data.value !== null
    ),
)

const parts = computed<StatPart[]>(() => {
  if (!props.data) return [{ text: '…' }]
  if (hasNoEntries.value || props.data.value === null) return [{ text: '–' }]
  return formatStatParts(props.widget.signal, props.data.value)
})

const label = computed(() =>
  hasNoEntries.value ? 'No entries' : CALCULATION_LABELS[props.widget.config.calculation],
)
</script>

<template>
  <StatValue class="widget-value" :style="{ color: widget.signal.color }" :parts="parts" />
  <WidgetMeta>{{ label }} · {{ formatWidgetTimeframe(widget) }}</WidgetMeta>
</template>

<style scoped>
.widget-value {
  font-size: var(--font-size-h1);
  font-weight: var(--font-weight-bold);
}
</style>
