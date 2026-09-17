<script setup lang="ts">
import { Toggle as ToggleRoot } from 'reka-ui'

const pressed = defineModel<boolean>({ default: false })
</script>

<template>
  <ToggleRoot v-model="pressed" class="toggle">
    <slot />
  </ToggleRoot>
</template>

<style scoped>
.toggle {
  all: unset;
  padding: 6px 12px;
  border-radius: var(--radius-xl);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  color: var(--input-color-label);
  cursor: pointer;
}

.toggle[data-state='on'] {
  background-color: var(--color-surface);
  color: var(--color-text);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}
</style>
