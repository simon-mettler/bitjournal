<script setup lang="ts">
import Header from '@/shared/ui/components/Header.vue'
import Button from '@/shared/ui/components/Button.vue'
import AppShellHeader from '@/shared/ui/layout/AppShellHeader.vue'
import { useAuthStore } from '@/modules/authentication/store'
import { useToast } from '@/shared/lib/useToast'
import ChangePasswordForm from '../components/ChangePasswordForm.vue'

const auth = useAuthStore()
const { toast } = useToast()

async function handleLogoutAll() {
  try {
    await auth.logoutAll()
  } catch {
    toast({ title: 'Could not log out everywhere', variant: 'danger' })
  }
}
</script>

<template>
  <AppShellHeader>
    <Header heading="Account" />
  </AppShellHeader>

  <div class="account-content">
    <section>
      <h2>Change password</h2>
      <ChangePasswordForm />
    </section>

    <section>
      <h2>Sessions</h2>
      <p>Log out on all devices, including this one.</p>
      <Button variant="secondary" @click="handleLogoutAll">Log out everywhere</Button>
    </section>
  </div>
</template>

<style scoped>
.account-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
  padding: var(--padding-app);
}

section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}
</style>
