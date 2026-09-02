<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Button from '@/shared/ui/components/Button.vue'
import SignalForm from '@/modules/signals/components/SignalForm.vue'
import AppShellHeader from '@/shared/ui/layout/AppShellHeader.vue'
import AppShellFooter from '@/shared/ui/layout/AppShellFooter.vue'
import { createSignal, type CreateSignalPayload } from '@/modules/signals/api'
import type { Signal } from '@/modules/signals/types'
import { useToast } from '@/shared/lib/useToast'
import Header from '@/shared/ui/components/Header.vue'
import Footer from '@/shared/ui/components/Footer.vue'
const toast = useToast()
const emit = defineEmits<{ created: [signal: Signal] }>()
const router = useRouter()

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
  } catch (err) {
    console.error(err)
  } finally {
    submitting.value = false
    router.back()
  }
}
</script>

<template>
  <AppShellHeader>
    <Header heading="Create signal"></Header>
  </AppShellHeader>

  <div class="add-signal-content">
    <SignalForm v-model:name="signalName" v-model:color="color" v-model:icon="icon" v-model:unit="signalUnit"
      v-model:type="selectedSignalType" v-model:summary-method="selectedSummaryMethod" v-model:min-value="minValue"
      v-model:max-value="maxValue" v-model:min-label="minLabel" v-model:max-label="maxLabel" :errors="errors" />
  </div>
  <AppShellFooter>
    <Footer>
      <Button variant="secondary">Cancel</Button>
      <Button :disabled="submitting" variant="primary" @click="submitSignal()">
        {{ submitting ? 'Saving...' : 'Create signal' }}
      </Button>
    </Footer>
  </AppShellFooter>
</template>

<style scoped>
.add-signal-content {
  padding: 0 var(--padding-app);
}
</style>
