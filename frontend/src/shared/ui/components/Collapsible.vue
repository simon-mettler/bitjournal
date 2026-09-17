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
      <span class="collapsible-title">{{ title }}</span>
      <slot name="actions" />
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
  border: 1px solid #87BBC5;
  border-radius: var(--radius-md);
  background: var(--color-surface);
  overflow: hidden;
}

.collapsible-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-md);
}

.collapsible-trigger {
  all: unset;
  flex: 1;
  align-self: stretch;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  cursor: pointer;
}

.collapsible-title {
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-sm);
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
  padding: var(--spacing-sm) var(--spacing-md) var(--spacing-md);
  overflow: hidden;
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
