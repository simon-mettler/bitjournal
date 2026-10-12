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
  // eslint-disable-next-line @typescript-eslint/no-unnecessary-type-assertion -- needed by vue-tsc for generic T
  if (typeof value === 'string' && value) model.value = value as T
}
</script>

<template>
  <ToggleGroupRoot
    type="single"
    :model-value="model"
    class="toggle-group"
    @update:model-value="onUpdate"
  >
    <ToggleGroupItem
      v-for="option in options"
      :key="option.value"
      :value="option.value"
      class="toggle-group-item"
    >
      {{ option.label }}
    </ToggleGroupItem>
  </ToggleGroupRoot>
</template>

<style scoped>
.toggle-group {
  display: flex;
  gap: 2px;
  padding: 4px;
  border: 1px solid #eee;
  border-radius: calc(var(--radius-md) - 2px);
  background-color: var(--color-surface);
}

.toggle-group-item {
  all: unset;
  padding: 5px 6px;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  color: var(--input-color-label);
  cursor: pointer;
}

.toggle-group-item:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 1px;
}

.toggle-group-item[data-state='on'] {
  background-color: var(--color-primary);
  color: var(--color-surface);
  box-shadow:
    0 0 0 1px color-mix(in srgb, var(--color-text) 8%, transparent),
    0 1px 3px rgba(0, 0, 0, 0.12);
}
</style>
