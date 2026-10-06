<script setup lang="ts">
import { computed, onMounted, ref, type Ref } from 'vue'
import { useRouter, useRoute, onBeforeRouteLeave } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useLogEventsUiStore } from '@/modules/events/store/logEventsUiStore'
import { MoreVertical, ChartColumn, Pencil, GripVertical, X, Check } from '@lucide/vue'
import AppShellHeader from '@/shared/ui/layout/AppShellHeader.vue'
import AddTile from '@/shared/ui/components/AddTile.vue'
import BoardTabs from '@/shared/ui/components/BoardTabs.vue'
import SignalPickerDialog from '@/modules/signals/components/SignalPickerDialog.vue'
import SignalCard from '@/shared/ui/components/SignalCard.vue'
import Header from '@/shared/ui/components/Header.vue'
import IconButton from '@/shared/ui/components/IconButton.vue'
import DropdownMenu from '@/shared/ui/components/DropdownMenu.vue'
import type { DropdownMenuOption } from '@/shared/ui/components/DropdownMenu.vue'
import LogEntryDrawer from '@/modules/events/components/LogEntryDrawer.vue'
import EventDraftBar from '@/modules/events/components/EventDraftBar.vue'
import {
  createBoard,
  deleteBoard,
  getBoards,
  reorderBoards,
  updateBoard,
} from '@/modules/boards/api'
import { getSignals } from '@/modules/signals/api'
import { useToast } from '@/shared/lib/useToast'
import { enqueueBoardWrite } from '@/shared/lib/boardWriteQueue'
import { useSortableList } from '@/shared/lib/useSortableList'
import { createEvent, getEvent, updateEvent } from '@/modules/events/api'
import { resolveIcon } from '@/shared/lib/iconRegistry'
import type { Board } from '@/modules/boards/types'
import type { Signal } from '@/modules/signals/types'
import type { DraftEntry } from '@/modules/events/types'
import {
  now,
  getLocalTimeZone,
  ZonedDateTime,
  toCalendarDate,
  toTime,
  type DateValue,
  fromDate,
} from '@internationalized/date'
import type { TimeValue } from 'reka-ui'

const route = useRoute()
const router = useRouter()
const toaster = useToast()

const loading = ref(true)
const draftBarVisible = ref(false)
const logEventsUiStore = useLogEventsUiStore()

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
  },
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

const { activeTab, editing: boardEditing } = storeToRefs(logEventsUiStore)
const ALL_TAB = 'all'
const pinnedTabs = [{ value: ALL_TAB, label: 'All' }]
const activeTabId = computed({
  get: () => activeTab.value,
  set: (id: string | null) => (activeTab.value = id ?? ALL_TAB),
})
const activeBoard = computed(() => boards.value.find((b) => b.id === activeTab.value))
const canEditSignals = computed(() => boardEditing.value && !!activeBoard.value)

const activeSignals = computed<Signal[]>(() => {
  if (activeTab.value === ALL_TAB) {
    return signals.value
  }
  const board = boards.value.find((board) => board.id === activeTab.value)
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

    const stillExists =
      activeTab.value === ALL_TAB || boards.value.some((b) => b.id === activeTab.value)
    if (!stillExists) {
      activeTab.value = ALL_TAB
    }
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
  if (boardEditing.value) return
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

function signalOptions(signal: Signal): DropdownMenuOption[] {
  return [
    {
      label: 'View stats',
      value: 'view-stats',
      icon: ChartColumn,
      onSelect: () => router.push({ name: 'signal-stats', params: { id: signal.id } }),
    },
    {
      label: 'Edit signal',
      value: 'edit-signal',
      icon: Pencil,
      onSelect: () => router.push({ name: 'signal-edit', params: { id: signal.id } }),
    },
  ]
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

// EDIT MODE

const signalsOf = (board: Board) => board.board_signals.map((bs) => bs.signal)
const signalIds = (board: Board) => signalsOf(board).map((s) => s.id)

const boardApi = {
  create: async (name: string) => (await createBoard({ name })).data,
  rename: (board: Board, name: string) =>
    updateBoard(board.id, { name, signal_ids: signalIds(board) }),
  remove: (board: Board) => deleteBoard(board.id),
  reorder: (ids: string[]) => reorderBoards({ board_ids: ids }),
  reload: load,
}

const gridEl = ref<HTMLElement | null>(null)

function setBoardSignals(board: Board, list: Signal[]) {
  board.board_signals = list.map((signal, order) => ({ signal, order }))
}

const boardSignals = computed<Signal[]>({
  get: () => (activeBoard.value ? signalsOf(activeBoard.value) : []),
  set: (list) => activeBoard.value && setBoardSignals(activeBoard.value, list),
})

function persistSignals(board: Board) {
  enqueueBoardWrite(() =>
    updateBoard(board.id, { name: board.name, signal_ids: signalIds(board) }),
  ).catch(() => {
    toaster.toast({ description: 'Could not save board.', variant: 'danger' })
    void load()
  })
}

useSortableList(gridEl, boardSignals, {
  handle: '.signal-card-handle',
  enabled: canEditSignals,
  onSorted: () => activeBoard.value && persistSignals(activeBoard.value),
})

function onSignalsAdded(added: Signal[]) {
  const board = activeBoard.value
  if (!board) return
  setBoardSignals(board, [...boardSignals.value, ...added])
  persistSignals(board)
}

function onRemoveSignalFromBoard(signal: Signal) {
  const board = activeBoard.value
  if (!board) return
  const index = boardSignals.value.findIndex((s) => s.id === signal.id)
  setBoardSignals(
    board,
    boardSignals.value.filter((s) => s.id !== signal.id),
  )
  persistSignals(board)
  toaster.toast({
    description: `Removed "${signal.name}" from ${board.name}.`,
    actionLabel: 'Undo',
    onAction: () => {
      const restored = signalsOf(board)
      restored.splice(index, 0, signal)
      setBoardSignals(board, restored)
      persistSignals(board)
    },
  })
}

function onCreateSignalForBoard() {
  if (!activeBoard.value) return
  void router.push({ name: 'signal-add', query: { boardId: activeBoard.value.id } })
}

// Add newly created signal to board.
function addCreatedSignalFromRoute() {
  const { boardId, addSignalId } = route.query
  if (typeof boardId !== 'string' || typeof addSignalId !== 'string') return
  void router.replace({ name: route.name!, params: route.params })

  const board = boards.value.find((b) => b.id === boardId)
  const signal = signals.value.find((s) => s.id === addSignalId)
  if (!board || !signal) return

  activeTab.value = board.id
  boardEditing.value = true
  if (signalsOf(board).some((s) => s.id === signal.id)) return
  setBoardSignals(board, [...signalsOf(board), signal])
  persistSignals(board)
}

onBeforeRouteLeave(() => {
  boardEditing.value = false
})

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
    value: e.value ?? undefined,
    duration: e.duration ?? undefined,
  }))
}

