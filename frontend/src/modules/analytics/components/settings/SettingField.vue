<script setup lang="ts">
defineProps<{ label: string }>()
</script>

<template>
  <div class="field">
    <span class="label">{{ label }}</span>
    <slot />
  </div>
</template>

<style scoped>
.field {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.label {
  font-size: var(--font-size-sm);
  padding-left: 8px;
  margin-bottom: 6px;
  color: var(--input-color-label);
}
</style>
