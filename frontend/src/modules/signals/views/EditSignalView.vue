<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Button from '@/shared/ui/components/Button.vue'
import Footer from '@/shared/ui/components/Footer.vue'
import Header from '@/shared/ui/components/Header.vue'
import AlertDialog from '@/shared/ui/components/AlertDialog.vue'
import SignalForm from '@/modules/signals/components/SignalForm.vue'
import AppShellHeader from '@/shared/ui/layout/AppShellHeader.vue'
import AppShellFooter from '@/shared/ui/layout/AppShellFooter.vue'
import { getSignal, updateSignal, deleteSignal, type CreateSignalPayload } from '@/modules/signals/api'
import type { Signal } from '@/modules/signals/types'
import { useToast } from '@/shared/lib/useToast'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const signalId = route.params.id as string

const saving = ref(false)
const errors = ref<Record<string, string[]>>({})

const signalName = ref('')
const color = ref('')
const icon = ref('')
const signalUnit = ref('')
const selectedSummaryMethod = ref<Signal['summary_method']>('total')
const minValue = ref<number>()
const maxValue = ref<number>()
const minLabel = ref('')
const maxLabel = ref('')

const signal = ref<Signal | null>(null)

async function load() {
  try {
    const { data } = await getSignal(signalId)
    signal.value = data
    signalName.value = data.name
    color.value = data.color ?? ''
    icon.value = data.icon ?? ''
    selectedSummaryMethod.value = data.summary_method
    if (data.value_config) {
      signalUnit.value = data.value_config.unit ?? ''
    }
    if (data.range_config) {
      minValue.value = data.range_config.min_value
      maxValue.value = data.range_config.max_value
      minLabel.value = data.range_config.min_label ?? ''
      maxLabel.value = data.range_config.max_label ?? ''
    }
  } catch (err) {
    console.error(err)
    toast.toast({ description: 'Failed to load signal', variant: 'error' })
  }
}

async function save() {
  if (!signalName.value || !signal.value) return

  const payload: CreateSignalPayload = {
    name: signalName.value,
    type: signal.value.type,
    summary_method: selectedSummaryMethod.value,
    color: color.value,
    icon: icon.value,
  }
  if (signal.value.type === 'value') {
    payload.value_config = { unit: signalUnit.value }
  }
  if (signal.value.type === 'range' && minValue.value !== undefined && maxValue.value !== undefined) {
    payload.range_config = {
      min_value: minValue.value,
      max_value: maxValue.value,
      min_label: minLabel.value,
      max_label: maxLabel.value,
    }
  }

  saving.value = true
  errors.value = {}
  try {
    await updateSignal(signal.value.id, payload)
    toast.toast({ description: 'Signal saved.', variant: 'success' })
    router.back()
  } catch (err) {
    console.error(err)
    toast.toast({ description: 'Failed to save signal', variant: 'error' })
  } finally {
    saving.value = false
  }
}

async function confirmDeleteSignal() {
  try {
    await deleteSignal(signalId)
    router.push({ name: 'manage-signals' })
  } catch (err) {
    console.log(err)
    toast.toast({ description: 'Could not delete signal.', variant: 'error' })
  }
}
onMounted(load)
</script>

<template>

  <AppShellHeader>
    <Header heading="Edit signal">
    </Header>
  </AppShellHeader>

  <div class="edit-signal-content">
    <SignalForm v-if="signal" v-model:name="signalName" v-model:color="color" v-model:icon="icon"
      v-model:unit="signalUnit" v-model:summary-method="selectedSummaryMethod" v-model:min-value="minValue"
      v-model:max-value="maxValue" v-model:min-label="minLabel" v-model:max-label="maxLabel" :type="signal.type"
      :errors="errors" lock-type />
    <AlertDialog title="Delete signal" confirm-text="Delete"
      :description="`Are you sure you want to delete signal &quot;${signalName}&quot;? This can't be undone.`"
      @confirm="confirmDeleteSignal">
      <template #trigger>
        <Button variant="secondary" class="danger-btn">Delete signal</Button>
      </template>
      <template #cancel>
        <Button variant="secondary">Cancel</Button>
      </template>
      <template #action>
        <Button variant="primary">Delete</Button>
      </template>
    </AlertDialog>
  </div>

  <AppShellFooter>
    <Footer>
      <Button variant="secondary" @click="router.back()">
        Cancel
      </Button>
      <Button variant="primary" :disabled="saving" @click="save">
        {{ saving ? 'Saving...' : 'Save' }}
      </Button>
    </Footer>
  </AppShellFooter>

</template>

<style scoped>
.edit-signal-content {
  padding: 0 var(--padding-app);
}
</style>
