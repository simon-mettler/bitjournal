<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { isAxiosError } from 'axios'
import Dialog from '@/shared/ui/components/Dialog.vue'
import InputText from '@/shared/ui/components/InputText.vue'
import Button from '@/shared/ui/components/Button.vue'
import { useFormValidation } from '@/shared/lib/useFormValidation'
import { required } from '@/shared/lib/validators'
import { useToast } from '@/shared/lib/useToast'
import { importData } from '../api'

const open = defineModel<boolean>('open', { default: false })

const { toast } = useToast()

const form = reactive<{ file: File | null; password: string }>({ file: null, password: '' })
const loading = ref(false)

const { errors, validateAll, clear } = useFormValidation(
  { file: () => form.file, password: () => form.password },
  { file: [required('Choose an export file.')], password: [required()] },
)

watch(open, (isOpen) => {
  if (isOpen) return
  form.file = null
  form.password = ''
  clear()
})

function firstMessage(value: unknown): string | undefined {
  return Array.isArray(value) ? value[0] : undefined
}

async function handleImport() {
  if (!validateAll() || !form.file) return
  loading.value = true
  try {
    await importData(form.file, form.password)
    // Stores cache the old data, start over with a fresh page.
    window.location.assign('/')
  } catch (err) {
    const data = isAxiosError(err) ? err.response?.data : undefined
    const fileError = firstMessage(data?.file)
    const passwordError = firstMessage(data?.password)
    if (fileError) errors.file = fileError
    if (passwordError) errors.password = passwordError
    if (!fileError && !passwordError) {
      toast({ title: 'Import failed', description: 'Nothing was changed.', variant: 'danger' })
    }
    loading.value = false
  }
}
</script>

<template>
  <Dialog
    v-model:open="open"
    title="Import data"
    description="This permanently deletes all your current signals, boards, dashboards and events and replaces them with the contents of the file. This cannot be undone."
  >
    <form id="import-data-form" @submit.prevent="handleImport">
      <div class="file">
        <input
          type="file"
          accept=".json,application/json"
          @change="form.file = ($event.target as HTMLInputElement).files?.[0] ?? null"
        />
        <p v-if="errors.file" class="error">{{ errors.file }}</p>
      </div>
      <InputText
        v-model="form.password"
        type="password"
        label="Password"
        autocomplete="current-password"
        :error="errors.password"
      />
    </form>
    <template #footer>
      <Button variant="secondary" @click="open = false">Cancel</Button>
      <Button variant="warn" type="submit" form="import-data-form" :disabled="loading">
        Replace my data
      </Button>
    </template>
  </Dialog>
</template>

<style scoped>
form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.error {
  color: var(--color-danger);
}
</style>
