<script setup lang="ts">
import { ref, watch, provide } from 'vue'
import { useRoute } from 'vue-router'
import { useScroll } from '@vueuse/core'
import { X } from '@lucide/vue'
import BottomNav from '@/shared/ui/components/BottomNav.vue'
import Sidebar from '@/shared/ui/components/Sidebar.vue'
import { SCROLL_KEY } from '@/shared/lib/useAppShellScroll'

const route = useRoute()
const drawerOpen = ref(false)

const contentRef = ref<HTMLElement | null>(null)
const scroll = useScroll(contentRef)

provide(SCROLL_KEY, scroll)

watch(() => route.fullPath, () => {
  drawerOpen.value = false
})
</script>

<template>
  <div class="app-shell">
    <Sidebar class="app-shell-sidebar-desktop" />

    <main ref="contentRef" class="app-shell-content">
      <RouterView />
    </main>

    <template v-if="!route.meta.hideNav">
      <BottomNav class="app-shell-bottom-nav" @more-click="drawerOpen = true" />

      <Teleport to="body">
        <div v-if="drawerOpen" class="drawer-overlay" @click="drawerOpen = false" />
        <div class="drawer" :class="{ open: drawerOpen }">
          <button type="button" class="drawer-close" aria-label="Close menu" @click="drawerOpen = false">
            <X :size="20" />
          </button>
          <Sidebar @navigate="drawerOpen = false" />
        </div>
      </Teleport>
    </template>
  </div>
</template>

<style scoped>
.app-shell {
  display: flex;
  height: 100dvh;
}

.app-shell-content {
  flex: 1;
  min-width: 0;
  min-height: 0;
  overflow-y: auto;
}

.app-shell-content.no-nav {
  padding-bottom: 0;
}

.app-shell-sidebar-desktop {
  display: none;
}

.app-shell-bottom-nav {
  display: flex;
}

.drawer-overlay {
  position: fixed;
  inset: 0;
  background-color: var(--color-app-backdrop);
  z-index: 200;
}

.drawer {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 260px;
  max-width: 80vw;
  background-color: var(--input-color-background);
  box-shadow: var(--shadow-md);
  z-index: 201;
  transform: translateX(-100%);
  transition: transform 200ms ease-out;
  padding-top: 12px;
}

.drawer.open {
  transform: translateX(0);
}

.drawer-close {
  all: unset;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  margin: 0 0 8px 12px;
  border-radius: var(--input-radius);
  cursor: pointer;
  color: var(--input-color-text);
}

.drawer-close:hover {
  background-color: var(--color-surface-muted);
}

@media (min-width: 768px) {
  .app-shell-sidebar-desktop {
    display: flex;
  }

  .app-shell-bottom-nav {
    display: none;
  }

  .app-shell-content {
    padding-bottom: 0;
  }

  .drawer,
  .drawer-overlay {
    display: none;
  }
}
</style>