onMounted(async () => {
  await load()
  addCreatedSignalFromRoute()
  if (editingEventId.value) {
    await loadEventForEdit(editingEventId.value)
  }
})
</script>

<template>
  <AppShellHeader>
    <Header :heading="isEditing ? 'Edit entry' : boardEditing ? 'Edit boards' : 'Log events'">
      <template #actions>
        <IconButton
          v-if="boardEditing"
          variant="primary"
          aria-label="Done editing"
          @click="boardEditing = false"
        >
          <Check />
        </IconButton>
        <IconButton
          v-else-if="!isEditing"
          variant="tertiary"
          aria-label="Edit boards"
          :disabled="draftBarVisible"
          @click="boardEditing = true"
        >
          <Pencil />
        </IconButton>
      </template>
      <template #content>
        <BoardTabs
          v-model:boards="boards"
          v-model:active="activeTabId"
          :editing="boardEditing"
          :show-tabs="boardEditing || boards.length > 0"
          :pinned="pinnedTabs"
          v-bind="boardApi"
        />
      </template>
    </Header>
  </AppShellHeader>

  <p v-if="boardEditing && !activeBoard" class="edit-hint">
    Select a board to rearrange or add signals.
  </p>

  <div ref="gridEl" class="signal-grid" :class="{ 'has-draft-bar': draftBarVisible }">
    <template v-if="!loading">
      <SignalCard
        v-for="signal in activeSignals"
        :key="signal.id"
        :signal="signal"
        :class="{ 'is-editing': boardEditing }"
        @select="onAddSignalEntry(signal)"
      >
        <template #icon>
          <component :is="resolveIcon(signal.icon)" :style="{ color: signal.color }" />
        </template>

        <template v-if="canEditSignals" #handle>
          <span aria-hidden="true">
            <GripVertical :size="20" />
          </span>
        </template>

        <template v-if="!boardEditing || canEditSignals" #actions>
          <IconButton
            v-if="canEditSignals"
            variant="tertiary"
            size="sm"
            :aria-label="`Remove ${signal.name} from board`"
            @click.stop="onRemoveSignalFromBoard(signal)"
          >
            <X />
          </IconButton>
          <DropdownMenu v-else :options="signalOptions(signal)">
            <template #trigger>
              <IconButton
                :aria-label="`Options for ${signal.name}`"
                variant="tertiary"
                size="sm"
                @click.stop
              >
                <MoreVertical />
              </IconButton>
            </template>
          </DropdownMenu>
        </template>
      </SignalCard>

      <SignalPickerDialog
        v-if="canEditSignals"
        :exclude-ids="boardSignals.map((s) => s.id)"
        allow-create
        @add="onSignalsAdded"
        @create="onCreateSignalForBoard"
      >
        <template #trigger>
          <AddTile>Add signal</AddTile>
        </template>
      </SignalPickerDialog>

      <p v-if="activeSignals.length === 0 && !canEditSignals" class="empty-state">
        {{
          activeBoard ? 'No signals in this board yet. Tap Edit to add some.' : 'No signals yet.'
        }}
      </p>
    </template>
  </div>

  <LogEntryDrawer
    v-if="selectedSignal"
    v-model:open="entryDrawerOpen"
    :numpad="true"
    :signal="selectedSignal"
    :editing="!!editingSignalEntry"
    :initial-value="editingSignalEntry?.value"
    :initial-duration="editingSignalEntry?.duration"
    @save="onSignalEntrySaved"
  />

  <EventDraftBar
    v-if="draftBarVisible"
    v-model:date="draftDate"
    v-model:time="draftTime"
    :entries="draftSignalEntries"
    @edit-entry="onEditSignalEntry"
    @remove-entry="onRemoveSignalEntry"
    @note-click="onNoteClick"
    @location-click="onLocationClick"
    @people-click="onPeopleClick"
    @cancel="onCancelDraft"
    @save="onSaveDraft"
  />
</template>

<style scoped>
.signal-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 0 var(--padding-app);
}

.signal-grid.has-draft-bar {
  padding-bottom: 220px;
}

.edit-hint {
  margin: 0 0 12px;
  padding: 0 var(--padding-app);
  font-size: var(--font-size-sm);
  color: var(--input-color-label);
}

.signal-card.is-editing {
  cursor: default;
}

.empty-state {
  grid-column: 1 / -1;
  padding: 24px;
  text-align: center;
  color: var(--input-color-label);
}
</style>
