<script setup lang="ts">
import {
  ToastAction,
  ToastClose,
  ToastDescription,
  ToastProvider,
  ToastRoot,
  ToastTitle,
  ToastViewport,
} from 'reka-ui'
import { X } from '@lucide/vue'
import { useToast } from '@/shared/lib/useToast'

const { toasts, dismiss } = useToast()

// keep the item mounted long enough for the closed-state CSS animation to play
function handleOpenChange(id: number, open: boolean) {
  if (!open) {
    setTimeout(() => dismiss(id), 200)
  }
}
</script>

<template>
  <ToastProvider swipe-direction="right">
    <ToastRoot v-for="item in toasts" :key="item.id" class="toast-root" :class="item.variant" :duration="item.duration"
      :type="item.variant === 'error' ? 'foreground' : 'background'"
      @update:open="(open) => handleOpenChange(item.id, open)">
      <ToastTitle v-if="item.title" class="toast-title">
        {{ item.title }}
      </ToastTitle>
      <ToastDescription class="toast-description">
        {{ item.description }}
      </ToastDescription>

      <ToastAction v-if="item.onAction" as-child :alt-text="item.actionAltText ?? item.actionLabel ?? 'Action'">
        <button type="button" class="toast-action" @click="item.onAction?.()">
          {{ item.actionLabel }}
        </button>
      </ToastAction>

      <ToastClose class="toast-close" aria-label="Close">
        <X :size="16" aria-hidden="true" />
      </ToastClose>
    </ToastRoot>

    <ToastViewport class="toast-viewport" />
  </ToastProvider>
</template>

<style>
.toast-viewport {
  position: fixed;
  bottom: 0;
  right: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 16px;
  width: 380px;
  max-width: 100vw;
  list-style: none;
  z-index: 100;
}

.toast-root {
  position: relative;
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 4px 12px;
  padding: 14px 16px;
  border-radius: var(--input-radius);
  background-color: white;
  box-shadow: var(--shadow-md);
  border-left: 4px solid var(--color-primary);
}

.toast-root.success {
  border-left-color: var(--color-success, #16a34a);
}

.toast-root.error {
  border-left-color: var(--color-danger);
}

.toast-title {
  grid-column: 1 / 2;
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-base);
  color: var(--color-text);
}

.toast-description {
  grid-column: 1 / 2;
  font-size: var(--font-size-sm);
  color: var(--color-text);
}

.toast-action {
  grid-column: 2 / 3;
  grid-row: 1 / 3;
  all: unset;
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
  white-space: nowrap;
}

.toast-close {
  all: unset;
  grid-column: 3 / 4;
  grid-row: 1 / 3;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--color-text);
}

.toast-root[data-state="open"] {
  animation: toast-in 200ms ease-out;
}

.toast-root[data-state="closed"] {
  animation: toast-out 200ms ease-in;
}

.toast-root[data-swipe="move"] {
  transform: translateX(var(--reka-toast-swipe-move-x));
}

.toast-root[data-swipe="cancel"] {
  transform: translateX(0);
  transition: transform 200ms ease-out;
}

.toast-root[data-swipe="end"] {
  animation: toast-swipe-out 150ms ease-out;
}

@keyframes toast-in {
  from {
    opacity: 0;
    transform: translateX(16px);
  }

  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes toast-out {
  from {
    opacity: 1;
  }

  to {
    opacity: 0;
  }
}

@keyframes toast-swipe-out {
  from {
    transform: translateX(var(--reka-toast-swipe-end-x));
  }

  to {
    transform: translateX(100%);
  }
}

@media (prefers-reduced-motion: reduce) {

  .toast-root[data-state],
  .toast-root[data-swipe="end"] {
    animation: none;
  }
}
</style>
