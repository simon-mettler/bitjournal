<script setup lang="ts">
import Header from '@/shared/ui/components/Header.vue'
import Button from '@/shared/ui/components/Button.vue'
import ToggleGroup from '@/shared/ui/components/ToggleGroup.vue'
import AppShellHeader from '@/shared/ui/layout/AppShellHeader.vue'
import { useAuthStore } from '@/modules/authentication/store'
import { ref } from 'vue'
import { useToast } from '@/shared/lib/useToast'
import { checkNow, useAppUpdate } from '@/shared/lib/appUpdate'
import { useTheme, type ThemeMode } from '@/shared/lib/useTheme'

const auth = useAuthStore()
const { toast } = useToast()
const { mode, setMode } = useTheme()
const themeOptions: { value: ThemeMode; label: string }[] = [
  { value: 'system', label: 'System' },
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
]

const update = useAppUpdate()
const checkingManually = ref(false)

function formatTime(ms: number | null) {
  return ms ? new Date(ms).toLocaleTimeString() : 'never'
}

async function handleCheckUpdate() {
  checkingManually.value = true
  try {
    const result = await checkNow()
    if (result === 'current') toast({ title: 'You are on the latest version', variant: 'success' })
    else if (result === 'error') toast({ title: 'Could not check for updates', variant: 'danger' })
  } finally {
    checkingManually.value = false
  }
}

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

    <section>
      <h2>About</h2>
      <p class="about-details">
        Version: {{ update.version }}<br />
        Build: {{ update.buildId }}<br />
        Service worker: {{ update.swState.value }}<br />
        Last checked: {{ formatTime(update.lastCheckedAt.value) }}
      </p>
      <Button variant="secondary" :disabled="checkingManually" @click="handleCheckUpdate">
        Check for updates
      </Button>
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

.about-details {
  overflow-wrap: anywhere;
}

.theme-toggle {
  width: fit-content;
}
</style>
