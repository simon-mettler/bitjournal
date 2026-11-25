<script setup lang="ts">
import { computed, ref, provide, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useScroll } from '@vueuse/core'
import NavBottom from '@/shared/ui/layout/NavBottom.vue'
import { useAuthStore } from '@/modules/authentication/store'
import NavSidebar from '@/shared/ui/layout/NavSidebar.vue'
import { SCROLL_KEY } from '@/shared/lib/useAppShellScroll'
import { APP_SHELL_HEADER_ID, APP_SHELL_FOOTER_ID } from '@/shared/lib/appShellSlots'

const route = useRoute()
const auth = useAuthStore()
const contentRef = ref<HTMLElement | null>(null)
const sidebar = ref<{ open: () => void } | null>(null)
const scroll = useScroll(contentRef)
provide(SCROLL_KEY, scroll)

const showNav = computed(() => auth.isAuthenticated && !route.meta.hideNav)

watch(
  () => route.fullPath,
  () => {
    if (contentRef.value) contentRef.value.scrollTop = 0
  },
)
</script>

<template>
  <div class="app-shell" :class="{ 'has-nav': showNav, 'is-wide': route.meta.wide }">
    <NavSidebar v-if="auth.isAuthenticated" ref="sidebar" />

    <div class="app-shell-main">
      <header :id="APP_SHELL_HEADER_ID" class="app-shell-header" />

      <main ref="contentRef" class="app-shell-content">
        <RouterView v-slot="{ Component }">
          <KeepAlive include="JournalView">
            <component :is="Component" />
          </KeepAlive>
        </RouterView>
      </main>

      <footer :id="APP_SHELL_FOOTER_ID" class="app-shell-footer" />

      <NavBottom
        v-if="!route.meta.hideNav"
        class="app-shell-bottom-nav"
        @more-click="sidebar?.open()"
      />
    </div>
  </div>
</template>

<style scoped>
.app-shell {
  --nav-width: 0px;
  --content-max: 640px;
  display: flex;
  height: 100dvh;
}

.app-shell.is-wide {
  --content-max: 1080px;
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

.app-shell-header {
  grid-area: header;
}

.app-shell-content {
  overflow-y: auto;
  min-height: 0;
  grid-area: content;
  padding-inline: max(0px, calc((100% - var(--content-max)) / 2));
}

.app-shell-footer {
  grid-area: footer;
}

.app-shell-bottom-nav {
  display: flex;
  grid-area: bottom-nav;
}

/* tablet: nav rail replaces the bottom nav */
@media (min-width: 768px) {
  .app-shell.has-nav {
    --nav-width: 88px;
  }

  .app-shell-bottom-nav {
    display: none;
  }
}

/* desktop: full sidebar */
@media (min-width: 1024px) {
  .app-shell.has-nav {
    --nav-width: 248px;
  }
}
</style>
