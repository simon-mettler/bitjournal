<script setup lang="ts">
import { useAppShellScroll } from '@/shared/lib/useAppShellScroll'
const { arrivedState } = useAppShellScroll()

defineProps<{
  heading: string
}>()
</script>

<template>
  <div :class="{ 'scrolled': !arrivedState.top }" class="header">
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
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-direction: column;
  border-bottom: 2px solid transparent;
  background-color: var(--color-app-bg);
  padding: var(--padding-app);

  transition:
    box-shadow 150ms ease,
    border-color 150ms ease;
}

.header-heading {
  display: flex;
  width: 100%;
  justify-content: space-between;
}

.header-content {
  width: 100%;
}

.header h1 {
  color: var(--color-primary);
  margin: 0;
}

.header.scrolled {
  border-bottom: 2px solid #cbcbcb;
  box-shadow: 0 2px 8px rgb(0 0 0 / 8%);
}
</style>
