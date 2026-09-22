<script setup lang="ts">
withDefaults(
  defineProps<{
    type?: 'button' | 'submit' | 'reset'
    disabled?: boolean
    variant?: 'primary' | 'secondary' | 'tertiary' | 'float'
    size?: 'lg' | 'sm'
  }>(),
  {
    type: 'button',
    variant: 'primary',
    size: 'lg',
  }
)
</script>

<template>
  <button :type="type" class="button" :class="variant, size" :disabled="disabled">
    <slot />
  </button>
</template>

<style scoped>
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 2px solid transparent;
  border-radius: var(--input-radius);
  cursor: pointer;

  &:focus {
    box-shadow: var(--input-shadow-focus);
    border: var(--input-border-focus);
  }

  &:disabled {
    cursor: not-allowed;
    opacity: 0.5;
  }
}

.button.lg {
  height: var(--input-height);
  width: var(--input-height);
}

.button.sm {
  height: 36px;
  width: 36px;
}

.button.primary {
  background-color: var(--color-primary);
  color: var(--color-surface);
}

.button.secondary {
  background-color: var(--color-surface);
  color: var(--input-color-text);
  border: var(--input-border);
}

.button.tertiary {
  color: var(--input-color-text);
  background-color: transparent;
}

.button.float {
  color: var(--input-color-text);
  border-radius: var(--radius-xl);
  background-color: var(--color-surface);
  box-shadow: var(--shadow-interact);
}

:deep(svg) {
  color: var(--input-color-label);
}
</style>
