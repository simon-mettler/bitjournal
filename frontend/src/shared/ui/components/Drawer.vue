<script setup lang="ts">
import { DrawerContent, DrawerHandle, DrawerOverlay, DrawerPortal, DrawerRoot, DrawerTitle } from 'reka-ui'

defineProps<{
  title: string
}>()

const open = defineModel<boolean>('open', { default: false })
</script>

<template>
  <DrawerRoot v-model:open="open">
    <DrawerPortal>
      <DrawerOverlay class="drawer-overlay" />
      <DrawerContent class="drawer-content">
        <DrawerHandle class="drawer-handle" />

        <div class="drawer-header">
          <span v-if="$slots.icon" class="drawer-header-icon">
            <slot name="icon" />
          </span>
          <DrawerTitle class="drawer-title">{{ title }}</DrawerTitle>
        </div>

        <div class="drawer-body">
          <slot />
        </div>

        <div class="drawer-footer">
          <slot name="footer" />
        </div>
      </DrawerContent>
    </DrawerPortal>
  </DrawerRoot>
</template>

<style scoped>
/* see https://reka-ui.com/docs/components/drawer#animating-the-drawer */
.drawer-overlay {
  background-color: var(--color-app-backdrop);
  position: fixed;
  inset: 0;
  z-index: 30;
}

.drawer-overlay[data-state='open'] {
  animation: drawerOverlayShow 450ms cubic-bezier(0.32, 0.72, 0, 1);
}

.drawer-overlay[data-state='closed'] {
  animation: drawerOverlayHide 450ms cubic-bezier(0.32, 0.72, 0, 1);
}

.drawer-header {
  display: flex;
  margin: 12px var(--spacing-lg) 0 var(--spacing-lg);
  gap: 10px;
}

/**
* --bleed: Extra drawer area that hangs below the viewport edge, kept off-screen
* by an equal negative margin. Pulling the drawer away from its edge slides the
* bleed into view instead of exposing the overlay behind it, so the drawer
* stretches rather than visually detaching while it rubber-bands.
*/
.drawer-content {
  --bleed: 48px;

  background-color: var(--drawer-color-background);
  border-radius: 16px 16px 0 0;
  position: fixed;
  inset-inline: 0;
  bottom: 0;
  margin-inline: auto;
  margin-bottom: calc(-1 * var(--bleed));
  padding-bottom: calc(env(safe-area-inset-bottom, 0px) + var(--bleed));
  max-width: 500px;
  display: flex;
  flex-direction: column;
  outline: none;
  z-index: 40;

  /* `--drawer-swipe-movement-y` is written by DrawerContent while dragging. */
  transform: translateY(var(--drawer-swipe-movement-y, 0px));
  transition: transform 450ms cubic-bezier(0.32, 0.72, 0, 1);
  will-change: transform;
}

/**
* Enter/exit keyframes animate the independent `translate` property so they
* compose with the inline `transform` carrying the live drag offset.
*/
.drawer-content[data-state='open'] {
  animation: drawerSlideBottomIn 450ms cubic-bezier(0.32, 0.72, 0, 1);
}

.drawer-content[data-state='closed'] {
  animation: drawerSlideBottomOut 450ms cubic-bezier(0.32, 0.72, 0, 1);
}

/**
* Silence the transform transition during an active drag so it tracks the
* pointer in real time.
*/
.drawer-content[data-swiping] {
  transition-duration: 0ms;
  user-select: none;
}

.drawer-handle {
  width: 48px;
  height: 6px;
  margin: 12px auto 0;
  flex-shrink: 0;
  border-radius: 9999px;
  background-color: var(--drawer-handle-color);
}

.drawer-body {
  padding: var(--spacing-lg);
}

.drawer-title {
  margin: 0;
  font-weight: 600;
  color: var(--color-text);
}

.drawer-footer {
  display: flex;
  margin: var(--spacing-lg);
  margin-top: 0;
  justify-content: flex-end;
}

@keyframes drawerOverlayShow {
  from {
    opacity: 0;
  }
}

@keyframes drawerOverlayHide {
  to {
    opacity: 0;
  }
}

/**
* The bleed already sits below the viewport edge, so the drawer only has to
* travel `height - bleed` to clear it. Translating a full 100% would overshoot
* by the bleed and make the slide look faster than it is.
*/
@keyframes drawerSlideBottomIn {
  from {
    translate: 0 calc(100% - var(--bleed));
  }
}

@keyframes drawerSlideBottomOut {
  to {
    translate: 0 calc(100% - var(--bleed));
  }
}
</style>
