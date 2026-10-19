<script setup lang="ts">
import { reactive, ref } from 'vue'
import { isAxiosError } from 'axios'
import InputText from '@/shared/ui/components/InputText.vue'
import Button from '@/shared/ui/components/Button.vue'
import { useFormValidation } from '@/shared/lib/useFormValidation'
import { required } from '@/shared/lib/validators'
import { useToast } from '@/shared/lib/useToast'
import { changeEmail } from '../api'

const emit = defineEmits<{ changed: [email: string] }>()

const { toast } = useToast()

const form = reactive({ email: '', password: '' })
const loading = ref(false)
const pendingEmail = ref('')

const { errors, validateAll, clear } = useFormValidation(
  { email: () => form.email, password: () => form.password },
  { email: [required()], password: [required()] },
)

function firstMessage(value: unknown): string | undefined {
  return Array.isArray(value) ? value[0] : undefined
}

async function handleSubmit() {
  if (!validateAll()) return
  loading.value = true
  pendingEmail.value = ''
  try {
    const { data } = await changeEmail({ new_email: form.email, current_password: form.password })
    if (data.status === 'confirmation_sent') {
      pendingEmail.value = form.email
    } else if (data.email) {
      emit('changed', data.email)
      toast({ title: 'Email changed', variant: 'success' })
    }
    form.email = form.password = ''
    clear()
  } catch (err) {
    const data = isAxiosError(err) ? err.response?.data : undefined
    const emailError = firstMessage(data?.new_email)
    const passwordError = firstMessage(data?.current_password)
    if (emailError) errors.email = emailError
    if (passwordError) errors.password = passwordError
    if (!emailError && !passwordError) {
      toast({
        title: 'Could not change email',
        description: data?.detail ?? 'Please try again later.',
        variant: 'danger',
      })
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <form @submit.prevent="handleSubmit">
    <InputText
      v-model="form.email"
      type="email"
      label="New email"
      autocomplete="email"
      :error="errors.email"
    />
    <InputText
      v-model="form.password"
      type="password"
      label="Current password"
      autocomplete="current-password"
      :error="errors.password"
    />
    <Button type="submit" :disabled="loading">Change email</Button>
    <p v-if="pendingEmail">
      We sent a confirmation link to {{ pendingEmail }}. Your email changes once you open it.
    </p>
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
