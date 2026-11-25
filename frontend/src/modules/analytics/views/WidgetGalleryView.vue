<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import Button from '@/shared/ui/components/Button.vue'
import Header from '@/shared/ui/components/Header.vue'
import Footer from '@/shared/ui/components/Footer.vue'
import AppShellHeader from '@/shared/ui/layout/AppShellHeader.vue'
import AppShellFooter from '@/shared/ui/layout/AppShellFooter.vue'
import WidgetCard from '@/modules/analytics/components/WidgetCard.vue'
import { WIDGET_DEFINITIONS } from '@/modules/analytics/widgetRegistry'

const route = useRoute()
const router = useRouter()

const boardId = route.params.boardId as string
</script>

<template>
  <AppShellHeader>
    <Header heading="Add widget" />
  </AppShellHeader>

  <ul class="gallery">
    <li v-for="definition in WIDGET_DEFINITIONS" :key="definition.type">
      <WidgetCard
        :definition="definition"
        :to="{ name: 'analytics-widget-add', params: { boardId, type: definition.type } }"
      />
    </li>
  </ul>

  <AppShellFooter>
    <Footer>
      <Button variant="secondary" @click="router.back()">Cancel</Button>
    </Footer>
  </AppShellFooter>
</template>

<style scoped>
.gallery {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
  margin: 0;
  padding: var(--spacing-xs) var(--padding-app) var(--spacing-lg);
  list-style: none;
}

.gallery li {
  display: grid;
}

@media (min-width: 768px) {
  .gallery {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: var(--spacing-md);
  }
}
</style>
