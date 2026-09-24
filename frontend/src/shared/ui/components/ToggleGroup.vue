<script setup lang="ts" generic="T extends string">
import { ToggleGroupItem, ToggleGroupRoot } from 'reka-ui'

export interface ToggleGroupOption<V extends string = string> {
  value: V
  label: string
}

defineProps<{
  options: ToggleGroupOption<T>[]
}>()

const model = defineModel<T>({ required: true })

function onUpdate(value: unknown) {
  if (typeof value === 'string' && value) model.value = value as T
}
</script>

<template>
  <ToggleGroupRoot type="single" :model-value="model" class="toggle-group" @update:model-value="onUpdate">
    <ToggleGroupItem v-for="option in options" :key="option.value" :value="option.value" class="toggle-group-item">
      {{ option.label }}
    </ToggleGroupItem>
  </ToggleGroupRoot>
</template>

<style scoped>
.toggle-group {
  display: flex;
  gap: 2px;
  padding: 2px;
  border-radius: var(--radius-xl);
  background-color: var(--color-surface-muted);
}

.toggle-group-item {
  all: unset;
  padding: 6px 12px;
  border-radius: var(--radius-xl);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  color: var(--input-color-label);
  cursor: pointer;
}

.toggle-group-item:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 1px;
}

.toggle-group-item[data-state='on'] {
  background-color: var(--color-surface);
  color: var(--color-text);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}
</style>
