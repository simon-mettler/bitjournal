<script setup lang="ts">
import { ref } from 'vue'
import { LogOut } from '@lucide/vue'
import Button from '@/shared/ui/components/Button.vue'
import Logo from '@/shared/ui/components/Logo.vue'
import { primaryNavItems, sidebarGroups, type NavGroup } from '@/shared/ui/layout/navConfig'
import { useAuthStore } from '@/modules/authentication/store'

withDefaults(
  defineProps<{
    /** persistent nav (tablet/desktop) */
    persistent?: boolean
    rail?: boolean
  }>(),
  { persistent: false, rail: false },
)

const auth = useAuthStore()
const logo = ref<{ replay: () => void } | null>(null)
const emit = defineEmits<{ navigate: [] }>()

defineExpose({ replayLogo: () => logo.value?.replay() })

const appVersion = __APP_VERSION__
const mainGroup: NavGroup = { label: 'Main', items: primaryNavItems }
</script>

<template>
  <nav
    class="nav-content"
    :class="{ rail, persistent }"
    :aria-label="persistent ? 'Primary' : 'Settings and configuration'"
  >
    <RouterLink :to="{ name: 'track' }" class="nav-content-logo" aria-label="bitjournal">
      <Logo ref="logo" :variant="rail ? 'mark' : 'full'" />
    </RouterLink>
    <div
      v-for="group in persistent ? [mainGroup, ...sidebarGroups] : sidebarGroups"
      :key="group.label"
      class="sidebar-group"
    >
      <p class="nav-content-group-label">{{ group.label }}</p>
      <ul class="nav-content-section">
        <li v-for="item in group.items" :key="item.label">
          <RouterLink
            :to="item.to"
            class="nav-content-item"
            active-class="active"
            :title="rail ? item.label : undefined"
            @click="emit('navigate')"
          >
            <component :is="item.icon" :size="rail ? 22 : 20" />
            <span class="nav-content-label">{{ item.label }}</span>
          </RouterLink>
        </li>
      </ul>
    </div>
    <Button v-if="!rail" class="nav-content-logout" @click="auth.logout()">Logout</Button>
    <button v-else type="button" class="nav-content-item nav-content-logout" @click="auth.logout()">
      <LogOut :size="22" />
      <span class="nav-content-label">Logout</span>
    </button>
    <span v-if="!rail" class="nav-content-version">v{{ appVersion }}</span>
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
  all: unset;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  margin-bottom: var(--spacing-xs);
  border-radius: var(--input-radius);
  text-decoration: none;
  color: var(--input-color-text);
  font-size: var(--font-size-base);
  cursor: pointer;
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

.nav-content.rail {
  gap: 4px;
  align-items: stretch;
}

.nav-content.rail .nav-content-logo {
  width: 40px;
  padding: 0;
  margin: 0 auto var(--spacing-md);
}

.nav-content.rail .sidebar-group + .sidebar-group {
  margin-top: var(--spacing-sm);
  padding-top: var(--spacing-sm);
  border-top: 1px solid var(--color-border);
}

.nav-content.rail .nav-content-group-label {
  display: none;
}

.nav-content.rail .nav-content-item {
  flex-direction: column;
  justify-content: center;
  gap: 2px;
  padding: 8px 4px;
  text-align: center;
}

.nav-content.rail .nav-content-label {
  font-size: 0.75rem;
}

.nav-content.rail .nav-content-logout {
  color: var(--input-color-label);
}
</style>
