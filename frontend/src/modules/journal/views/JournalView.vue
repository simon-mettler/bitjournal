<script setup lang="ts">
import { computed, onMounted, ref, type Ref } from 'vue'
import { getLocalTimeZone, today, type DateValue } from '@internationalized/date'
import { CalendarDays, ChevronRight, Plus } from '@lucide/vue'
import AppShellHeader from '@/shared/ui/layout/AppShellHeader.vue'
import JournalEventCard from '@/modules/journal/components/JournalEventCard.vue'
import Header from '@/shared/ui/components/Header.vue'
import AlertDialog from '@/shared/ui/components/AlertDialog.vue'
import Button from '@/shared/ui/components/Button.vue'
import Collapsible from '@/shared/ui/components/Collapsible.vue'
import Toggle from '@/shared/ui/components/Toggle.vue'
import DatePicker from '@/shared/ui/components/DatePicker.vue'
import SignalPickerDialog from '@/modules/boards/components/SignalPickerDialog.vue'
import SignalChip from '@/shared/ui/components/SignalChip.vue'
import { getEvents, getEventsPage, deleteEvent } from '@/modules/events/api'
import type { SignalLogic } from '@/modules/events/api'
import { groupEventsByDay } from '@/modules/journal/format'
import { useToast } from '@/shared/lib/useToast'
import type { Event } from '@/modules/events/types'
import type { Signal } from '@/modules/signals/types'

const logicOptions: { value: SignalLogic; label: string }[] = [
  { value: 'or', label: 'Any (OR)' },
  { value: 'and', label: 'All (AND)' },
]

const toaster = useToast()

const events = ref<Event[]>([])
const loading = ref(true)
const loadingMore = ref(false)
const nextPage = ref<string | null>(null)
const dayGroups = computed(() => groupEventsByDay(events.value))

const draftBefore = ref<DateValue | undefined>(undefined) as Ref<DateValue | undefined>
const draftSignals = ref<Signal[]>([])
const draftLogic = ref<SignalLogic>('or')

const appliedBefore = ref<DateValue | undefined>(undefined) as Ref<DateValue | undefined>
const appliedSignals = ref<Signal[]>([])
const appliedLogic = ref<SignalLogic>('or')

const draftSignalIds = computed(() => draftSignals.value.map(s => s.id))

const dateBoundaryLabel = computed(() => {
  const date = draftBefore.value
  if (!date) return 'Any date'
  const jsDate = date.toDate(getLocalTimeZone())
  const isToday = date.compare(today(getLocalTimeZone())) === 0
  const formatted = jsDate.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
  return isToday ? `Today, ${formatted}` : formatted
})

function addSignals(signals: Signal[]) {
  draftSignals.value = [...draftSignals.value, ...signals]
}

function removeSignal(id: string) {
  draftSignals.value = draftSignals.value.filter(s => s.id !== id)
}

// Include the whole selected day, since occurred_at is a datetime and the filter is <=
function toBeforeIso(date: DateValue | undefined) {
  if (!date) return undefined
  const d = date.toDate(getLocalTimeZone())
  d.setHours(23, 59, 59, 999)
  return d.toISOString()
}

const isDirty = computed(() => {
  const dateChanged = String(draftBefore.value ?? '') !== String(appliedBefore.value ?? '')
  const logicChanged = draftLogic.value !== appliedLogic.value
  const signalsChanged =
    draftSignals.value.length !== appliedSignals.value.length ||
    draftSignals.value.some((s, i) => s.id !== appliedSignals.value[i]?.id)
  return dateChanged || logicChanged || signalsChanged
})

const hasActiveFilters = computed(
  () => Boolean(appliedBefore.value) || appliedSignals.value.length > 0,
)

function currentFilterParams() {
  return {
    before: toBeforeIso(appliedBefore.value),
    signalIds: appliedSignals.value.length ? appliedSignals.value.map(s => s.id) : undefined,
    signalLogic: appliedSignals.value.length ? appliedLogic.value : undefined,
  }
}

function applyFilters() {
  appliedBefore.value = draftBefore.value
  appliedSignals.value = [...draftSignals.value]
  appliedLogic.value = draftLogic.value
  load()
}

function clearAll() {
  draftBefore.value = undefined
  draftSignals.value = []
  draftLogic.value = 'or'
  appliedBefore.value = undefined
  appliedSignals.value = []
  appliedLogic.value = 'or'
  load()
}

const confirmDeleteOpen = ref(false)
const eventPendingDelete = ref<Event | null>(null)
const deleting = ref(false)

async function load() {
  loading.value = true
  try {
    const { data } = await getEvents(currentFilterParams())
    events.value = data.results
    nextPage.value = data.next
  } finally {
    loading.value = false
  }
}

async function loadMore() {
  if (!nextPage.value || loadingMore.value) return
  loadingMore.value = true
  try {
    const { data } = await getEventsPage(nextPage.value)
    events.value = [...events.value, ...data.results]
    nextPage.value = data.next
  } finally {
    loadingMore.value = false
  }
}

function requestDelete(event: Event) {
  eventPendingDelete.value = event
  confirmDeleteOpen.value = true
}

async function confirmDelete() {
  if (!eventPendingDelete.value) return
  const target = eventPendingDelete.value
  deleting.value = true
  try {
    await deleteEvent(target.id)
    events.value = events.value.filter(e => e.id !== target.id)
    toaster.toast({ description: 'Event deleted.', variant: 'success' })
  } catch (err) {
    console.error(err)
    toaster.toast({ description: 'Could not delete event.', variant: 'danger' })
  } finally {
    deleting.value = false
    confirmDeleteOpen.value = false
    eventPendingDelete.value = null
  }
}

