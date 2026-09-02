<script setup lang="ts">
import { X } from '@lucide/vue'
import type { Signal } from '@/modules/signals/types'

withDefaults(defineProps<{
  signal: Signal
  value: string | null
  clickable?: boolean
  removable?: boolean
}>(), {
  clickable: false,
  removable: false,
})

const emit = defineEmits<{
  click: []
  remove: []
}>()
</script>

<template>
  <component :is="clickable ? 'button' : 'span'" class="signal-chip" :type="clickable ? 'button' : undefined"
    @click="clickable && emit('click')">
    <span class="signal-chip-dot" :style="{ backgroundColor: signal.color }" />
    <span class="signal-chip-value" :class="{ 'value-padding': !removable }">{{ value }}</span>
    <button v-if="removable" type="button" class="signal-chip-remove" :aria-label="`Remove ${signal.name}`"
      @click.stop="emit('remove')">
      <X />
    </button>
  </component>
</template>

<style scoped>
.signal-chip {
  all: unset;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding-left: 11px;
  border-radius: var(--radius-xl);
  background-color: var(--color-surface-muted);
  font-size: var(--font-size-sm);
  color: var(--color-text);
  cursor: pointer;
  height: 36px;
}

.signal-chip-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  flex-shrink: 0;
}

.signal-chip-remove {
  all: unset;
  display: inline-flex;
  align-items: center;
  justify-items: center;
  color: var(--input-color-label);
  height: 36px;
  width: 31px;
}

.value-padding {
  padding-right: 12px;
}
</style>
