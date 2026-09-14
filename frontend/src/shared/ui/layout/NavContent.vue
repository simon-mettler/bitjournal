<script setup lang="ts">
import { useRouter } from 'vue-router'
import Button from '@/shared/ui/components/Button.vue'
import { sidebarGroups } from '@/shared/ui/layout/navConfig'
import { useAuthStore } from '@/modules/authentication/store'

const router = useRouter()
const auth = useAuthStore()
const emit = defineEmits<{ navigate: [] }>()

async function logout() {
  try {
    await auth.logout()
  } finally {
    router.push('login')
  }
}
</script>

<template>
  <nav class="nav-content" aria-label="Settings and configuration">
    <div v-for="group in sidebarGroups" :key="group.label" class="sidebar-group">
      <p class="nav-content-group-label">{{ group.label }}</p>
      <ul class="nav-content-section">
        <li v-for="item in group.items" :key="item.label">
          <RouterLink :to="item.to" class="nav-content-item" active-class="active" @click="emit('navigate')">
            <component :is="item.icon" :size="20" />
            <span>{{ item.label }}</span>
          </RouterLink>
        </li>
      </ul>
    </div>
    <Button class="nav-content-logout" @click="logout()">Logout</Button>
  </nav>
</template>

<style scoped>
.nav-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.nav-content-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-content-group-label {
  font-size: var(--font-size-sm);
  color: var(--input-color-label);
  padding: 0 12px;
  margin: 0 0 4px;
  text-transform: uppercase;
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
}

.nav-content-item.active {
  background-color: var(--color-surface-muted);
  color: var(--color-primary);
  font-weight: var(--font-weight-bold);
}

.nav-content-logout {
  margin-top: 20%;
}
</style>
