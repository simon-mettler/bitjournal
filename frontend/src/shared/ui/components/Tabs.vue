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
}

.tabs-list::-webkit-scrollbar {
  display: none;
}

.tabs-trigger {
  all: unset;
  flex-shrink: 0;
  padding: 8px 16px;
  border-radius: var(--radius-xl);
  border: 1px solid #62656B;
  font-size: var(--font-size-sm);
  color: var(--input-color-text);
  cursor: pointer;
  white-space: nowrap;
}

.tabs-trigger[data-state='active'] {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
  color: var(--color-surface);
  font-weight: var(--font-weight-bold);
}
</style>
