<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router'
import type { WidgetDefinition } from '@/modules/analytics/widgetRegistry'

defineProps<{
  definition: WidgetDefinition
  to: RouteLocationRaw
}>()
</script>

<template>
  <RouterLink :to="to" replace class="widget-type-card">
    <div class="preview">
      <component :is="definition.preview" />
    </div>
    <div class="text">
      <span class="name">{{ definition.name }}</span>
      <span class="description">{{ definition.description }}</span>
    </div>
  </RouterLink>
</template>

<style scoped>
.widget-type-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  border: 2px solid transparent;
  border-radius: var(--input-radius);
  background-color: var(--color-surface);
  box-shadow: var(--shadow-card);
  color: var(--color-text);
  text-decoration: none;
  transition: border-color 160ms ease;
}

.widget-type-card:hover {
  border-color: var(--color-primary-border);
}

.widget-type-card:focus-visible {
  outline: none;
  box-shadow: var(--input-shadow-focus);
}

.preview {
  flex-shrink: 0;
  width: 112px;
  padding: var(--spacing-xs);
  border-radius: var(--radius-sm);
  background-color: var(--color-surface-muted);
}

.preview :deep(svg) {
  display: block;
  width: 100%;
}

.text {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  min-width: 0;
}

.name {
  font-weight: var(--font-weight-bold);
}

.description {
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
}

@media (min-width: 768px) {
  .widget-type-card {
    flex-direction: column;
    align-items: stretch;
  }

  .preview {
    width: auto;
  }
}
</style>
