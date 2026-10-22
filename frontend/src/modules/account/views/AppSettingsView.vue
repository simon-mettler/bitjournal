<script setup lang="ts">
import Header from '@/shared/ui/components/Header.vue'
import Button from '@/shared/ui/components/Button.vue'
import ToggleGroup from '@/shared/ui/components/ToggleGroup.vue'
import AppShellHeader from '@/shared/ui/layout/AppShellHeader.vue'
import { useAuthStore } from '@/modules/authentication/store'
import { useToast } from '@/shared/lib/useToast'
import { useTheme, type ThemeMode } from '@/shared/lib/useTheme'

const auth = useAuthStore()
const { toast } = useToast()
const { mode, setMode } = useTheme()
const themeOptions: { value: ThemeMode; label: string }[] = [
  { value: 'system', label: 'System' },
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
]

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
    <Header heading="App" />
  </AppShellHeader>

  <div class="app-settings-content">
    <section>
      <h2>Appearance</h2>
      <ToggleGroup
        :model-value="mode"
        :options="themeOptions"
        class="theme-toggle"
        @update:model-value="setMode"
      />
    </section>

    <section>
      <h2>Sessions</h2>
      <p>Log out on all devices, including this one.</p>
      <Button variant="secondary" @click="handleLogoutAll">Log out everywhere</Button>
    </section>
  </div>
</template>

<style scoped>
.app-settings-content {
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

.theme-toggle {
  width: fit-content;
}
</style>
