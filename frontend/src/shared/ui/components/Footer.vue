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
  position: fixed;
  gap: 16px;
  bottom: 0;
  width: 100%;
  box-sizing: border-box;
  background-color: var(--color-surface);
  padding: var(--padding-app);
  padding-bottom: calc(var(--spacing-md) + env(safe-area-inset-bottom));
}

:deep(button) {
  flex: 1;
}
</style>
