<script setup lang="ts">
withDefaults(
  defineProps<{
    variant?: 'primary' | 'secondary' | 'tertiary' | 'warn' | 'float'
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
  border: 2px solid transparent;
  border-radius: var(--input-radius);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  line-height: 1;
  cursor: pointer;
  transition:
    transform 120ms ease,
    box-shadow 160ms ease,
    background-color 160ms ease;

  &:active:not(:disabled) {
    transform: translateY(1px) scale(0.985);
  }

  &:focus {
    box-shadow: var(--input-shadow-focus);
    border: var(--input-border-focus);
  }

  &:disabled {
    cursor: not-allowed;
    opacity: 0.5;
  }
}

.button.primary {
  background: var(--color-primary);
  color: var(--color-on-primary);

  &:hover:not(:disabled) {
    background: var(--color-primary-hover);
  }
}

.button.secondary {
  background-color: var(--input-color-background);
  color: var(--input-color-text);
  border: var(--button-border);
}

.button.tertiary {
  background-color: var(--color-primary-soft);
  color: var(--color-primary);
  border: 2px solid transparent;

  &:hover:not(:disabled) {
    background-color: color-mix(in srgb, var(--color-primary) 20%, transparent);
  }
}

.button.warn {
  background-color: var(--color-danger);
  color: #fff;
}

.button.float {
  color: var(--input-color-text);
  border-radius: var(--radius-xl);
  background-color: var(--color-surface);
  box-shadow: var(--shadow-glow);
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
