<script setup lang="ts">
import { useAppShellScroll } from '@/shared/lib/useAppShellScroll'
const { arrivedState } = useAppShellScroll()

defineProps<{
  heading: string
}>()
</script>

<template>
  <div :class="{ scrolled: !arrivedState.top }" class="header">
    <div class="header-heading">
      <h1>{{ heading }}</h1>
      <div class="header-actions">
        <slot name="actions" />
      </div>
    </div>
    <div class="header-content">
      <slot name="content" />
    </div>
  </div>
</template>

<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-direction: column;
  position: relative;
  z-index: 2;
  background-color: var(--header-color-background);
  padding: var(--padding-app);
  box-sizing: border-box;
  max-width: 100vw;
  transition: box-shadow 200ms ease;
}

.header-heading {
  display: flex;
  width: 100%;
  justify-content: space-between;
  align-items: center;
}

.header-content {
  width: 100%;
}

.header h1 {
  color: var(--header-color-heading);
  margin: 0;
  font-weight: var(--font-weight-bold);
}

.header.scrolled {
  box-shadow: var(--shadow-md);
}
</style>
