<script setup lang="ts">
import { reactive, ref } from 'vue'
import { isAxiosError } from 'axios'
import InputText from '@/shared/ui/components/InputText.vue'
import Button from '@/shared/ui/components/Button.vue'
import { useFormValidation } from '@/shared/lib/useFormValidation'
import { required, type Rule } from '@/shared/lib/validators'
import { useToast } from '@/shared/lib/useToast'
import { changePassword } from '../api'

const { toast } = useToast()

const form = reactive({ current: '', next: '', confirm: '' })
const loading = ref(false)

const matchesNew: Rule = (v) => v === form.next || 'Passwords do not match'

const { errors, validateAll, clear } = useFormValidation(
  {
    current: () => form.current,
    next: () => form.next,
    confirm: () => form.confirm,
  },
  {
    current: [required()],
    next: [required()],
    confirm: [required(), matchesNew],
  },
)

function firstMessage(value: unknown): string | undefined {
  return Array.isArray(value) ? value[0] : undefined
}

async function handleSubmit() {
  if (!validateAll()) return
  loading.value = true
  try {
    await changePassword({ current_password: form.current, new_password: form.next })
    form.current = form.next = form.confirm = ''
    clear()
    toast({ title: 'Password changed', variant: 'success' })
  } catch (err) {
    const data = isAxiosError(err) ? err.response?.data : undefined
    const currentError = firstMessage(data?.current_password)
    const nextError = firstMessage(data?.new_password)
    if (currentError) errors.current = currentError
    if (nextError) errors.next = nextError
    if (!currentError && !nextError) {
      toast({ title: 'Could not change password', variant: 'danger' })
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <form @submit.prevent="handleSubmit">
    <InputText
      v-model="form.current"
      type="password"
      label="Current password"
      autocomplete="current-password"
      :error="errors.current"
    />
    <InputText
      v-model="form.next"
      type="password"
      label="New password"
      autocomplete="new-password"
      :error="errors.next"
    />
    <InputText
      v-model="form.confirm"
      type="password"
      label="Confirm new password"
      autocomplete="new-password"
      :error="errors.confirm"
    />
    <Button type="submit" :disabled="loading">Change password</Button>
  </form>
</template>

<style scoped>
form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

form > button {
  margin-top: var(--spacing-md);
}
</style>
