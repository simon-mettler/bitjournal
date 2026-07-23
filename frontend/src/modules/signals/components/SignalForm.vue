<script setup lang="ts">
import Select from '@/shared/ui/components/Select.vue'
import ColorPicker from '@/shared/ui/components/ColorPicker.vue'
import IconPicker from '@/shared/ui/components/IconPicker.vue'
import InputText from '@/shared/ui/components/InputText.vue'
import InputNumber from '@/shared/ui/components/InputNumber.vue'
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
</script>

<template>
  <div class="form-name">
    <InputText v-model="signalName" label="Name" placeholder="" />
    <IconPicker v-model="icon" />
    <ColorPicker v-model="color" />
  </div>

  <Select v-model="selectedSummaryMethod" :options="summaryMethod" label="Summary method"
    placeholder="Summary method" />
  <Select v-model="selectedSignalType" :options="signalType" label="Signal type" placeholder="Choose a type"
    :disabled="lockType" />

  <InputText v-if="selectedSignalType === 'value'" v-model="signalUnit" label="Unit" placeholder="Unit" />
  <template v-if="selectedSignalType === 'range'">
    <InputNumber v-model.number="minValue" label="Min value" />
    <InputText v-model="minLabel" label="Min label" />
    <InputNumber v-model.number="maxValue" label="Max value" />
    <InputText v-model="maxLabel" label="Max label" />
  </template>

  <p v-if="errors.name" class="error">{{ errors.name[0] }}</p>
  <p v-if="errors.value_config" class="error">{{ errors.value_config }}</p>
  <p v-if="errors.range_config" class="error">{{ errors.range_config }}</p>
</template>

<style scoped>
.form-name {
  display: flex;
  align-items: flex-end;
  gap: 8px;
}
</style>
