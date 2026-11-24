<script setup lang="ts">
import { onMounted, ref } from 'vue'
import Header from '@/shared/ui/components/Header.vue'
import Button from '@/shared/ui/components/Button.vue'
import AppShellHeader from '@/shared/ui/layout/AppShellHeader.vue'
import { useToast } from '@/shared/lib/useToast'
import ExtensionSlot from '@/shared/ui/components/ExtensionSlot.vue'
import ChangeEmailForm from '../components/ChangeEmailForm.vue'
import ChangePasswordForm from '../components/ChangePasswordForm.vue'
import { exportData, getMe } from '../api'
import ImportDataDialog from '../components/ImportDataDialog.vue'
import DeleteAccountDialog from '../components/DeleteAccountDialog.vue'

const { toast } = useToast()
const deleteOpen = ref(false)
const importOpen = ref(false)

async function handleExport() {
  try {
    await exportData()
  } catch {
    toast({ title: 'Could not export your data', variant: 'danger' })
  }
}
const email = ref('')

onMounted(async () => {
  try {
    const { data } = await getMe()
    email.value = data.email
  } catch {
    toast({ title: 'Could not load your account', variant: 'danger' })
  }
})
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

    <ExtensionSlot name="account" />

    <section>
      <h2>Your data</h2>
      <p>
        Download all your signals, boards, dashboards and events as a file, or replace everything
        with a previously exported file. Works across bitjournal instances.
      </p>
      <div class="actions">
        <Button variant="secondary" @click="handleExport">Export</Button>
        <Button variant="warn" @click="importOpen = true">Import</Button>
      </div>
    </section>

    <section>
      <h2>Delete account</h2>
      <p>Permanently delete your account and all your data.</p>
      <Button variant="warn" @click="deleteOpen = true">Delete account</Button>
    </section>
  </div>

  <ImportDataDialog v-model:open="importOpen" />
  <DeleteAccountDialog v-model:open="deleteOpen" />
</template>

<style scoped>
.account-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xxxl);
  padding: var(--padding-app);
}

section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}
.actions {
  display: flex;
  gap: var(--spacing-md);
}
</style>
