<script setup lang="ts">
import { ref, watch } from 'vue'
import {
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from 'reka-ui'
import { X } from '@lucide/vue'

defineProps<{
  title: string
  description?: string
}>()

const open = ref<boolean>(false)

</script>

<template>
  <DialogRoot v-model:open="open">
    <DialogTrigger as-child>
      <slot name="trigger" />
    </DialogTrigger>
    <DialogPortal>
      <DialogOverlay class="dialog-overlay" />
      <DialogContent class="dialog-content">
        <DialogTitle class="dialog-title">
          {{ title }}
        </DialogTitle>
        <DialogDescription v-if="description" class="dialog-description">
          {{ description }}
        </DialogDescription>

        <div class="dialog-body">
          <slot />
        </div>

        <div class="dialog-footer">
          <slot name="footer" />
        </div>

        <DialogClose class="dialog-close" aria-label="Close">
          <X />
        </DialogClose>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>

<style scoped>
.dialog-overlay {
  z-index: 10;
  background-color: var(--color-app-backdrop);
  position: fixed;
  inset: 0;
  animation: overlayShow 700ms cubic-bezier(0.16, 1, 0.3, 1);
  overflow: hidden;
}

.dialog-content {
  z-index: 11;
  background-color: var(--dialog-color-background);
  border-radius: var(--dialog-radius);
  box-shadow: hsl(206 22% 7% / 35%) 0px 10px 38px -10px,
    hsl(206 22% 7% / 20%) 0px 10px 20px -15px;
  position: fixed;
  top: calc(var(--visual-viewport-offset-top) + var(--visual-viewport-height) / 2);
  left: 50%;
  transform: translate(-50%, -50%);
  width: 83vw;
  max-width: 450px;
  max-height: calc(var(--visual-viewport-height) - var(--spacing-md) - var(--spacing-md));
  padding: var(--dialog-padding);
  display: flex;
  flex-direction: column;
  animation: contentShow 600ms cubic-bezier(0.16, 1, 0.3, 1);
}

.dialog-body {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  overflow-y: auto;
  min-height: 0;
  padding: 4px;
  margin: -4px;
}

.dialog-title {
  margin: 0 0 var(--spacing-md) 0;
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
  font-size: var(--font-size-h1);
}

.dialog-description {
  margin: 0 0 var(--spacing-md) 0;
  color: var(--color-text);
  font-size: var(--font-size-base);
}

.dialog-footer {
  display: flex;
  margin-top: var(--dialog-padding);
  justify-content: flex-end;
  gap: var(--spacing-sm);
}

.dialog-close {
  font-family: inherit;
  border-radius: 100%;
  height: 40px;
  width: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text);
  position: absolute;
  top: var(--dialog-padding);
  right: var(--dialog-padding);
  background: none;
  border: none;
  cursor: pointer;
}

@keyframes overlayShow {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

@keyframes contentShow {
  from {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.5);
  }

  to {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
}
</style>
