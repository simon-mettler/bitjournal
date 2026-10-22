<script setup lang="ts">
import { computed, onMounted, ref, type Ref } from 'vue'
import { getLocalTimeZone, today, type DateValue } from '@internationalized/date'
import { CalendarDays, ChevronRight, ListFilter, Plus } from '@lucide/vue'
import AppShellHeader from '@/shared/ui/layout/AppShellHeader.vue'
import JournalEventCard from '@/modules/journal/components/JournalEventCard.vue'
import Header from '@/shared/ui/components/Header.vue'
import AlertDialog from '@/shared/ui/components/AlertDialog.vue'
import Button from '@/shared/ui/components/Button.vue'
import Collapsible from '@/shared/ui/components/Collapsible.vue'
import ToggleGroup from '@/shared/ui/components/ToggleGroup.vue'
import DatePicker from '@/shared/ui/components/DatePicker.vue'
import SignalPickerDialog from '@/modules/signals/components/SignalPickerDialog.vue'
import SignalChip from '@/shared/ui/components/SignalChip.vue'
import { getEvents, cursorOf, deleteEvent } from '@/modules/events/api'
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
const nextCursor = ref<string | null>(null)
const dayGroups = computed(() => groupEventsByDay(events.value))

const draftBefore = ref<DateValue | undefined>(undefined) as Ref<DateValue | undefined>
const draftSignals = ref<Signal[]>([])
const draftLogic = ref<SignalLogic>('or')

const appliedBefore = ref<DateValue | undefined>(undefined) as Ref<DateValue | undefined>
const appliedSignals = ref<Signal[]>([])
const appliedLogic = ref<SignalLogic>('or')

const draftSignalIds = computed(() => draftSignals.value.map((s) => s.id))

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
  draftSignals.value = draftSignals.value.filter((s) => s.id !== id)
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
    signalIds: appliedSignals.value.length ? appliedSignals.value.map((s) => s.id) : undefined,
    signalLogic: appliedSignals.value.length ? appliedLogic.value : undefined,
  }
}

function applyFilters() {
  appliedBefore.value = draftBefore.value
  appliedSignals.value = [...draftSignals.value]
  appliedLogic.value = draftLogic.value
  void load()
}

function clearAll() {
  draftBefore.value = undefined
  draftSignals.value = []
  draftLogic.value = 'or'
  appliedBefore.value = undefined
  appliedSignals.value = []
  appliedLogic.value = 'or'
  void load()
}

const confirmDeleteOpen = ref(false)
const eventPendingDelete = ref<Event | null>(null)
const deleting = ref(false)

let loadId = 0

async function load() {
  const id = ++loadId
  loading.value = true
  try {
    const { data } = await getEvents(currentFilterParams())
    if (id !== loadId) return
    events.value = data.results
    nextCursor.value = cursorOf(data.next)
  } finally {
    if (id === loadId) loading.value = false
  }
}

async function loadMore() {
  const cursor = nextCursor.value
  if (!cursor || loadingMore.value) return
  const id = loadId
  loadingMore.value = true
  try {
    const { data } = await getEvents({ ...currentFilterParams(), cursor })
    if (id !== loadId) return
    events.value = [...events.value, ...data.results]
    nextCursor.value = cursorOf(data.next)
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
    events.value = events.value.filter((e) => e.id !== target.id)
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
    <template #icon>
      <ListFilter :size="18" class="filters-icon" />
    </template>
    <template #actions>
      <button type="button" class="filters-clear" @click="clearAll">Clear all</button>
    </template>

    <DatePicker v-model="draftBefore">
      <template #trigger="{ open }">
        <button type="button" class="filter-button" @click="open">
          <span class="filter-button-icon">
            <CalendarDays :size="18" />
          </span>
          <span class="filter-button-label">Up to:</span>
          <span class="filter-button-value">{{ dateBoundaryLabel }}</span>
          <ChevronRight :size="16" class="filter-button-chevron" />
        </button>
      </template>
    </DatePicker>

    <div class="trackers-header">
      <div class="trackers-label">
        <span>Signals</span>
        <span v-if="draftSignals.length" class="trackers-count">{{ draftSignals.length }}</span>
      </div>
      <ToggleGroup v-model="draftLogic" :options="logicOptions" />
    </div>

    <div class="tracker-chips">
      <SignalChip
        v-for="signal in draftSignals"
        :key="signal.id"
        :signal="signal"
        :value="signal.name"
        removable
        @remove="removeSignal(signal.id)"
      />

      <SignalPickerDialog :exclude-ids="draftSignalIds" @add="addSignals">
        <template #trigger>
          <button type="button" class="add-tracker-button">
            <Plus :size="14" />
            Add signal
          </button>
        </template>
      </SignalPickerDialog>
    </div>

    <Button
      variant="primary"
      class="show-results-button"
      :disabled="!isDirty"
      @click="applyFilters"
    >
      Show Results
    </Button>
  </Collapsible>

  <div v-if="!loading" class="journal-groups">
    <section v-for="group in dayGroups" :key="group.key" class="journal-day-group">
      <div class="journal-day-header">
        <span class="journal-day-label">{{ group.label }}</span>
      </div>

      <div class="journal-day-events">
        <JournalEventCard
          v-for="event in group.events"
          :key="event.id"
          :event="event"
          @request-delete="requestDelete"
        />
      </div>
    </section>

    <p v-if="dayGroups.length === 0" class="empty-state">
      {{ hasActiveFilters ? 'No entries match these filters.' : 'No entries yet.' }}
    </p>

    <div v-if="nextCursor" class="journal-load-more">
      <Button variant="secondary" :disabled="loadingMore" @click="loadMore">
        {{ loadingMore ? 'Loading…' : 'Load more' }}
      </Button>
    </div>
  </div>

  <AlertDialog
    v-model:open="confirmDeleteOpen"
    title="Delete entry"
    confirm-text="Delete"
    description="Are you sure you want to delete this entry? This can't be undone."
    @confirm="confirmDelete"
  >
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
  margin: 12px var(--padding-app) 16px;
}

.filters-clear {
  all: unset;
  color: var(--color-primary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-normal);
  cursor: pointer;
}

.filter-button {
  all: unset;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  width: 100%;
  height: var(--input-height);
  margin-bottom: var(--spacing-lg);
  padding: 0 var(--spacing-md);
  background-color: var(--color-surface-muted);
  border-radius: var(--radius-md);
  color: var(--input-color-text);
  font-size: var(--font-size-base);
  cursor: pointer;
}

.filter-button:focus-visible {
  box-shadow: var(--input-shadow-focus);
  border: var(--input-border-focus);
}

.filter-button-icon {
  display: flex;
  align-items: center;
  color: var(--input-color-label);
  flex-shrink: 0;
}

.filter-button-label {
  color: var(--input-color-label);
}

.filter-button-value {
  flex: 1;
  min-width: 0;
  font-weight: var(--font-weight-bold);
}

.filter-button-chevron {
  flex-shrink: 0;
  color: var(--input-color-label);
}

.trackers-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-md);
}

.trackers-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
  letter-spacing: 0.04em;
  color: var(--input-color-text);
}

.trackers-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: var(--radius-xl);
  background: var(--color-primary-soft);
  color: var(--color-primary);
  font-size: var(--font-size-sm);
}

.tracker-chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
}

.add-tracker-button {
  all: unset;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px var(--spacing-md);
  border-radius: var(--radius-xl);
  border: 1px dashed var(--color-primary-border);
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
