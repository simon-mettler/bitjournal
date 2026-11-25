<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import NavContent from '@/shared/ui/layout/NavContent.vue'
import { useIsDesktopUp, useIsTabletUp } from '@/shared/lib/useBreakpoint'

const route = useRoute()
const isTablet = useIsTabletUp()
const isDesktop = useIsDesktopUp()
const drawerOpen = ref(false)
const drawerNav = ref<{ replayLogo: () => void } | null>(null)

watch(
  () => route.fullPath,
  () => {
    drawerOpen.value = false
  },
)

// the drawer only exists on mobile; close it if the viewport grows past it
watch(isTablet, (tablet) => {
  if (tablet) drawerOpen.value = false
})

watch(drawerOpen, (isOpen) => {
  if (isOpen) drawerNav.value?.replayLogo()
})

function open() {
  drawerOpen.value = true
}
function close() {
  drawerOpen.value = false
}

defineExpose({ open, close })
</script>

<template>
  <template v-if="!route.meta.hideNav">
    <!-- tablet/desktop: persistent navigation (rail, then full sidebar) -->
    <aside v-if="isTablet" class="sidebar" :class="{ rail: !isDesktop }">
      <NavContent persistent :rail="!isDesktop" />
    </aside>

    <!-- mobile: "More" drawer -->
    <Teleport v-else to="body">
      <div v-if="drawerOpen" class="drawer-backdrop" @click="close" />
      <div class="drawer" :class="{ open: drawerOpen }">
        <NavContent ref="drawerNav" @navigate="close" />
      </div>
    </Teleport>
  </template>
</template>

<style scoped>
.sidebar {
  flex: none;
  width: var(--nav-width);
  box-sizing: border-box;
  padding: var(--spacing-lg) var(--spacing-md);
  overflow-y: auto;
  background-color: var(--color-app-bg);
  border-right: 1px solid var(--color-border);
}

.sidebar.rail {
  padding-inline: var(--spacing-sm);
}

.sidebar :deep(.nav-content) {
  min-height: 100%;
}

.drawer-backdrop {
  position: fixed;
  inset: 0;
  backdrop-filter: var(--backdrop-blur);
  z-index: 200;
}

.drawer {
  padding: var(--spacing-lg);
  padding-bottom: max(56px, env(safe-area-inset-bottom));
  box-sizing: border-box;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 280px;
  max-width: 80vw;
  background-color: var(--color-app-bg);
  box-shadow: var(--shadow-md);
  z-index: 201;
  transform: translateX(-100%);
  transition: transform 200ms ease-out;
}

.drawer :deep(.nav-content) {
  height: 100%;
}

.drawer.open {
  transform: translateX(0);
}
</style>
