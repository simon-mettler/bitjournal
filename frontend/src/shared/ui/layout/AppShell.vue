<script setup lang="ts">
import { ref, provide } from 'vue'
import { useRoute } from 'vue-router'
import { useScroll } from '@vueuse/core'
import NavBottom from '@/shared/ui/layout/NavBottom.vue'
import { useAuthStore } from '@/modules/authentication/store'
import DesktopNotice from '@/shared/ui/components/DesktopNotice.vue'
import { Menu } from '@lucide/vue'
import IconButton from '@/shared/ui/components/IconButton.vue'
import NavSidebar from '@/shared/ui/layout/NavSidebar.vue'
import { SCROLL_KEY } from '@/shared/lib/useAppShellScroll'
import { APP_SHELL_HEADER_ID, APP_SHELL_FOOTER_ID } from '@/shared/lib/appShellSlots'

const route = useRoute()
const auth = useAuthStore()
const contentRef = ref<HTMLElement | null>(null)
const sidebar = ref<{ open: () => void } | null>(null)
const scroll = useScroll(contentRef)
provide(SCROLL_KEY, scroll)
</script>

<template>
  <div class="app-shell">
    <template v-if="auth.isAuthenticated">
      <NavSidebar ref="sidebar" />
      <IconButton
        v-if="!route.meta.hideNav"
        variant="tertiary"
        class="app-shell-menu"
        aria-label="Open menu"
        @click="sidebar?.open()"
      >
        <Menu />
      </IconButton>
    </template>

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

    <DesktopNotice />
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
    'header'
    'content'
    'footer'
    'bottom-nav';
  grid-template-columns: minmax(0, 1fr);
  grid-template-rows: auto minmax(0, 1fr) auto auto;
  flex: 1;
  min-width: 0;
  min-height: 0;
}

.app-shell-menu {
  display: none;
}

@media (min-width: 768px) {
  .app-shell {
    justify-content: center;
  }

  .app-shell-main {
    max-width: 600px;
  }

  .app-shell-menu {
    display: inline-flex;
    position: fixed;
    top: var(--spacing-md);
    left: var(--spacing-md);
    z-index: 5;
  }
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
</style>
