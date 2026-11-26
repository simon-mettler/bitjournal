<script setup lang="ts">
import { computed, watch } from 'vue'
import ToggleGroup from '@/shared/ui/components/ToggleGroup.vue'
import SettingField from '@/modules/analytics/components/settings/SettingField.vue'
import {
  availableCalculations,
  calculationHint,
  calculationOptions,
  defaultCalculation,
} from '@/modules/analytics/calculations'
import type { WidgetCalculation } from '@/modules/analytics/types'
import type { Signal } from '@/modules/signals/types'

const props = defineProps<{
  signal?: Signal
  chart?: boolean
}>()
const calculation = defineModel<WidgetCalculation>({ required: true })

const options = computed(() => calculationOptions(props.signal))

// not every signal offers every calculation
watch(
  () => props.signal,
  (signal) => {
    if (signal && !availableCalculations(signal).includes(calculation.value)) {
      calculation.value = defaultCalculation(signal)
    }
  },
)
</script>

<template>
  <SettingField label="Calculation">
    <ToggleGroup v-model="calculation" :options="options" />
    <p class="hint">
      {{ calculationHint(calculation, signal) }}
    </p>
  </SettingField>
</template>

<style scoped>
.hint {
  margin: 6px 0 0;
  padding-left: 8px;
  font-size: var(--font-size-sm);
  color: var(--input-color-label);
}
</style>
