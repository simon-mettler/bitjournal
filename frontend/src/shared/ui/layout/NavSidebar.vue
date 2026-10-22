<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import NavContent from '@/shared/ui/layout/NavContent.vue'

const route = useRoute()
const drawerOpen = ref(false)
const drawerNav = ref<{ replayLogo: () => void } | null>(null)

watch(
  () => route.fullPath,
  () => {
    drawerOpen.value = false
  },
)

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
  <NavContent class="app-sidebar-rail" />

  <template v-if="!route.meta.hideNav">
    <Teleport to="body">
      <div v-if="drawerOpen" class="drawer-backdrop" @click="close" />
      <div class="drawer" :class="{ open: drawerOpen }">
        <NavContent ref="drawerNav" @navigate="close" />
      </div>
    </Teleport>
  </template>
</template>

<style scoped>
.app-sidebar-rail {
  display: none;
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

@media (min-width: 768px) {
  .app-sidebar-rail {
    display: flex;
    flex: 0 0 248px;
    box-sizing: border-box;
    padding: var(--spacing-lg) var(--spacing-md);
    background-color: var(--color-app-bg);
    overflow-y: auto;
    z-index: 4;
  }

  .drawer,
  .drawer-backdrop {
    display: none;
  }
}
</style>
