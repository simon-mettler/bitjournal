<script setup lang="ts">
import { ref, provide } from 'vue'
import { useRoute } from 'vue-router'
import { useScroll } from '@vueuse/core'
import NavBottom from '@/shared/ui/layout/NavBottom.vue'
import NavSidebar from '@/shared/ui/layout/NavSidebar.vue'
import { SCROLL_KEY } from '@/shared/lib/useAppShellScroll'
import { APP_SHELL_HEADER_ID, APP_SHELL_FOOTER_ID } from '@/shared/lib/appShellSlots'

const route = useRoute()
const contentRef = ref<HTMLElement | null>(null)
const sidebar = ref<InstanceType<typeof NavSidebar> | null>(null)
const scroll = useScroll(contentRef)
provide(SCROLL_KEY, scroll)
</script>

<template>
  <div class="app-shell">
    <NavSidebar ref="sidebar" />

    <div class="app-shell-main">
      <header :id="APP_SHELL_HEADER_ID" class="app-shell-header" />

      <main ref="contentRef" class="app-shell-content">
        <RouterView />
      </main>

      <footer :id="APP_SHELL_FOOTER_ID" class="app-shell-footer" />

      <template v-if="!route.meta.hideNav">
        <NavBottom class="app-shell-bottom-nav" @more-click="sidebar?.open()" />
      </template>
    </div>
  </div>
</template>

<style scoped>
.app-shell {
  display: flex;
  height: 100dvh;
}

.app-shell-main {
  display: grid;
  grid-template-areas:
    "header"
    "content"
    "footer"
    "bottom-nav";
  grid-template-rows: auto minmax(0, 1fr) auto auto;
  flex: 1;
  min-width: 0;
  min-height: 0;
}

.app-shell-header {
  grid-area: header;
}

.app-shell-content {
  overflow-y: auto;
  min-height: 0;
  grid-area: content;
}

.app-shell-footer {
  grid-area: footer;
}

.app-shell-bottom-nav {
  display: flex;
  grid-area: bottom-nav;
}

@media (min-width: 768px) {
  .app-shell-bottom-nav {
    display: none;
  }
}
</style>
