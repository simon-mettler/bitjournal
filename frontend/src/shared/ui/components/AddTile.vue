<script setup lang="ts">
import { Plus } from '@lucide/vue'
</script>

<template>
  <button type="button" class="add-tile">
    <Plus :size="20" />
    <slot />
  </button>
</template>

<style scoped>
.add-tile {
  all: unset;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  min-height: 75px;
  border-radius: var(--input-radius);
  border: 2px dashed var(--input-color-label);
  font-size: var(--font-size-sm);
  color: var(--input-color-label);
  cursor: pointer;
}

.add-tile:focus-visible {
  box-shadow: var(--input-shadow-focus);
}
</style>
