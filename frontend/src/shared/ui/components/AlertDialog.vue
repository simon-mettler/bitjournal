<script setup lang="ts">
import Button from '@/shared/ui/components/Button.vue'
import {
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogOverlay,
  AlertDialogPortal,
  AlertDialogRoot,
  AlertDialogTitle,
  AlertDialogTrigger,
} from 'reka-ui'

defineProps<{
  title: string
  description?: string
  confirmText: string
}>()

const emit = defineEmits<{
  confirm: []
}>()

const open = defineModel<boolean>('open', { default: false })
</script>

<template>
  <AlertDialogRoot v-model:open="open">
    <AlertDialogTrigger v-if="$slots.trigger" as-child>
      <slot name="trigger" />
    </AlertDialogTrigger>
    <AlertDialogPortal>
      <AlertDialogOverlay class="dialog-overlay" />
      <AlertDialogContent class="dialog-content">
        <AlertDialogTitle class="dialog-title">
          {{ title }}
        </AlertDialogTitle>
        <AlertDialogDescription v-if="description" class="dialog-description">
          {{ description }}
        </AlertDialogDescription>
        <div class="dialog-body">
          <slot />
        </div>
        <div class="dialog-footer">
          <AlertDialogCancel as-child>
            <Button variant="secondary">Cancel</Button>
          </AlertDialogCancel>
          <AlertDialogAction as-child>
            <Button variant="warn" @click="emit('confirm')">{{ confirmText }}</Button>
          </AlertDialogAction>
        </div>
      </AlertDialogContent>
    </AlertDialogPortal>
  </AlertDialogRoot>
</template>

<style scoped>
.dialog-overlay {
  z-index: 10;
  backdrop-filter: var(--backdrop-blur);
  position: fixed;
  inset: 0;
  animation: overlayShow 1000ms cubic-bezier(0.16, 1, 0.3, 1);
}

.dialog-content {
  z-index: 11;
  --input-color-background: var(--color-surface-muted);
  --input-shadow: none;
  background-color: var(--dialog-color-background);
  backdrop-filter: var(--glass-filter-overlay);
  border-radius: var(--dialog-radius);
  box-shadow: var(--shadow-lg);
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 83vw;
  max-width: 450px;
  padding: var(--dialog-padding);
  animation: contentShow 400ms cubic-bezier(0.16, 1, 0.3, 1);
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

.dialog-body {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.dialog-footer {
  display: flex;
  margin-top: var(--dialog-padding);
  gap: var(--spacing-sm);
}

.dialog-footer > :deep(*) {
  flex: 1 1 0;
  min-width: 0;
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
