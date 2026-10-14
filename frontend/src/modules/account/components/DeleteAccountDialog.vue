<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { isAxiosError } from 'axios'
import Dialog from '@/shared/ui/components/Dialog.vue'
import InputText from '@/shared/ui/components/InputText.vue'
import Button from '@/shared/ui/components/Button.vue'
import { useFormValidation } from '@/shared/lib/useFormValidation'
import { required } from '@/shared/lib/validators'
import { useToast } from '@/shared/lib/useToast'
import { useAuthStore } from '@/modules/authentication/store'

const open = defineModel<boolean>('open', { default: false })

const auth = useAuthStore()
const { toast } = useToast()

const form = reactive({ email: '', password: '' })
const loading = ref(false)

const { errors, validateAll, clear } = useFormValidation(
  { email: () => form.email, password: () => form.password },
  { email: [required()], password: [required()] },
)

watch(open, (isOpen) => {
  if (isOpen) return
  form.email = form.password = ''
  clear()
})

function firstMessage(value: unknown): string | undefined {
  return Array.isArray(value) ? value[0] : undefined
}

async function handleDelete() {
  if (!validateAll()) return
  loading.value = true
  try {
    await auth.deleteAccount({ email: form.email, password: form.password })
    open.value = false
    toast({ title: 'Account deleted', variant: 'success' })
  } catch (err) {
    const data = isAxiosError(err) ? err.response?.data : undefined
    const emailError = firstMessage(data?.email)
    const passwordError = firstMessage(data?.password)
    if (emailError) errors.email = emailError
    if (passwordError) errors.password = passwordError
    if (!emailError && !passwordError) {
      toast({
        title: 'Could not delete account',
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
  <Dialog
    v-model:open="open"
    title="Delete account"
    description="This permanently deletes your account and all your signals, boards and events. This cannot be undone."
  >
    <form id="delete-account-form" @submit.prevent="handleDelete">
      <InputText
        v-model="form.email"
        type="email"
        label="Type your email to confirm"
        autocomplete="off"
        :error="errors.email"
      />
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
      <Button variant="warn" type="submit" form="delete-account-form" :disabled="loading">
        Delete account
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
</style>
