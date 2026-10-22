<script setup lang="ts">
import Logo from '@/shared/ui/components/Logo.vue'
</script>

<template>
  <div class="auth-logo">
    <Logo />
  </div>
</template>

<style scoped>
.auth-logo {
  display: flex;
  justify-content: center;
  padding: var(--spacing-xl) var(--padding-app) var(--spacing-sm);
}

.auth-logo :deep(.logo) {
  width: min(240px, 70vw);
}
</style>
