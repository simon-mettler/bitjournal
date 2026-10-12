<script setup lang="ts">
import Toast from '@/shared/ui/components/Toast.vue'
import AppShell from '@/shared/ui/layout/AppShell.vue'
import { useViewportHeight } from './shared/lib/useViewportHeight'
import { watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/modules/authentication/store'

useViewportHeight()

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
watch(
  () => auth.isAuthenticated,
  (authenticated) => {
    if (!authenticated && !route.matched.some((r) => r.meta.public))
      void router.push({ name: 'login' })
  },
)
</script>

<template>
  <Toast />
  <AppShell />
</template>
