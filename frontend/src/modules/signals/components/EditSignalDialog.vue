<script setup lang="ts">
import { ref, watch } from 'vue'
import Modal from '@/shared/ui/components/Dialog.vue'
import Button from '@/shared/ui/components/Button.vue'
import SignalForm from '@/modules/signals/components/SignalForm.vue'
import { DialogClose } from 'reka-ui'
import { updateSignal, type CreateSignalPayload } from '@/modules/signals/api'
import type { Signal } from '@/modules/signals/types'

const props = defineProps<{ signal: Signal }>()
const emit = defineEmits<{ updated: [signal: Signal] }>()

const open = ref(false)
const signalName = ref(props.signal.name)
const color = ref(props.signal.color ?? '')
const icon = ref(props.signal.icon ?? '')
const signalUnit = ref(props.signal.value_config?.unit ?? '')
const selectedSignalType = ref<CreateSignalPayload['type']>(props.signal.type)
const selectedSummaryMethod = ref<CreateSignalPayload['summary_method']>(props.signal.summary_method)
const minValue = ref(props.signal.range_config?.min_value)
const maxValue = ref(props.signal.range_config?.max_value)
const minLabel = ref(props.signal.range_config?.min_label ?? '')
const maxLabel = ref(props.signal.range_config?.max_label ?? '')
const errors = ref<Record<string, string[]>>({})
const submitting = ref(false)

watch(open, (isOpen) => {
  if (!isOpen) return
  signalName.value = props.signal.name
  color.value = props.signal.color ?? ''
  icon.value = props.signal.icon ?? ''
  signalUnit.value = props.signal.value_config?.unit ?? ''
  selectedSummaryMethod.value = props.signal.summary_method
  minValue.value = props.signal.range_config?.min_value
  maxValue.value = props.signal.range_config?.max_value
  minLabel.value = props.signal.range_config?.min_label ?? ''
  maxLabel.value = props.signal.range_config?.max_label ?? ''
  errors.value = {}
})

async function submitSignal() {
  if (!signalName.value) return

  const payload: CreateSignalPayload = {
    name: signalName.value,
    type: selectedSignalType.value,
    summary_method: selectedSummaryMethod.value,
    color: color.value,
    icon: icon.value,
  }

  if (selectedSignalType.value === 'value') {
    payload.value_config = { unit: signalUnit.value }
  }
  if (selectedSignalType.value === 'range' && minValue.value !== undefined && maxValue.value !== undefined) {
    payload.range_config = {
      min_value: minValue.value,
      max_value: maxValue.value,
      min_label: minLabel.value,
      max_label: maxLabel.value,
    }
  }

  submitting.value = true
  errors.value = {}
  try {
    const { data } = await updateSignal(props.signal.id, payload)
    emit('updated', data)
    open.value = false
  } catch (err) {
    console.error(err)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <Modal v-model:open="open" title="Edit signal">
    <template #trigger>
      <slot name="trigger">
        <Button variant="secondary">Edit</Button>
      </slot>
    </template>

    <SignalForm v-model:name="signalName" v-model:color="color" v-model:icon="icon" v-model:unit="signalUnit"
      v-model:type="selectedSignalType" v-model:summary-method="selectedSummaryMethod" v-model:min-value="minValue"
      v-model:max-value="maxValue" v-model:min-label="minLabel" v-model:max-label="maxLabel" :errors="errors"
      lock-type />

    <template #footer>
      <DialogClose as-child>
        <Button variant="secondary">Cancel</Button>
      </DialogClose>
      <Button :disabled="submitting" variant="primary" @click="submitSignal()">
        {{ submitting ? 'Saving...' : 'Save changes' }}
      </Button>
    </template>
  </Modal>
</template>