onMounted(load)
</script>

<template>
  <AppShellHeader>
    <Header heading="Journal" />
  </AppShellHeader>

  <Collapsible title="Filters" class="filters-panel">
    <template #actions>
      <button type="button" class="filters-clear" @click="clearAll">Clear all</button>
    </template>

    <div class="filter-row">
      <div class="filter-row-icon">
        <CalendarDays :size="18" />
      </div>
      <div class="filter-row-text">
        <span class="filter-row-title">Date Boundary</span>
        <span class="filter-row-subtitle">Filter events up to date</span>
      </div>
      <DatePicker v-model="draftBefore">
        <template #trigger="{ open }">
          <button type="button" class="filter-value-button" @click="open">
            <span>{{ dateBoundaryLabel }}</span>
            <ChevronRight :size="16" />
          </button>
        </template>
      </DatePicker>
    </div>

    <div class="filters-divider" />

    <div class="trackers-header">
      <div class="trackers-label">
        <span>TRACKERS</span>
        <span v-if="draftSignals.length" class="trackers-count">{{ draftSignals.length }}</span>
      </div>
      <div class="logic-toggle">
        <Toggle v-for="option in logicOptions" :key="option.value" :model-value="draftLogic === option.value"
          @update:model-value="pressed => pressed && (draftLogic = option.value)">
          {{ option.label }}
        </Toggle>
      </div>
    </div>

    <div class="tracker-chips">
      <SignalChip v-for="signal in draftSignals" :key="signal.id" :signal="signal" :value="signal.name" removable
        @remove="removeSignal(signal.id)" />

      <SignalPickerDialog :exclude-ids="draftSignalIds" @add="addSignals">
        <template #trigger>
          <button type="button" class="add-tracker-button">
            <Plus :size="14" />
            Add tracker
          </button>
        </template>
      </SignalPickerDialog>
    </div>

    <Button variant="primary" class="show-results-button" :disabled="!isDirty" @click="applyFilters">
      Show Results
    </Button>
  </Collapsible>

  <div v-if="!loading" class="journal-groups">
    <section v-for="group in dayGroups" :key="group.key" class="journal-day-group">
      <div class="journal-day-header">
        <span class="journal-day-label">{{ group.label }}</span>
      </div>

      <div class="journal-day-events">
        <JournalEventCard v-for="event in group.events" :key="event.id" :event="event"
          @request-delete="requestDelete" />
      </div>
    </section>

    <p v-if="dayGroups.length === 0" class="empty-state">
      {{ hasActiveFilters ? 'No entries match these filters.' : 'No entries yet.' }}
    </p>

    <div v-if="nextPage" class="journal-load-more">
      <Button variant="secondary" :disabled="loadingMore" @click="loadMore">
        {{ loadingMore ? 'Loading…' : 'Load more' }}
      </Button>
    </div>
  </div>

  <AlertDialog title="Delete entry" confirm-text="Delete"
    description="Are you sure you want to delete this entry? This can't be undone." v-model:open="confirmDeleteOpen"
    @confirm="confirmDelete">
    <template #cancel>
      <Button variant="secondary">Cancel</Button>
    </template>
    <template #action>
      <Button variant="primary" :disabled="deleting">Delete</Button>
    </template>
  </AlertDialog>
</template>

<style scoped>
.filters-panel {
  margin: 0 var(--padding-app) 16px;
}

.filters-clear {
  all: unset;
  color: var(--color-primary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  text-decoration: underline;
  cursor: pointer;
}

.filters-divider {
  height: 1px;
  background: var(--input-color-border);
  margin: var(--spacing-md) 0;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.filter-row-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  background: var(--color-surface-muted);
  color: var(--input-color-label);
  flex-shrink: 0;
}

.filter-row-text {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.filter-row-title {
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-sm);
}

.filter-row-subtitle {
  font-size: var(--font-size-sm);
  color: var(--input-color-label);
}

.filter-value-button {
  all: unset;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-xl);
  background: var(--color-surface-muted);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  cursor: pointer;
  white-space: nowrap;
}

.trackers-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-sm);
}

.trackers-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  letter-spacing: 0.04em;
  color: var(--input-color-label);
}

.trackers-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: var(--radius-xl);
  background: oklab(from var(--color-primary) l a b / 0.15);
  color: var(--color-primary);
  font-size: var(--font-size-sm);
}

.logic-toggle {
  display: flex;
  gap: 2px;
  padding: 2px;
  border-radius: var(--radius-xl);
  background: var(--color-surface-muted);
}

.tracker-chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.add-tracker-button {
  all: unset;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px var(--spacing-md);
  border-radius: var(--radius-xl);
  border: 1px dashed var(--color-primary);
  color: var(--color-primary);
  font-size: var(--font-size-sm);
  cursor: pointer;
}

.show-results-button {
  width: 100%;
}

.journal-load-more {
  display: flex;
  justify-content: center;
  padding: var(--spacing-md) 0;
}

.journal-groups {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  padding: 0 var(--padding-app);
  margin-bottom: 200px;
}

.journal-day-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.journal-day-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-md);
}

.journal-day-label {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
  color: var(--input-color-label);
  white-space: nowrap;
  padding-left: var(--spacing-sm);
}

.journal-day-events {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.empty-state {
  padding: var(--spacing-lg);
  text-align: center;
  color: var(--input-color-label);
}
</style>
