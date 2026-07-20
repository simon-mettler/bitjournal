<script setup lang="ts">
withDefaults(
  defineProps<{
    variant?: 'primary' | 'secondary'
    disabled?: boolean
    type?: 'button' | 'submit' | 'reset'
  }>(),
  {
    variant: 'primary',
    type: 'button',
  },
)
</script>

<template>
  <button :type="type" class="button" :class="variant" :disabled="disabled">
    <span v-if="$slots.icon" class="button-icon">
      <slot name="icon" />
    </span>
    <slot />
  </button>
</template>

<style scoped>
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: var(--input-height);
  padding: 0 14px;
  border-radius: var(--input-radius);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-normal);
  line-height: 1;
  cursor: pointer;
  border: none;

  &:focus-visible {
    box-shadow: var(--input-shadow-focus);
  }

  &:disabled {
    cursor: not-allowed;
    opacity: 0.5;
  }
}

.button.primary {
  background-color: var(--color-primary);
  color: var(--color-surface);
}

.button.secondary {
  background-color: var(--input-color-background);
  color: var(--input-color-text);
  border: var(--input-border);

  &:focus {
    border: var(--input-border-focus);
  }
}

.button-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.button-icon :deep(svg) {
  width: 16px;
  height: 16px;
}
</style>
