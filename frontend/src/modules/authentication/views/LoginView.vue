<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store'
import { isAxiosError } from 'axios'

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
  TEST
  <form @submit.prevent="handleSubmit">
    <input v-model="username" placeholder="Username" required />
    <input v-model="password" type="password" placeholder="Password" required />
    <button type="submit" :disabled="loading">Login</button>
    <p v-if="error">{{ error }}</p>
  </form>
</template>
