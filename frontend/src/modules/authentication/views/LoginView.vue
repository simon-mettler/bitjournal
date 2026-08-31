<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store'
import { isAxiosError } from 'axios'
import InputText from '@/shared/ui/components/InputText.vue'
import Button from '@/shared/ui/components/Button.vue'
import Header from '@/shared/ui/components/Header.vue'

const auth = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login({ username: username.value, password: password.value })
    router.push('/')
  } catch (err) {
    if (isAxiosError(err)) {
      error.value = err.response?.data?.detail || 'Login failed'
    } else {
      error.value = 'error: unknown'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Header heading="Login"></Header>
  <form @submit.prevent="handleSubmit">
    <InputText v-model="username" label="Username" required />
    <InputText v-model="password" type="password" label="Password" required />
    <Button type="submit" :disabled="loading">Login</Button>
    <p v-if="error">{{ error }}</p>
  </form>

  <p class="login-hint">
    No account yet?
    <RouterLink :to="{ name: 'register' }">Register here</RouterLink>
  </p>
</template>

<style scoped>
form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  padding: var(--padding-app);
}

form>button {
  margin-top: 16px;
}

.login-hint {
  text-align: center;
}
</style>
