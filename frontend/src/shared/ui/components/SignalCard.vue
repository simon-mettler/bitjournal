<script setup lang="ts">
import type { Signal } from '@/modules/signals/types'

withDefaults(
  defineProps<{
    signal: Signal
    colored?: boolean
  }>(),
  {
    colored: false,
  },
)

const emit = defineEmits<{
  select: []
}>()
</script>

<template>
  <div
    class="signal-card"
    :class="{ colored }"
    :style="{ '--card-signal-color': signal.color }"
    @click="emit('select')"
  >
    <div class="signal-card-top">
      <span v-if="$slots.handle" class="signal-card-handle">
        <slot name="handle" />
      </span>
      <span v-else-if="$slots.icon" class="signal-card-icon">
        <slot name="icon" />
      </span>
      <span class="signal-card-spacer" />
      <span v-if="$slots.actions" class="signal-card-actions">
        <slot name="actions" />
      </span>
    </div>

    <div class="signal-card-info">
      <span class="signal-card-name">{{ signal.name }}</span>
    </div>
  </div>
</template>

<style scoped>
.signal-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 58px;
  padding: 10px 7px 14px 14px;
  border-radius: var(--input-radius);
  background-color: var(--color-surface);
  border: 1px solid var(--color-surface-muted);
  cursor: pointer;
  box-shadow: var(--shadow-card);
}

.signal-card.colored {
  background-color: oklab(from var(--card-signal-color) l a b / 0.1);
  border-color: oklab(from var(--card-signal-color) l a b / 0.7);
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

.signal-card-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
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
