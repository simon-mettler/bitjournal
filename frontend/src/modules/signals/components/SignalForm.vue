<script setup lang="ts">
import Select from '@/shared/ui/components/Select.vue'
import ColorPicker from '@/shared/ui/components/ColorPicker.vue'
import IconPicker from '@/shared/ui/components/IconPicker.vue'
import InputText from '@/shared/ui/components/InputText.vue'
import InputNumber from '@/shared/ui/components/InputNumber.vue'
import { useFormValidation } from '@/shared/lib/useFormValidation'
import { required, maxLength, isLessThan, when, isMoreThan } from '@/shared/lib/validators'
import type { CreateSignalPayload } from '@/modules/signals/api'

const signalType = [
  { value: 'tally', label: 'Tally' },
  { value: 'range', label: 'Range' },
  { value: 'value', label: 'Value' },
  { value: 'duration', label: 'Duration' },
]
const summaryMethod = [
  { value: 'total', label: 'Total' },
  { value: 'average', label: 'Average' },
]

defineProps<{
  errors: Record<string, string[]>
  lockType?: boolean // true in edit mode
}>()

const signalName = defineModel<string>('name', { required: true })
const color = defineModel<string>('color', { required: true })
const icon = defineModel<string>('icon', { required: true })
const signalUnit = defineModel<string>('unit', { required: true })
const selectedSignalType = defineModel<CreateSignalPayload['type']>('type', { required: true })
const selectedSummaryMethod = defineModel<CreateSignalPayload['summary_method']>('summaryMethod', { required: true })
const minValue = defineModel<number>('minValue')
const maxValue = defineModel<number>('maxValue')
const minLabel = defineModel<string>('minLabel', { required: true })
const maxLabel = defineModel<string>('maxLabel', { required: true })

const isRange = () => selectedSignalType.value === 'range'
const isValue = () => selectedSignalType.value === 'value'

const { errors: validationErrors, validateField, validateAll } = useFormValidation(
  {
    name: () => signalName.value,
    minLabel: () => minLabel.value,
    maxLabel: () => maxLabel.value,
    minValue: () => minValue.value,
    maxValue: () => maxValue.value,
    signalUnit: () => signalUnit.value,
  },
  {
    name: [required('Name is required'), maxLength(50, '50 characters or fewer')],
    minLabel: [when(isRange, maxLength(50, '50 characters or fewer'))],
    maxLabel: [when(isRange, maxLength(50, '50 characters or fewer'))],
    minValue: [when(isRange, required('Min value is required')), when(isRange, isLessThan(() => maxValue.value, 'Must be less than max'))],
    maxValue: [when(isRange, required('Max value is required')), when(isRange, isMoreThan(() => minValue.value, 'Must be more than min'))],
    signalUnit: [when(isValue, maxLength(20, '20 characters or fewer'))],
  },
)

defineExpose({ validateAll, errors: validationErrors })
</script>

<template>
  <div class="form">
    <div class="form-name">
      <InputText v-model="signalName" label="Name" placeholder="" @blur="validateField('name')"
        :error="validationErrors['name']" />
      <IconPicker v-model="icon" />
      <ColorPicker v-model="color" />
    </div>

    <Select v-model="selectedSummaryMethod" :options="summaryMethod" label="Summary method"
      placeholder="Summary method" />
    <Select v-model="selectedSignalType" :options="signalType" label="Signal type" placeholder="Choose a type"
      :disabled="lockType" />

    <InputText v-if="selectedSignalType === 'value'" v-model="signalUnit" label="Unit" placeholder="Unit"
      @blur="validateField('signalUnit')" :error="validationErrors['signalUnit']" />
    <template v-if="selectedSignalType === 'range'">
      <div class="form-group">
        <InputNumber v-model.number="minValue" label="Min value" signToggle @blur="validateField('minValue')"
          :error="validationErrors['minValue']" />
        <InputText v-model="minLabel" label="Min label" @blur="validateField('minLabel')"
          :error="validationErrors['minLabel']" />
      </div>
      <div class="form-group">
        <InputNumber v-model.number="maxValue" label="Max value" @blur="validateField('maxValue')"
          :error="validationErrors['maxValue']" signToggle />
        <InputText v-model="maxLabel" label="Max label" @blur="validateField('maxLabel')"
          :error="validationErrors['maxLabel']" />
      </div>
    </template>
  </div>
</template>

<style scoped>
.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-name {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.form-group {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.form-group>* {
  flex: 1;
  min-width: 0;
}
</style>
