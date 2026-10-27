<script setup lang="ts">
import { ref } from 'vue'
import Button from '@/shared/ui/components/Button.vue'
import Logo from '@/shared/ui/components/Logo.vue'
import { sidebarGroups } from '@/shared/ui/layout/navConfig'
import { useAuthStore } from '@/modules/authentication/store'

const auth = useAuthStore()
const logo = ref<{ replay: () => void } | null>(null)
const emit = defineEmits<{ navigate: [] }>()

defineExpose({ replayLogo: () => logo.value?.replay() })

const appVersion = __APP_VERSION__
</script>

<template>
  <nav class="nav-content" aria-label="Settings and configuration">
    <RouterLink :to="{ name: 'track' }" class="nav-content-logo" aria-label="bitjournal">
      <Logo ref="logo" />
    </RouterLink>
    <div v-for="group in sidebarGroups" :key="group.label" class="sidebar-group">
      <p class="nav-content-group-label">{{ group.label }}</p>
      <ul class="nav-content-section">
        <li v-for="item in group.items" :key="item.label">
          <RouterLink
            :to="item.to"
            class="nav-content-item"
            active-class="active"
            @click="emit('navigate')"
          >
            <component :is="item.icon" :size="20" />
            <span>{{ item.label }}</span>
          </RouterLink>
        </li>
      </ul>
    </div>
    <Button class="nav-content-logout" @click="auth.logout()">Logout</Button>
    <span class="nav-content-version">v{{ appVersion }}</span>
  </nav>
</template>

<style scoped>
.nav-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.nav-content-logo {
  display: block;
  width: 184px;
  padding: 0 12px;
  margin-bottom: var(--spacing-sm);
}

.nav-content-logo :deep(.logo) {
  width: 100%;
}

.nav-content-group-label {
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  color: var(--input-color-label);
  padding: 0 12px;
  margin: 0 0 4px;
}

.nav-content-section {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.nav-content-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: var(--input-radius);
  text-decoration: none;
  color: var(--input-color-text);
  font-size: var(--font-size-base);
  transition: background-color 160ms ease;
}

.nav-content-item:hover {
  background-color: var(--color-primary-soft);
}

.nav-content-item.active {
  background-color: var(--color-primary-soft);
  color: var(--color-primary);
  font-weight: var(--font-weight-bold);
}

.nav-content-logout {
  margin-top: auto;
}

.nav-content-version {
  text-align: center;
  font-size: var(--font-size-sm);
  color: var(--input-color-label);
}
</style>
