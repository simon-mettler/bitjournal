<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft } from '@lucide/vue'
import NavContent from '@/shared/ui/layout/NavContent.vue'
import IconButton from '@/shared/ui/components/IconButton.vue'

const route = useRoute()
const drawerOpen = ref(false)

watch(() => route.fullPath, () => {
  drawerOpen.value = false
})

function open() { drawerOpen.value = true }
function close() { drawerOpen.value = false }

defineExpose({ open, close })
</script>

<template>
  <NavContent class="app-sidebar-rail" />

  <template v-if="!route.meta.hideNav">
    <Teleport to="body">
      <div v-if="drawerOpen" class="drawer-backdrop" @click="close" />
      <div class="drawer" :class="{ open: drawerOpen }">
        <IconButton variant="tertiary" class="drawer-close" aria-label="Close menu" @click="close">
          <ArrowLeft />
        </IconButton>
        <NavContent @navigate="close" />
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
  background-color: none;
  z-index: 200;
}

.drawer {
  padding: var(--spacing-lg);
  padding-bottom: max(10px, env(safe-area-inset-bottom));
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

.drawer.open {
  transform: translateX(0);
}

.drawer-close {
  position: absolute;
  right: var(--spacing-lg);
  bottom: max(10px, env(safe-area-inset-bottom));
}

@media (min-width: 768px) {
  .app-sidebar-rail {
    display: flex;
  }

  .drawer,
  .drawer-backdrop {
    display: none;
  }
}
</style>
