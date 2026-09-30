<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { ChevronDown } from '@lucide/vue'
import InputText from '@/shared/ui/components/InputText.vue'
import InputNumber from '@/shared/ui/components/InputNumber.vue'
import Select from '@/shared/ui/components/Select.vue'
import ToggleGroup from '@/shared/ui/components/ToggleGroup.vue'
import SignalPickerDialog from '@/modules/signals/components/SignalPickerDialog.vue'
import { getSignals } from '@/modules/signals/api'
import type { Signal } from '@/modules/signals/types'
import type { WidgetAggregation, WidgetTimeframe } from '@/modules/analytics/types'
import {
  WIDGET_TIMEFRAME_LABELS,
  earlierQuarterOptions,
  earlierYearOptions,
} from '@/modules/analytics/format'
import { useFormValidation } from '@/shared/lib/useFormValidation'
import { required, maxLength, when } from '@/shared/lib/validators'

const title = defineModel<string>('title', { required: true })
const signalId = defineModel<string>('signalId')
const aggregation = defineModel<WidgetAggregation>('aggregation', { required: true })
const timeframe = defineModel<WidgetTimeframe>('timeframe', { required: true })
const periodStart = defineModel<string>('periodStart')
const days = defineModel<number>('days')

const signals = ref<Signal[]>([])

const selectedSignal = computed(() => signals.value.find((s) => s.id === signalId.value))
const timeframeOptions = Object.entries(WIDGET_TIMEFRAME_LABELS).map(([value, label]) => ({
  value,
  label,
}))
const aggregationOptions: { value: WidgetAggregation; label: string }[] = [
  { value: 'total', label: 'Total' },
  { value: 'average', label: 'Average' },
]
const quarterOptions = earlierQuarterOptions()
const yearOptions = earlierYearOptions()

const timeframeModel = computed({
  get: () => timeframe.value,
  set: (value: string) => {
    timeframe.value = value as WidgetTimeframe
    periodStart.value = undefined
  },
})

const needsPeriodStart = () => timeframe.value === 'quarter' || timeframe.value === 'year'
const needsDays = () => timeframe.value === 'last_days'

const { errors, validateField, validateAll } = useFormValidation(
  {
    title: () => title.value,
    signal: () => signalId.value,
    periodStart: () => periodStart.value,
    days: () => days.value,
  },
  {
    title: [required('Title is required'), maxLength(100, '100 characters or fewer')],
    signal: [required('Select a signal')],
    periodStart: [when(needsPeriodStart, required('Select a period'))],
    days: [
      when(needsDays, required('Enter a number of days')),
      when(needsDays, (v) => v >= 1 || 'At least 1 day'),
    ],
  },
)

// add signal name as title if no title is set
watch(signalId, (id) => {
  if (title.value.trim()) return
  title.value = signals.value.find((s) => s.id === id)?.name ?? ''
})

onMounted(async () => {
  const { data } = await getSignals()
  signals.value = data
})

defineExpose({ validateAll, errors })
</script>

<template>
  <div class="form">
    <div class="field">
      <span class="label">Signal</span>
      <SignalPickerDialog :multiple="false" @add="([signal]) => (signalId = signal.id)">
        <template #trigger>
          <button type="button" class="signal-trigger" :class="{ placeholder: !selectedSignal }">
            <span class="signal-trigger-value">{{ selectedSignal?.name ?? 'Select signal...' }}</span>
            <ChevronDown />
          </button>
        </template>
      </SignalPickerDialog>
      <p v-if="errors['signal']" class="error-text">{{ errors['signal'] }}</p>
    </div>

    <InputText v-model="title" label="Title" placeholder="" @blur="validateField('title')" :error="errors['title']" />

    <div class="field">
      <span class="label">Display</span>
      <ToggleGroup v-model="aggregation" :options="aggregationOptions" class="aggregation-toggle" />
    </div>

    <Select v-model="timeframeModel" label="Timeframe" :options="timeframeOptions" />

    <Select v-if="timeframe === 'quarter'" v-model="periodStart" label="Quarter" :options="quarterOptions"
      placeholder="Select quarter..." :error="errors['periodStart']" />
    <Select v-if="timeframe === 'year'" v-model="periodStart" label="Year" :options="yearOptions"
      placeholder="Select year..." :error="errors['periodStart']" />
    <InputNumber v-if="timeframe === 'last_days'" v-model="days" label="Days back (including today)" :min="1" :step="1"
      :error="errors['days']" @blur="validateField('days')" />
  </div>
</template>

<style scoped>
.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field {
  display: flex;
  flex-direction: column;
}

.label {
  font-size: var(--font-size-sm);
  padding-left: 8px;
  margin-bottom: 6px;
  color: var(--input-color-label);
}

.signal-trigger {
  all: unset;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  height: var(--input-height);
  padding: 0 10px;
  font-size: var(--font-size-base);
  color: var(--input-color-text);
  background-color: var(--input-color-background);
  border: var(--input-border);
  border-radius: var(--input-radius);
  box-shadow: var(--shadow-fields);
  cursor: pointer;
}

.signal-trigger:focus-visible {
  box-shadow: var(--input-shadow-focus);
  border: var(--input-border-focus);
}

.signal-trigger.placeholder {
  color: var(--input-color-placeholder);
}

.signal-trigger-value {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.signal-trigger :deep(svg) {
  flex-shrink: 0;
  color: var(--color-surface-medium);
}

.error-text {
  margin: 0;
  padding-left: 8px;
  font-size: var(--font-size-sm);
  color: var(--color-danger);
}

.aggregation-toggle {
  align-self: flex-start;
}
</style>
