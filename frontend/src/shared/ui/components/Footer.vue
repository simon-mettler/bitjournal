<script setup lang="ts">
</script>

<template>
  <div class="footer">
    <slot />
  </div>
</template>

<style scoped>
.footer {
  display: flex;
  gap: 16px;
  width: 100%;
  height: 82px;
  box-sizing: border-box;
  background-color: var(--color-surface);
  padding: var(--padding-app);
  padding-bottom: calc(var(--spacing-md) + env(safe-area-inset-bottom));
  box-shadow: var(--shadow-footer);
  border-radius: var(--radius-md) var(--radius-md) 0 0;
}

:deep(button) {
  flex: 1;
}
</style>
