<script setup lang="ts">
import { onMounted, ref } from 'vue'
import Header from '@/shared/ui/components/Header.vue'
import Button from '@/shared/ui/components/Button.vue'
import AppShellHeader from '@/shared/ui/layout/AppShellHeader.vue'
import { useAuthStore } from '@/modules/authentication/store'
import { useToast } from '@/shared/lib/useToast'
import ChangeEmailForm from '../components/ChangeEmailForm.vue'
import ChangePasswordForm from '../components/ChangePasswordForm.vue'
import { getMe } from '../api'
import DeleteAccountDialog from '../components/DeleteAccountDialog.vue'

const auth = useAuthStore()
const { toast } = useToast()
const deleteOpen = ref(false)
const email = ref('')

onMounted(async () => {
  try {
    const { data } = await getMe()
    email.value = data.email
  } catch {
    toast({ title: 'Could not load your account', variant: 'danger' })
  }
})

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
      <h2>Email</h2>
      <p v-if="email">Current email: {{ email }}</p>
      <ChangeEmailForm @changed="email = $event" />
    </section>

    <section>
      <h2>Change password</h2>
      <ChangePasswordForm />
    </section>

    <section>
      <h2>Sessions</h2>
      <p>Log out on all devices, including this one.</p>
      <Button variant="secondary" @click="handleLogoutAll">Log out everywhere</Button>
    </section>

    <section>
      <h2>Delete account</h2>
      <p>Permanently delete your account and all your data.</p>
      <Button variant="warn" @click="deleteOpen = true">Delete account</Button>
    </section>
  </div>

  <DeleteAccountDialog v-model:open="deleteOpen" />
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
