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
import { X, Lightbulb, Check, Flag } from '@lucide/vue'
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
      :type="item.variant === 'danger' ? 'foreground' : 'background'"
      @update:open="(open) => handleOpenChange(item.id, open)">
      <div class="toast-icon">
        <Lightbulb :size="20" v-if="item.variant == 'info'" />
        <Check :size="20" v-if="item.variant == 'success'" />
        <Flag :size="20" v-if="item.variant == 'warn'" />
        <X :size="20" v-if="item.variant == 'danger'" />
      </div>
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
  bottom: calc(85px + env(safe-area-inset-bottom));
  right: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 0;
  width: 100vw;
  list-style: none;
  z-index: 100;
  align-items: center;
}

.toast-root {
  display: grid;
  grid-template-areas:
    'icon title action close'
    'icon desc  action close';
  grid-template-rows: auto auto;
  grid-template-columns: 30px auto auto 48px;
  position: relative;
  gap: 0 12px;
  padding: 12px;
  border-radius: var(--input-radius);
  background-color: white;
  box-shadow: var(--shadow-md);
  border-left: 4px solid var(--color-primary);
  width: 70vw;
  max-width: 380px;
}

.toast-root:not(:has(.toast-title)) {
  grid-template-areas:
    'icon desc action close';
  grid-template-rows: auto;
}



.toast-icon {
  grid-area: icon;
  display: grid;
  place-self: center;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: 40px;

  &>svg {
    color: white;
  }
}


.info {
  &.toast-root {
    border: 1px solid var(--color-info);
    background-color: var(--color-info-bg);
  }

  .toast-icon {
    background-color: var(--color-info);
  }
}

.success {
  &.toast-root {
    border: 1px solid var(--color-success);
    background-color: var(--color-success-bg);
  }

  .toast-icon {
    background-color: var(--color-success);
  }
}

.warn {
  &.toast-root {
    border: 1px solid var(--color-warn);
    background-color: var(--color-warn-bg);
  }

  .toast-icon {
    background-color: var(--color-warn);
  }
}

.danger {

  &.toast-root {
    border: 1px solid var(--color-danger);
    background-color: var(--color-danger-bg);
  }

  .toast-icon {
    background-color: var(--color-danger);
  }
}

.toast-title {
  grid-area: title;
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-base);
  color: var(--color-text);
}

.toast-description {
  grid-area: desc;
  font-size: var(--font-size-sm);
  color: var(--color-text);
  align-self: center;
}

.toast-action {
  grid-area: action;
  all: unset;
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
  white-space: nowrap;
  grid-area: action;
  place-self: center;
}

.toast-close {
  all: unset;
  grid-area: close;
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
