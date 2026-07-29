<script setup lang="ts">
import type { Signal } from '@/modules/signals/types'

defineProps<{
  signal: Signal
}>()
</script>

<template>
  <div class="signal-card">
    <div class="signal-card-top">
      <span v-if="$slots.handle" class="signal-card-handle">
        <slot name="handle" />
      </span>
      <span class="signal-card-spacer" />
      <span v-if="$slots.actions" class="signal-card-actions">
        <slot name="actions" />
      </span>
    </div>

    <div class="signal-card-info">
      <span class="signal-card-name">{{ signal.name }}</span>
      <span class="signal-card-type">{{ signal.type }}</span>
    </div>
  </div>
</template>

<style scoped>
.signal-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px;
  border-radius: var(--input-radius);
  background-color: var(--input-color-background);
  box-shadow: var(--shadow-sm, var(--shadow-md));
}

.signal-card-top {
  display: flex;
  align-items: center;
}

.signal-card-spacer {
  flex: 1;
}

.signal-card-handle {
  display: inline-flex;
  color: var(--input-color-label);
  cursor: grab;
  touch-action: none;
}

.signal-card-handle:active {
  cursor: grabbing;
}

.signal-card-actions {
  display: inline-flex;
}

.signal-card-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.signal-card-name {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
}

.signal-card-type {
  font-size: var(--font-size-sm);
  color: var(--input-color-label);
  text-transform: capitalize;
}
</style>
