<script setup lang="ts">
import { ref } from 'vue'
import InputText from '@/shared/ui/components/InputText.vue'
import Button from '@/shared/ui/components/Button.vue'
import Header from '@/shared/ui/components/Header.vue'
import { requestPasswordReset } from '../api'

const email = ref('')
const error = ref('')
const loading = ref(false)
const sent = ref(false)

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    await requestPasswordReset({ email: email.value })
    sent.value = true
  } catch {
    error.value = 'Could not send the mail. Please try again later.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Header heading="Forgot password"></Header>
  <p v-if="sent" class="forgot-hint">
    If an account exists for {{ email }}, we sent a link to reset the password.
  </p>
  <form v-else @submit.prevent="handleSubmit">
    <InputText v-model="email" type="email" label="Email" required />
    <Button type="submit" :disabled="loading">Send reset link</Button>
    <p v-if="error">{{ error }}</p>
  </form>

  <p class="forgot-hint">
    <RouterLink :to="{ name: 'login' }">Back to login</RouterLink>
  </p>
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

.forgot-hint {
  text-align: center;
  padding: var(--padding-app);
}
</style>
