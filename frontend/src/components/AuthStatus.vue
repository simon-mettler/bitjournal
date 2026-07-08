<script setup lang="ts">
// for testing
import { useAuthStore } from '@/modules/authentication/store'
import { api } from '@/shared/api'
import { ref } from 'vue'
import { isAxiosError } from 'axios'

const auth = useAuthStore()
const testResult = ref('')

async function testProtectedRoute() {
  testResult.value = 'loading...'
  try {
    const { data } = await api.get('/users/me/')
    testResult.value = JSON.stringify(data)
  } catch (err) {
    if (isAxiosError(err)) {
      testResult.value = `error: ${err.response?.status} ${JSON.stringify(err.response?.data)}`
    } else {
      testResult.value = 'error: unknown'
    }
  }
}
</script>

<template>
  <div style="border: 1px solid #ccc; padding: 1rem; margin-bottom: 1rem;">
    <p>
      Status:
      <strong :style="{ color: auth.isAuthenticated ? 'green' : 'red' }">
        {{ auth.isAuthenticated ? 'Logged in' : 'Logged out' }}
      </strong>
    </p>

    <button @click="testProtectedRoute">Test protected route</button>
    <button v-if="auth.isAuthenticated" @click="auth.logout()">Logout</button>

    <p v-if="testResult">{{ testResult }}</p>
  </div>
</template>
