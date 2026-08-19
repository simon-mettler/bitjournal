<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { MoreVertical, Settings } from '@lucide/vue'
import Tabs from '@/shared/ui/components/Tabs.vue'
import SignalCard from '@/shared/ui/components/SignalCard.vue'
import LogEntryDrawer from '@/modules/events/components/LogEntryDrawer.vue'
import EventDraftBar from '@/modules/events/components/EventDraftBar.vue'
import { getBoards } from '../api'
import { getSignals } from '@/modules/signals/api'
import { createEvent } from '@/modules/events/api'
import type { Board } from '@/modules/boards/types'
import type { Signal } from '@/modules/signals/types'
import type { DraftEntry } from '@/modules/events/types'
import { resolveIcon } from '@/shared/lib/iconRegistry'
import { useToast } from '@/shared/lib/useToast'

const toast = useToast()

const boards = ref<Board[]>([])
const signals = ref<Signal[]>([])

const loading = ref(true)

const selectedSignal = ref<Signal | null>(null)
const entryDrawerOpen = ref(false)
const editingSignalEntry = ref<DraftEntry | null>(null)
const editingSignalEntryId = ref<string | null>(null)

const draftSignalEntries = ref<DraftEntry[]>([])
const now = new Date()
const draftDate = ref(now.toISOString().slice(0, 10))
const draftHours = ref(now.getHours())
const draftMinutes = ref(now.getMinutes())

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

function onAddSignalEntry(signal: Signal) {
  if (signal.type === 'tally') {
    draftSignalEntries.value.push({
      id: crypto.randomUUID(),
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

// tapping a chip in the draft bar: reopen the sheet pre-filled, by entry id
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
    draftSignalEntries.value.push({ ...entry, id: crypto.randomUUID() })
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

async function onSaveDraft() {
  const pad = (n: number) => String(n).padStart(2, '0')
  try {
    await createEvent({
      date: draftDate.value,
      time: `${pad(draftHours.value)}:${pad(draftMinutes.value)}:00`,
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
  <div class="track-header">
    <h1>Track</h1>
    <button type="button" class="settings-btn" aria-label="Settings">
      <Settings :size="22" />
    </button>
  </div>

  <Tabs v-if="tabs.length > 1" v-model="activeTab" :items="tabs" class="track-tabs" />

  <div v-if="!loading" class="signal-grid" :class="{ 'has-draft-bar': draftSignalEntries.length > 0 }">
    <SignalCard v-for="signal in activeSignals" :key="signal.id" :signal="signal" @select="onAddSignalEntry(signal)">
      <template v-if="resolveIcon(signal.icon)" #icon>
        <component :is="resolveIcon(signal.icon)" :style="{ color: signal.color }" />
      </template>

      <template #actions>
        <button type="button" class="icon-btn" :aria-label="`Options for ${signal.name}`"
          @click.stop="onSignalOptions(signal)">
          <MoreVertical :size="18" />
        </button>
      </template>
    </SignalCard>

    <p v-if="activeSignals.length === 0" class="empty-state">
      No signals in this board yet.
    </p>
  </div>

  <LogEntryDrawer v-if="selectedSignal" v-model:open="entryDrawerOpen" :signal="selectedSignal"
    :editing="!!editingSignalEntry" :initial-value="editingSignalEntry?.value"
    :initial-duration="editingSignalEntry?.duration" @save="onSignalEntrySaved" />

  <EventDraftBar v-if="draftSignalEntries.length > 0" :entries="draftSignalEntries" v-model:date="draftDate"
    v-model:hours="draftHours" v-model:minutes="draftMinutes" @edit-entry="onEditSignalEntry"
    @remove-entry="onRemoveSignalEntry" @note-click="onNoteClick" @location-click="onLocationClick"
    @people-click="onPeopleClick" @cancel="onCancelDraft" @save="onSaveDraft" />
</template>

<style scoped>
.track-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.track-header h1 {
  color: var(--color-primary);
  margin: 0;
}

.settings-btn {
  all: unset;
  display: inline-flex;
  cursor: pointer;
  color: var(--input-color-label);
}

.track-tabs {
  margin-bottom: 16px;
}

.signal-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.signal-grid.has-draft-bar {
  /* TODO: check draft bar height */
  padding-bottom: 220px;
}

.icon-btn {
  all: unset;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: var(--input-radius);
  cursor: pointer;
  color: var(--input-color-label);
}

.icon-btn:hover {
  background-color: var(--color-surface-muted);
}

.empty-state {
  grid-column: 1 / -1;
  padding: 24px;
  text-align: center;
  color: var(--input-color-label);
}
</style>
