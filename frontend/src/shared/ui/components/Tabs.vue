<script setup lang="ts">
import { TabsList, TabsRoot, TabsTrigger } from 'reka-ui'

export interface TabItem {
  value: string
  label: string
}

defineProps<{
  items: TabItem[]
}>()

const model = defineModel<string>({ required: true })
</script>

<template>
  <TabsRoot v-model="model" class="tabs-root">
    <TabsList class="tabs-list" aria-label="Tabs">
      <TabsTrigger v-for="item in items" :key="item.value" class="tabs-trigger" :value="item.value">
        {{ item.label }}
      </TabsTrigger>
    </TabsList>
  </TabsRoot>
</template>

<style scoped>
.tabs-root {
  width: 100%;
}

.tabs-list {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  scrollbar-width: none;

  & > :first-child {
    margin-left: 16px;
  }
}

.tabs-list::-webkit-scrollbar {
  display: none;
}

.tabs-trigger {
  all: unset;
  flex-shrink: 0;
  padding: 8px 16px;
  border-radius: var(--radius-xl);
  border: 1px solid transparent;
  background-color: var(--color-surface);
  font-size: var(--font-size-sm);
  color: var(--input-color-text);
  cursor: pointer;
  white-space: nowrap;
  transition:
    background-color 160ms ease,
    box-shadow 160ms ease;
}

.tabs-trigger[data-state='active'] {
  background: var(--color-primary);
  border-color: transparent;
  color: var(--color-on-primary);
  font-weight: var(--font-weight-bold);
}
</style>
