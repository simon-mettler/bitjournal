<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { isAxiosError } from 'axios'
import InputText from '@/shared/ui/components/InputText.vue'
import Button from '@/shared/ui/components/Button.vue'
import Header from '@/shared/ui/components/Header.vue'
import { useFormValidation } from '@/shared/lib/useFormValidation'
import { required, type Rule } from '@/shared/lib/validators'
import { useToast } from '@/shared/lib/useToast'
import { confirmPasswordReset } from '../api'

const route = useRoute()
const router = useRouter()
const { toast } = useToast()

const form = reactive({ next: '', confirm: '' })
const loading = ref(false)
const linkError = ref('')

const matchesNew: Rule = (v) => v === form.next || 'Passwords do not match'

const { errors, validateAll } = useFormValidation(
  { next: () => form.next, confirm: () => form.confirm },
  { next: [required()], confirm: [required(), matchesNew] },
)

function firstMessage(value: unknown): string | undefined {
  return Array.isArray(value) ? value[0] : undefined
}

async function handleSubmit() {
  if (!validateAll()) return
  linkError.value = ''
  loading.value = true
  try {
    await confirmPasswordReset({
      uid: String(route.params.uid),
      token: String(route.params.token),
      new_password: form.next,
    })
    toast({ title: 'Password changed', description: 'You can log in now.', variant: 'success' })
    await router.push({ name: 'login' })
  } catch (err) {
    const data = isAxiosError(err) ? err.response?.data : undefined
    linkError.value = firstMessage(data?.token) ?? ''
    const passwordError = firstMessage(data?.new_password)
    if (passwordError) errors.next = passwordError
    if (!linkError.value && !passwordError) {
      toast({ title: 'Could not reset password', variant: 'danger' })
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Header heading="Reset password"></Header>
  <form @submit.prevent="handleSubmit">
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
    <Button type="submit" :disabled="loading">Set new password</Button>
    <p v-if="linkError">
      {{ linkError }}
      <RouterLink :to="{ name: 'forgot-password' }">Request a new link</RouterLink>
    </p>
  </form>
</template>

<style scoped>
form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  padding: var(--padding-app);
}

form > button {
  margin-top: 16px;
}
</style>
