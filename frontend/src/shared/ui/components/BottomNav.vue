<script setup lang="ts">
import { primaryNavItems, moreNavIcon } from '@/shared/ui/layout/navConfig'

const emit = defineEmits<{
  moreClick: []
}>()
</script>

<template>
  <nav class="bottom-nav" aria-label="Primary">
    <button type="button" class="bottom-nav-item" aria-label="More" @click="emit('moreClick')">
      <component :is="moreNavIcon" :size="22" />
      <span class="bottom-nav-label">More</span>
    </button>
    <RouterLink v-for="item in primaryNavItems" :key="item.label" :to="item.to" class="bottom-nav-item"
      active-class="active">
      <component :is="item.icon" :size="22" />
      <span class="bottom-nav-label">{{ item.label }}</span>
    </RouterLink>

  </nav>
</template>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-around;
  align-items: center;
  height: 60px;
  background-color: var(--input-color-background);
  border-top: var(--input-border);
  z-index: 1;
}

.bottom-nav-item {
  all: unset;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  flex: 1;
  height: 100%;
  justify-content: center;
  text-decoration: none;
  color: var(--input-color-label);
  cursor: pointer;
}

.bottom-nav-item.active {
  color: var(--color-primary);
}

.bottom-nav-label {
  font-size: var(--font-size-sm);
}
</style>
