<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import AppShellHeader from '@/shared/ui/layout/AppShellHeader.vue'
import JournalEventCard from '@/modules/journal/components/JournalEventCard.vue'
import Header from '@/shared/ui/components/Header.vue'
import { getEvents } from '@/modules/events/api'
import { groupEventsByDay } from '@/modules/journal/format'
import type { Event } from '@/modules/events/types'

const events = ref<Event[]>([])
const loading = ref(true)
const dayGroups = computed(() => groupEventsByDay(events.value))

async function load() {
  loading.value = true
  try {
    const { data } = await getEvents()
    events.value = data
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <AppShellHeader>
    <Header heading="Journal">
    </Header>
  </AppShellHeader>

  <div v-if="!loading" class="journal-groups">

    <section v-for="group in dayGroups" :key="group.key" class="journal-day-group">
      <div class="journal-day-header">
        <span class="journal-day-label">{{ group.label }}</span>
      </div>

      <div class="journal-day-events">
        <JournalEventCard v-for="event in group.events" :key="event.id" :event="event" />
      </div>
    </section>

    <p v-if="dayGroups.length === 0" class="empty-state">
      No entries yet.
    </p>

  </div>
</template>

<style scoped>
.journal-groups {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 0 var(--padding-app);
  margin-bottom: 200px;
}

.journal-day-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.journal-day-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
}

.journal-day-label {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
  color: var(--input-color-label);
  white-space: nowrap;
  padding-left: 12px;
}

.journal-day-events {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.empty-state {
  padding: 24px;
  text-align: center;
  color: var(--input-color-label);
}
</style>
