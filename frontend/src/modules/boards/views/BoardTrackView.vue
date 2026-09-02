<script setup lang="ts">
import { computed, onMounted, ref, type Ref } from 'vue'
import { MoreVertical, Settings } from '@lucide/vue'
import AppShellHeader from '@/shared/ui/layout/AppShellHeader.vue'
import Tabs from '@/shared/ui/components/Tabs.vue'
import SignalCard from '@/shared/ui/components/SignalCard.vue'
import Header from '@/shared/ui/components/Header.vue'
import IconButton from '@/shared/ui/components/IconButton.vue'
import LogEntryDrawer from '@/modules/events/components/LogEntryDrawer.vue'
import EventDraftBar from '@/modules/events/components/EventDraftBar.vue'
import { useRouter } from 'vue-router'
import { getBoards } from '@/modules/boards/api'
import { getSignals } from '@/modules/signals/api'
import { createEvent } from '@/modules/events/api'
import { useToast } from '@/shared/lib/useToast'
import { resolveIcon } from '@/shared/lib/iconRegistry'
import { now, getLocalTimeZone, toCalendarDate, toTime } from '@internationalized/date'
import type { Board } from '@/modules/boards/types'
import type { Signal } from '@/modules/signals/types'
import type { DraftEntry } from '@/modules/events/types'
import type { DateValue, ZonedDateTime } from '@internationalized/date'
import type { TimeValue } from 'reka-ui'

const router = useRouter()

const loading = ref(true)
const toast = useToast()

const boards = ref<Board[]>([])
const signals = ref<Signal[]>([])
const selectedSignal = ref<Signal | null>(null)

const entryDrawerOpen = ref(false)
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

// tapping a chip in the draft bar: reopen the drawer pre-filled, by entry id
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
  if (editingSignalEntryId.value) {
    // existing entry: keep its id, replace its contents
    const index = draftSignalEntries.value.findIndex((e) => e.id === editingSignalEntryId.value)
    if (index !== -1) {
      draftSignalEntries.value[index] = { ...entry, id: editingSignalEntryId.value }
    }
  } else {
    // new entry, even if it's the same signal as an existing one
    draftSignalEntries.value.push({ ...entry, id: Date.now().toString() })
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
  draftSignalEntries.value = []
}
function goToManage() {
  if (activeTab.value === ALL_TAB) {
    router.push({ name: 'manage-boards' })
  } else {
    router.push({ name: 'board-edit', params: { id: activeTab.value } })
  }
}
async function onSaveDraft() {
  try {
    await createEvent({
      occurred_at: draftDateTime.value.toDate().toISOString(),
      entries: draftSignalEntries.value.map((e) => ({
        signal_id: e.signal.id,
        value: e.value,
        duration: e.duration,
      })),
    })
    draftSignalEntries.value = []
    toast.toast({ description: 'Entry saved.', variant: 'success' })
  } catch (err) {
    toast.toast({ description: 'Could not save entry.', variant: 'error' })
    console.error(err)
  }
}
onMounted(load)
</script>

<template>

  <AppShellHeader>
    <Header heading="Log events">
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

  <div v-if="!loading" class="signal-grid" :class="{ 'has-draft-bar': draftSignalEntries.length > 0 }">
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

  <EventDraftBar v-if="draftSignalEntries.length > 0" :entries="draftSignalEntries" v-model:date="draftDate"
    v-model:time="draftTime" @edit-entry="onEditSignalEntry" @remove-entry="onRemoveSignalEntry"
    @note-click="onNoteClick" @location-click="onLocationClick" @people-click="onPeopleClick" @cancel="onCancelDraft"
    @save="onSaveDraft" />
</template>

<style scoped>
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
