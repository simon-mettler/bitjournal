<script setup lang="ts">
import { computed } from 'vue'
import ToggleGroup from '@/shared/ui/components/ToggleGroup.vue'
import SettingField from '@/modules/analytics/components/settings/SettingField.vue'
import type { TimeseriesWidgetConfig, WidgetChartType } from '@/modules/analytics/types'

const config = defineModel<TimeseriesWidgetConfig>({ required: true })

const chartTypeOptions: { value: WidgetChartType; label: string }[] = [
  { value: 'bar', label: 'Bar' },
  { value: 'line', label: 'Line' },
]
const averageOptions = [
  { value: 'on' as const, label: 'Show' },
  { value: 'off' as const, label: 'Hide' },
]

const averageModel = computed({
  get: () => (config.value.show_average ? 'on' : 'off'),
  set: (value: 'on' | 'off') => (config.value.show_average = value === 'on'),
})
</script>

<template>
  <SettingField label="Chart type">
    <ToggleGroup v-model="config.chart_type" :options="chartTypeOptions" />
  </SettingField>
  <SettingField label="Average line">
    <ToggleGroup v-model="averageModel" :options="averageOptions" />
  </SettingField>
</template>
