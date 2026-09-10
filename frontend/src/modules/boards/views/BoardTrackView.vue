<script setup lang="ts">
import { computed, onMounted, ref, type Ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { MoreVertical, Settings } from '@lucide/vue'
import AppShellHeader from '@/shared/ui/layout/AppShellHeader.vue'
import Tabs from '@/shared/ui/components/Tabs.vue'
import SignalCard from '@/shared/ui/components/SignalCard.vue'
import Header from '@/shared/ui/components/Header.vue'
import IconButton from '@/shared/ui/components/IconButton.vue'
import LogEntryDrawer from '@/modules/events/components/LogEntryDrawer.vue'
import EventDraftBar from '@/modules/events/components/EventDraftBar.vue'
import { getBoards } from '@/modules/boards/api'
import { getSignals } from '@/modules/signals/api'
import { useToast } from '@/shared/lib/useToast'
import { createEvent, getEvent, updateEvent } from '@/modules/events/api'
import { resolveIcon } from '@/shared/lib/iconRegistry'
import type { Board } from '@/modules/boards/types'
import type { Signal } from '@/modules/signals/types'
import type { DraftEntry } from '@/modules/events/types'
import { now, getLocalTimeZone, ZonedDateTime, toCalendarDate, toTime, type DateValue, fromDate } from '@internationalized/date'
import type { TimeValue } from 'reka-ui'

const route = useRoute()
const router = useRouter()
const toaster = useToast()

const loading = ref(true)
const draftBarVisible = ref(false)

const editingEventId = computed(() => route.params.eventId as string | undefined)
const isEditing = computed(() => !!editingEventId.value)
const entryDrawerOpen = ref(false)

const boards = ref<Board[]>([])
const signals = ref<Signal[]>([])
const selectedSignal = ref<Signal | null>(null)
const editingSignalEntry = ref<DraftEntry | null>(null)
const editingSignalEntryId = ref<string | null>(null)
const draftSignalEntries = ref<DraftEntry[]>([])
const draftDateTime = ref<ZonedDateTime>(now(getLocalTimeZone())) as Ref<ZonedDateTime>

const draftDate = computed<DateValue>({
  get: () => toCalendarDate(draftDateTime.value),
  set: (newDate) => {
    draftDateTime.value = draftDateTime.value.set({
      year: newDate.year,
      month: newDate.month,
      day: newDate.day,
    })
  }
})

const draftTime = computed<TimeValue>({
  get: () => toTime(draftDateTime.value),
  set: (newTime) => {
    draftDateTime.value = draftDateTime.value.set({
      hour: newTime.hour,
      minute: newTime.minute,
      second: newTime.second,
    })
  },
})

const ALL_TAB = 'all'
const activeTab = ref<string>(ALL_TAB)
const tabs = computed(() => [
  { value: ALL_TAB, label: 'All' },
  ...boards.value.map((b) => ({ value: b.id, label: b.name })),
])

const activeSignals = computed<Signal[]>(() => {
  if (activeTab.value === ALL_TAB) {
    return signals.value
  }
  const board = boards.value.find(board => board.id === activeTab.value)
  return board ? board.board_signals.map((bs) => bs.signal) : []
})

async function load() {
  loading.value = true

  try {
    const [{ data: boardsData }, { data: signalsData }] = await Promise.all([
      getBoards(),
      getSignals(),
    ])
    boards.value = boardsData
    signals.value = signalsData
  } finally {
    loading.value = false
  }
}

function setDraftTimestamp() {
  if (draftSignalEntries.value.length === 0) {
    draftDateTime.value = now(getLocalTimeZone())
  }
}

function onAddSignalEntry(signal: Signal) {
  setDraftTimestamp()
  draftBarVisible.value = true
  if (signal.type === 'tally') {
    draftSignalEntries.value.push({
      id: Date.now().toString(),
      signal,
      value: 1,
    })
    return
  }

  selectedSignal.value = signal
  editingSignalEntry.value = null
  editingSignalEntryId.value = null
  entryDrawerOpen.value = true
}

function onEditSignalEntry(entryId: string) {
  const entry = draftSignalEntries.value.find((e) => e.id === entryId)
  if (!entry) return
  selectedSignal.value = entry.signal
  editingSignalEntry.value = entry
  editingSignalEntryId.value = entry.id
  entryDrawerOpen.value = true
}

function onRemoveSignalEntry(entryId: string) {
  draftSignalEntries.value = draftSignalEntries.value.filter((e) => e.id !== entryId)
}

function onSignalEntrySaved(entry: Omit<DraftEntry, 'id'> & { id?: string }) {
  draftBarVisible.value = true
  if (editingSignalEntryId.value) {
    // existing entry: keep its local id and server-side entryId, replace its contents
    const index = draftSignalEntries.value.findIndex((e) => e.id === editingSignalEntryId.value)
    if (index !== -1) {
      const existing = draftSignalEntries.value[index]
      draftSignalEntries.value[index] = { ...entry, id: existing.id, entryId: existing.entryId }
    }
  } else {
    // new entry: no server-side entryId yet
    draftSignalEntries.value.push({ ...entry, id: Math.random().toString(36).slice(2) })
  }
}

// TODO: implement or hide for later
function onSignalOptions(signal: Signal) {
  console.log('signal options', signal)
}

function onNoteClick() {
  console.log('note click')
}
function onLocationClick() {
  console.log('location click')
}
function onPeopleClick() {
  console.log('people click')
}

function onCancelDraft() {
  draftBarVisible.value = false
  draftSignalEntries.value = []
  if (editingEventId.value) {
    router.back()
  }
}

function goToManage() {
  if (activeTab.value === ALL_TAB) {
    router.push({ name: 'manage-boards' })
  } else {
    router.push({ name: 'board-edit', params: { id: activeTab.value } })
  }
}

async function onSaveDraft() {
  const payload = {
    occurred_at: draftDateTime.value.toDate().toISOString(),
    entries: draftSignalEntries.value.map((e) => ({
      id: e.entryId,
      signal_id: e.signal.id,
      value: e.value,
      duration: e.duration,
    })),
  }

  try {
    if (editingEventId.value) {
      await updateEvent(editingEventId.value, payload)
      toaster.toast({ description: 'Entry updated.', variant: 'success' })
      router.back()
    } else {
      await createEvent(payload)
      draftBarVisible.value = false
      toaster.toast({ description: 'Entry saved.', variant: 'success' })
    }
    draftSignalEntries.value = []
  } catch (err) {
    toaster.toast({ description: 'Could not save entry.', variant: 'danger' })
    console.error(err)
  }
}

async function loadEventForEdit(id: string) {
  const { data } = await getEvent(id)

  draftBarVisible.value = true
  draftDateTime.value = fromDate(new Date(data.occurred_at), getLocalTimeZone())

  draftSignalEntries.value = data.entries.map((e) => ({
    id: Math.random().toString(36).slice(2),
    entryId: e.id,
    signal: e.signal,
    value: e.value != null ? Number(e.value) : undefined,
    duration: e.duration,
  }))
}

onMounted(async () => {
  await load()
  if (editingEventId.value) {
    await loadEventForEdit(editingEventId.value)
  }
})
</script>

<template>

  <AppShellHeader>
    <Header :heading="isEditing ? 'Edit entry' : 'Log events'">
      <template #actions>
        <IconButton variant="tertiary" @click="goToManage">
          <Settings />
        </IconButton>
      </template>
      <template #content>
        <Tabs v-if="tabs.length > 1" v-model="activeTab" :items="tabs" class="track-tabs" />
      </template>
    </Header>
  </AppShellHeader>

  <div v-if="!loading" class="signal-grid" :class="{ 'has-draft-bar': draftBarVisible }">
    <SignalCard v-for="signal in activeSignals" :key="signal.id" :signal="signal" @select="onAddSignalEntry(signal)">
      <template v-if="resolveIcon(signal.icon)" #icon>
        <component :is="resolveIcon(signal.icon)" :style="{ color: signal.color }" />
      </template>

      <template #actions>
        <IconButton @click.stop="onSignalOptions(signal)" :aria-label="`Options for ${signal.name}`" variant="tertiary"
          size="sm">
          <MoreVertical />
        </IconButton>
      </template>
    </SignalCard>

    <p v-if="activeSignals.length === 0" class="empty-state">
      No signals in this board yet.
    </p>
  </div>

  <LogEntryDrawer v-if="selectedSignal" v-model:open="entryDrawerOpen" :numpad="true" :signal="selectedSignal"
    :editing="!!editingSignalEntry" :initial-value="editingSignalEntry?.value"
    :initial-duration="editingSignalEntry?.duration" @save="onSignalEntrySaved" />

  <EventDraftBar v-if="draftBarVisible" :entries="draftSignalEntries" v-model:date="draftDate" v-model:time="draftTime"
    @edit-entry="onEditSignalEntry" @remove-entry="onRemoveSignalEntry" @note-click="onNoteClick"
    @location-click="onLocationClick" @people-click="onPeopleClick" @cancel="onCancelDraft" @save="onSaveDraft" />
</template>

<style scoped>
.track-tabs {
  width: 100vw;
  margin-left: -16px;
}

.settings-btn {
  all: unset;
  display: inline-flex;
  cursor: pointer;
  color: var(--input-color-label);
}

.signal-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 0 var(--padding-app);
}

.signal-grid.has-draft-bar {
  padding-bottom: 220px;
}

.empty-state {
  grid-column: 1 / -1;
  padding: 24px;
  text-align: center;
  color: var(--input-color-label);
}
</style>
