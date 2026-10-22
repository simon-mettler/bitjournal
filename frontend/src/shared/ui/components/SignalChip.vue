<script setup lang="ts">
import { X } from '@lucide/vue'
import { computed } from 'vue'
import type { Signal } from '@/modules/signals/types'
import { resolveIcon } from '@/shared/lib/iconRegistry'

const props = withDefaults(
  defineProps<{
    signal: Signal
    value: string | null
    clickable?: boolean
    removable?: boolean
    colored?: boolean
  }>(),
  {
    clickable: false,
    removable: false,
    colored: false,
  },
)

const emit = defineEmits<{
  click: []
  remove: []
}>()

const icon = computed(() => resolveIcon(props.signal.icon))
</script>

<template>
  <component
    :is="clickable ? 'button' : 'span'"
    class="signal-chip"
    :class="{ colored }"
    :style="{ '--chip-signal-color': signal.color }"
    :type="clickable ? 'button' : undefined"
    @click="clickable && emit('click')"
  >
    <component :is="icon" v-if="icon" class="signal-chip-icon" :style="{ color: signal.color }" />
    <span v-else class="signal-chip-dot" :style="{ backgroundColor: signal.color }" />
    <span class="signal-chip-value" :class="{ 'value-padding': !removable }">{{ value }}</span>
    <button
      v-if="removable"
      type="button"
      class="signal-chip-remove"
      :aria-label="`Remove ${signal.name}`"
      @click.stop="emit('remove')"
    >
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
  padding-left: 9px;
  border-radius: var(--radius-xl);
  background-color: var(--input-color-background);
  box-sizing: border-box;
  border: var(--chip-border);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text);
  cursor: pointer;
  height: 33px;
}

.signal-chip.colored {
  background-image: linear-gradient(
    oklab(from var(--chip-signal-color) l a b / 0.16),
    oklab(from var(--chip-signal-color) l a b / 0.16)
  );
}

.signal-chip-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  flex-shrink: 0;
}

.signal-chip-icon {
  width: 21px;
  height: 21px;
  flex-shrink: 0;
}

.signal-chip-remove {
  all: unset;
  display: inline-flex;
  align-items: center;
  justify-items: center;
  color: var(--color-text);
  opacity: 0.8;
  height: 36px;
  width: 29px;

  & > svg {
    width: 20px;
    height: 20px;
  }
}

.value-padding {
  padding-right: 12px;
}
</style>
