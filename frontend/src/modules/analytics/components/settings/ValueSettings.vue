<script setup lang="ts">
import { computed, watch } from 'vue'
import ToggleGroup from '@/shared/ui/components/ToggleGroup.vue'
import SettingField from '@/modules/analytics/components/settings/SettingField.vue'
import { aggregationOptions } from '@/modules/analytics/format'
import type { ValueWidgetConfig } from '@/modules/analytics/types'
import type { Signal } from '@/modules/signals/types'

const props = defineProps<{ signal?: Signal }>()
const config = defineModel<ValueWidgetConfig>({ required: true })

const options = computed(() => aggregationOptions(props.signal))

// not every signal offers every option
watch(
  () => props.signal,
  (signal) => {
    if (signal && !options.value.some((o) => o.value === config.value.aggregation)) {
      config.value.aggregation = 'average'
    }
  },
)
</script>

<template>
  <SettingField label="Display">
    <ToggleGroup v-model="config.aggregation" :options="options" />
  </SettingField>
</template>
