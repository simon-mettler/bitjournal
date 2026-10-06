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
import type {
  WidgetAggregation,
  WidgetChartType,
  WidgetTimeframe,
  WidgetType,
} from '@/modules/analytics/types'
import type { WidgetFormState } from '@/modules/analytics/widgetFormState'
import {
  WIDGET_TIMEFRAME_LABELS,
  earlierQuarterOptions,
  earlierYearOptions,
} from '@/modules/analytics/format'
import { useFormValidation } from '@/shared/lib/useFormValidation'
import { required, maxLength, when } from '@/shared/lib/validators'

const form = defineModel<WidgetFormState>({ required: true })

const signals = ref<Signal[]>([])

const selectedSignal = computed(() => signals.value.find((s) => s.id === form.value.signalId))
const isTimeseries = computed(() => form.value.type === 'timeseries')

const typeOptions: { value: WidgetType; label: string }[] = [
  { value: 'value', label: 'Value' },
  { value: 'timeseries', label: 'Over time' },
]
const aggregationOptions: { value: WidgetAggregation; label: string }[] = [
  { value: 'total', label: 'Total' },
  { value: 'average', label: 'Average' },
]
const chartTypeOptions: { value: WidgetChartType; label: string }[] = [
  { value: 'bar', label: 'Bar' },
  { value: 'line', label: 'Line' },
]
const averageOptions = [
  { value: 'on' as const, label: 'Show' },
  { value: 'off' as const, label: 'Hide' },
]
const quarterOptions = earlierQuarterOptions()
const yearOptions = earlierYearOptions()

// a single day has nothing to plot over time
const SINGLE_DAY_TIMEFRAMES: WidgetTimeframe[] = ['today', 'yesterday']
const timeframeOptions = computed(() =>
  Object.entries(WIDGET_TIMEFRAME_LABELS)
    .filter(
      ([value]) => !isTimeseries.value || !SINGLE_DAY_TIMEFRAMES.includes(value as WidgetTimeframe),
    )
    .map(([value, label]) => ({ value, label })),
)

watch(isTimeseries, (timeseries) => {
  if (timeseries && SINGLE_DAY_TIMEFRAMES.includes(form.value.timeframe)) {
    form.value.timeframe = 'this_week'
  }
})

const timeframeModel = computed({
  get: () => form.value.timeframe,
  set: (value: string) => {
    form.value.timeframe = value as WidgetTimeframe
    form.value.periodStart = undefined
  },
})

const averageModel = computed({
  get: () => (form.value.showAverage ? 'on' : 'off'),
  set: (value: 'on' | 'off') => (form.value.showAverage = value === 'on'),
})

const needsPeriodStart = () => form.value.timeframe === 'quarter' || form.value.timeframe === 'year'
const needsDays = () => form.value.timeframe === 'last_days'

const { errors, validateField, validateAll } = useFormValidation(
  {
    title: () => form.value.title,
    signal: () => form.value.signalId,
    periodStart: () => form.value.periodStart,
    days: () => form.value.days,
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
watch(
  () => form.value.signalId,
  (id) => {
    if (form.value.title.trim()) return
    form.value.title = signals.value.find((s) => s.id === id)?.name ?? ''
  },
)

onMounted(async () => {
  const { data } = await getSignals()
  signals.value = data
})

defineExpose({ validateAll, errors })
</script>

<template>
  <div class="form">
    <div class="field">
      <span class="label">Widget type</span>
      <ToggleGroup v-model="form.type" :options="typeOptions" class="toggle" />
    </div>

    <div class="field">
      <span class="label">Signal</span>
      <SignalPickerDialog :multiple="false" @add="([signal]) => (form.signalId = signal.id)">
        <template #trigger>
          <button type="button" class="signal-trigger" :class="{ placeholder: !selectedSignal }">
            <span class="signal-trigger-value">{{
              selectedSignal?.name ?? 'Select signal...'
            }}</span>
            <ChevronDown />
          </button>
        </template>
      </SignalPickerDialog>
      <p v-if="errors['signal']" class="error-text">{{ errors['signal'] }}</p>
    </div>

    <InputText
      v-model="form.title"
      label="Title"
      placeholder=""
      :error="errors['title']"
      @blur="validateField('title')"
    />

    <div v-if="!isTimeseries" class="field">
      <span class="label">Display</span>
      <ToggleGroup v-model="form.aggregation" :options="aggregationOptions" class="toggle" />
    </div>

    <template v-else>
      <div class="field">
        <span class="label">Chart type</span>
        <ToggleGroup v-model="form.chartType" :options="chartTypeOptions" class="toggle" />
      </div>
      <div class="field">
        <span class="label">Average line</span>
        <ToggleGroup v-model="averageModel" :options="averageOptions" class="toggle" />
      </div>
    </template>

    <Select v-model="timeframeModel" label="Timeframe" :options="timeframeOptions" />

    <Select
      v-if="form.timeframe === 'quarter'"
      v-model="form.periodStart"
      label="Quarter"
      :options="quarterOptions"
      placeholder="Select quarter..."
      :error="errors['periodStart']"
    />
    <Select
      v-if="form.timeframe === 'year'"
      v-model="form.periodStart"
      label="Year"
      :options="yearOptions"
      placeholder="Select year..."
      :error="errors['periodStart']"
    />
    <InputNumber
      v-if="form.timeframe === 'last_days'"
      v-model="form.days"
      label="Days back (including today)"
      :min="1"
      :step="1"
      :error="errors['days']"
      @blur="validateField('days')"
    />
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

.toggle {
  align-self: flex-start;
}
</style>
