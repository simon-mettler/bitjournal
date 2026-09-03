<script setup lang="ts">
import { sidebarGroups } from '@/shared/ui/layout/navConfig'

import { useAuthStore } from '@/modules/authentication/store'
import { useRouter } from 'vue-router'

const router = useRouter()
const auth = useAuthStore()
const emit = defineEmits<{
  navigate: []
}>()

async function logout() {
  try {
    await auth.logout()
  } finally {
    router.push('login')
  }
}
</script>

<template>
  <nav class="sidebar" aria-label="Settings and configuration">
    <div v-for="group in sidebarGroups" :key="group.label" class="sidebar-group">
      <p class="sidebar-group-label">{{ group.label }}</p>
      <ul class="sidebar-section">
        <li v-for="item in group.items" :key="item.label">
          <RouterLink :to="item.to" class="sidebar-item" active-class="active" @click="emit('navigate')">
            <component :is="item.icon" :size="20" />
            <span>{{ item.label }}</span>
          </RouterLink>
        </li>
      </ul>
    </div>
    <button @click="logout()">Logout</button>
  </nav>
</template>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 220px;
  height: 100vh;
  padding: 16px 8px;
}

.sidebar-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sidebar-group-label {
  font-size: var(--font-size-sm);
  color: var(--input-color-label);
  padding: 0 12px;
  margin: 0 0 4px;
  text-transform: uppercase;
}

.sidebar-section {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: var(--input-radius);
  text-decoration: none;
  color: var(--input-color-text);
  font-size: var(--font-size-base);
}


.sidebar-item.active {
  background-color: var(--color-surface-muted);
  color: var(--color-primary);
  font-weight: var(--font-weight-bold);
}
</style>
