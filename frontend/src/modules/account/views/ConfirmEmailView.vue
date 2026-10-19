<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { isAxiosError } from 'axios'
import Header from '@/shared/ui/components/Header.vue'
import { confirmEmailChange } from '../api'

const route = useRoute()

const status = ref<'loading' | 'success' | 'error'>('loading')
const email = ref('')
const error = ref('')

onMounted(async () => {
  try {
    const { data } = await confirmEmailChange({ token: String(route.params.token) })
    email.value = data.email
    status.value = 'success'
  } catch (err) {
    const data = isAxiosError(err) ? err.response?.data : undefined
    error.value = data?.token?.[0] ?? 'Could not confirm your new email.'
    status.value = 'error'
  }
})
</script>

<template>
  <Header heading="Confirm email"></Header>
  <p class="confirm-message">
    <template v-if="status === 'loading'">Confirming...</template>
    <template v-else-if="status === 'success'">
      Your email is now {{ email }}. Use it the next time you log in.
    </template>
    <template v-else>{{ error }}</template>
  </p>
  <p class="confirm-message">
    <RouterLink :to="{ name: 'account' }">Go to account</RouterLink>
  </p>
</template>

<style scoped>
.confirm-message {
  text-align: center;
  padding: var(--padding-app);
}
</style>
