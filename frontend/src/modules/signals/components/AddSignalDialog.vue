<script setup lang="ts">
import { ref } from 'vue'
import Modal from '@/shared/ui/components/Dialog.vue'
import Button from '@/shared/ui/components/Button.vue'
import SignalForm from '@/modules/signals/components/SignalForm.vue'
import { DialogClose } from 'reka-ui'
import { createSignal, type CreateSignalPayload } from '@/modules/signals/api'
import type { Signal } from '@/modules/signals/types'
import { useToast } from '@/shared/lib/useToast'

const toast = useToast()
const emit = defineEmits<{ created: [signal: Signal] }>()

const open = ref(false)
const signalName = ref('')
const color = ref('#324245')
const icon = ref('')
const signalUnit = ref('')
const selectedSignalType = ref<CreateSignalPayload['type']>('tally')
const selectedSummaryMethod = ref<CreateSignalPayload['summary_method']>('total')
const minValue = ref<number>()
const maxValue = ref<number>()
const minLabel = ref('')
const maxLabel = ref('')
const errors = ref<Record<string, string[]>>({})
const submitting = ref(false)

function resetForm() {
  signalName.value = ''
  color.value = '#324245'
  icon.value = ''
  signalUnit.value = ''
  selectedSignalType.value = 'tally'
  selectedSummaryMethod.value = 'total'
  minValue.value = undefined
  maxValue.value = undefined
  minLabel.value = ''
  maxLabel.value = ''
  errors.value = {}
}

async function submitSignal() {
  if (!selectedSignalType.value || !selectedSummaryMethod.value || !signalName.value) return

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
    const { data } = await createSignal(payload)
    emit('created', data)
    resetForm()
    open.value = false
  } catch (err) {
    console.error(err)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <Modal v-model:open="open" title="Create signal">
    <template #trigger>
      <slot name="trigger">
        <Button>Create signal</Button>
      </slot>
    </template>

    <SignalForm v-model:name="signalName" v-model:color="color" v-model:icon="icon" v-model:unit="signalUnit"
      v-model:type="selectedSignalType" v-model:summary-method="selectedSummaryMethod" v-model:min-value="minValue"
      v-model:max-value="maxValue" v-model:min-label="minLabel" v-model:max-label="maxLabel" :errors="errors" />

    <template #footer>
      <DialogClose as-child>
        <Button variant="secondary">Cancel</Button>
      </DialogClose>
      <Button :disabled="submitting" variant="primary" @click="submitSignal()">
        {{ submitting ? 'Saving...' : 'Create signal' }}
      </Button>
    </template>
  </Modal>
</template>
