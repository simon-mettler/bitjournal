<script setup lang="ts">
import { ChevronDown } from '@lucide/vue'
import { CollapsibleContent, CollapsibleRoot, CollapsibleTrigger } from 'reka-ui'
import { ref } from 'vue'

defineProps<{
  title: string
}>()

const open = ref(false)
</script>

<template>
  <CollapsibleRoot v-model:open="open" class="collapsible">
    <div class="collapsible-header">
      <slot name="icon" />
      <span class="collapsible-title">{{ title }}</span>
      <div class="collapsible-actions">
        <slot name="actions" />
      </div>
      <CollapsibleTrigger class="collapsible-trigger">
        <ChevronDown class="collapsible-icon" :class="{ 'is-open': open }" />
      </CollapsibleTrigger>
    </div>

    <CollapsibleContent class="collapsible-content">
      <slot />
    </CollapsibleContent>
  </CollapsibleRoot>
</template>

<style scoped>
.collapsible {
  border-radius: var(--radius-md);
  background: var(--color-surface);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

.collapsible-header {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-md);
}

.collapsible-actions {
  position: relative;
  z-index: 1;
  margin-left: auto;
}

.collapsible-trigger {
  all: unset;
  display: flex;
  align-items: center;
  cursor: pointer;
}

/* Stretch the click target over the whole header (title included) */
.collapsible-trigger::before {
  content: '';
  position: absolute;
  inset: 0;
}

.collapsible-title {
  font-weight: var(--font-weight-bold);
  font-size: 1.15rem;
  color: var(--color-text);
}

.collapsible-icon {
  flex-shrink: 0;
  width: 18px;
  height: 18px;
  color: var(--input-color-label);
  transition: transform 200ms ease;
}

.collapsible-icon.is-open {
  transform: rotate(180deg);
}

.collapsible-content {
  padding: 0 var(--spacing-md) var(--spacing-md);
  overflow: hidden;
}

/* Divider between header and content */
.collapsible-content::before {
  content: '';
  display: block;
  height: 1px;
  margin-bottom: var(--spacing-md);
  background: var(--input-color-border);
}

.collapsible-content[data-state='open'] {
  animation: collapsible-expand 220ms ease-out;
}

.collapsible-content[data-state='closed'] {
  animation: collapsible-collapse 220ms ease-out;
}

@keyframes collapsible-expand {
  from {
    height: 0;
  }

  to {
    height: var(--reka-collapsible-content-height);
  }
}

@keyframes collapsible-collapse {
  from {
    height: var(--reka-collapsible-content-height);
  }

  to {
    height: 0;
  }
}
</style>
