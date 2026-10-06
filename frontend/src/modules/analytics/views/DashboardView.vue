<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef, watch } from 'vue'
import { onBeforeRouteLeave, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { Check, GripVertical, MoreVertical, Pencil, X } from '@lucide/vue'
import AppShellHeader from '@/shared/ui/layout/AppShellHeader.vue'
import Header from '@/shared/ui/components/Header.vue'
import Button from '@/shared/ui/components/Button.vue'
import IconButton from '@/shared/ui/components/IconButton.vue'
import AddTile from '@/shared/ui/components/AddTile.vue'
import BoardTabs from '@/shared/ui/components/BoardTabs.vue'
import AlertDialog from '@/shared/ui/components/AlertDialog.vue'
import DropdownMenu from '@/shared/ui/components/DropdownMenu.vue'
import type { DropdownMenuOption } from '@/shared/ui/components/DropdownMenu.vue'
import {
  createAnalyticsBoard,
  deleteAnalyticsBoard,
  deleteAnalyticsWidget,
  getAnalyticsBoardValues,
  getAnalyticsBoards,
  reorderAnalyticsBoards,
  updateAnalyticsBoard,
} from '@/modules/analytics/api'
import TimeseriesChart from '@/modules/analytics/components/TimeseriesChart.vue'
import { formatStatValue, formatWidgetTimeframe } from '@/modules/analytics/format'
import { periodUsesWeeklyBins } from '@/modules/analytics/timeseriesBins'
import { useDashboardUiStore } from '@/modules/analytics/store/dashboardUiStore'
import type {
  AnalyticsBoard,
  AnalyticsWidget,
  AnalyticsWidgetValue,
} from '@/modules/analytics/types'
import { useToast } from '@/shared/lib/useToast'
import { enqueueBoardWrite } from '@/shared/lib/boardWriteQueue'
import { resolveIcon } from '@/shared/lib/iconRegistry'
import { useSortableList } from '@/shared/lib/useSortableList'

const router = useRouter()
const toaster = useToast()

const { activeBoardId, editing } = storeToRefs(useDashboardUiStore())

const loading = ref(true)
const boards = ref<AnalyticsBoard[]>([])
const values = ref<Record<string, AnalyticsWidgetValue>>({})

const activeBoard = computed(() => boards.value.find((b) => b.id === activeBoardId.value))

const widgets = computed<AnalyticsWidget[]>({
  get: () => activeBoard.value?.widgets ?? [],
  set: (value) => {
    if (activeBoard.value) activeBoard.value.widgets = value
  },
})

async function loadBoards() {
  loading.value = true
  try {
    const { data } = await getAnalyticsBoards()
    boards.value = data
    if (!boards.value.some((b) => b.id === activeBoardId.value)) {
      activeBoardId.value = boards.value[0]?.id ?? null
    }
  } finally {
    loading.value = false
  }
}

async function loadValues(boardId: string) {
  try {
    const { data } = await getAnalyticsBoardValues(boardId)
    if (boardId !== activeBoardId.value) return
    values.value = Object.fromEntries(data.map((v) => [v.widget_id, v]))
  } catch {
    toaster.toast({ description: 'Could not load dashboard values.', variant: 'danger' })
  }
}

watch(activeBoardId, (id) => {
  values.value = {}
  if (id) void loadValues(id)
})

const hasNoEntries = (widget: AnalyticsWidget) => values.value[widget.id]?.count === 0

function displayValue(widget: AnalyticsWidget): string {
  const value = values.value[widget.id]
  if (!value) return '…'
  if (value.count === 0 || value.value === null) return '–'
  return formatStatValue(widget.signal, value.value)
}

// TABS (BOARDS)

const boardTabs = useTemplateRef<{ askAddBoard: () => void }>('boardTabs')

const boardApi = {
  create: async (name: string) => (await createAnalyticsBoard({ name })).data,
  rename: (board: AnalyticsBoard, name: string) =>
    updateAnalyticsBoard(board.id, { name, widget_ids: board.widgets.map((w) => w.id) }),
  remove: (board: AnalyticsBoard) => deleteAnalyticsBoard(board.id),
  reorder: (ids: string[]) => reorderAnalyticsBoards({ board_ids: ids }),
  reload: loadBoards,
}

function describeBoardDelete(board: AnalyticsBoard) {
  const count = board.widgets.length
  const widgetsNote = count > 0 ? ` and its ${count} widget${count === 1 ? '' : 's'}` : ''
  return `Are you sure you want to delete "${board.name}"${widgetsNote}? This can't be undone.`
}

// WIDGETS

const gridEl = ref<HTMLElement | null>(null)

function persistWidgetOrder() {
  const board = activeBoard.value
  if (!board) return
  enqueueBoardWrite(() =>
    updateAnalyticsBoard(board.id, {
      name: board.name,
      widget_ids: board.widgets.map((w) => w.id),
    }),
  ).catch(() => {
    toaster.toast({ description: 'Could not save new order.', variant: 'danger' })
    void loadBoards()
  })
}

useSortableList(gridEl, widgets, {
  handle: '.widget-handle',
  draggable: '.widget-card',
  ghostClass: 'widget-ghost',
  enabled: editing,
  onSorted: persistWidgetOrder,
})

const widgetToDelete = ref<AnalyticsWidget | null>(null)
const deleteWidgetOpen = ref(false)

function askDeleteWidget(widget: AnalyticsWidget) {
  widgetToDelete.value = widget
  deleteWidgetOpen.value = true
}

async function confirmDeleteWidget() {
  const widget = widgetToDelete.value
  const board = activeBoard.value
  if (!widget || !board) return
  try {
    await enqueueBoardWrite(() => deleteAnalyticsWidget(widget.id))
    board.widgets = board.widgets.filter((w) => w.id !== widget.id)
    toaster.toast({ description: `Deleted "${widget.title}".`, variant: 'success' })
  } catch {
    toaster.toast({ description: 'Could not delete widget.', variant: 'danger' })
  }
}

function openWidget(widget: AnalyticsWidget) {
  void router.push({ name: 'analytics-widget-edit', params: { id: widget.id } })
}

function openAddWidget() {
  if (!activeBoard.value) return
  void router.push({ name: 'analytics-widget-add', params: { boardId: activeBoard.value.id } })
}

function widgetOptions(widget: AnalyticsWidget): DropdownMenuOption[] {
  return [
    {
      label: 'Edit widget',
      value: 'edit-widget',
      icon: Pencil,
      onSelect: () => openWidget(widget),
    },
  ]
}

// EDIT MODE

// keep edit mode on for widget analytics widget routes, off otherwise
onBeforeRouteLeave((to) => {
  if (typeof to.name !== 'string' || !to.name.startsWith('analytics-widget')) {
    editing.value = false
  }
})

onMounted(async () => {
  const previousId = activeBoardId.value
  await loadBoards()
  if (boards.value.length === 0) editing.value = false
  if (activeBoardId.value && activeBoardId.value === previousId)
    void loadValues(activeBoardId.value)
})
</script>

<template>
  <AppShellHeader>
    <Header :heading="editing ? 'Edit dashboard' : 'Dashboard'">
      <template #actions>
        <IconButton
          v-if="editing"
          variant="primary"
          aria-label="Done editing"
          @click="editing = false"
        >
          <Check />
        </IconButton>
        <IconButton
          v-else-if="boards.length > 0"
          variant="tertiary"
          aria-label="Edit dashboard"
          @click="editing = true"
        >
          <Pencil />
        </IconButton>
      </template>
      <template #content>
        <BoardTabs
          ref="boardTabs"
          v-model:boards="boards"
          v-model:active="activeBoardId"
          noun="dashboard"
          :editing="editing"
          :show-tabs="boards.length > 0 && (editing || boards.length > 1)"
          :delete-description="describeBoardDelete"
          v-bind="boardApi"
        />
      </template>
    </Header>
  </AppShellHeader>

  <div ref="gridEl" class="widget-grid" :class="{ editing }">
    <template v-if="!loading">
      <div
        v-for="widget in widgets"
        :key="widget.id"
        class="widget-card"
        :class="{ editing, wide: widget.type === 'timeseries' }"
        @click="editing && openWidget(widget)"
      >
        <div class="widget-top">
          <span v-if="editing" class="widget-handle" aria-hidden="true" @click.stop>
            <GripVertical :size="18" />
          </span>
          <component
            :is="resolveIcon(widget.signal.icon)"
            class="widget-icon"
            :size="18"
            :style="{ color: widget.signal.color }"
          />
          <span class="widget-title">{{ widget.title }}</span>
          <IconButton
            v-if="editing"
            variant="tertiary"
            size="sm"
            :aria-label="`Delete ${widget.title}`"
            @click.stop="askDeleteWidget(widget)"
          >
            <X />
          </IconButton>
          <DropdownMenu v-else :options="widgetOptions(widget)">
            <template #trigger>
              <IconButton :aria-label="`Options for ${widget.title}`" variant="tertiary" size="sm">
                <MoreVertical />
              </IconButton>
            </template>
          </DropdownMenu>
        </div>
        <template v-if="widget.type === 'timeseries'">
          <p v-if="hasNoEntries(widget)" class="widget-chart-placeholder">
            No entries in this period
          </p>
          <p v-else-if="!values[widget.id]?.timeseries" class="widget-chart-placeholder">…</p>
          <TimeseriesChart
            v-else
            :signal="widget.signal"
            :timeseries="values[widget.id].timeseries!"
            :chart-type="widget.chart_type"
            :show-average="widget.show_average"
            :weekly="periodUsesWeeklyBins(values[widget.id].period)"
            :height="220"
          />
          <span class="widget-meta">{{ formatWidgetTimeframe(widget) }}</span>
        </template>
        <template v-else>
          <span class="widget-value" :style="{ color: widget.signal.color }">{{
            displayValue(widget)
          }}</span>
          <span class="widget-meta">
            {{
              hasNoEntries(widget)
                ? 'No entries'
                : widget.aggregation === 'average'
                  ? 'Average'
                  : 'Total'
            }}
            · {{ formatWidgetTimeframe(widget) }}
          </span>
        </template>
      </div>

      <AddTile v-if="editing && activeBoard" class="add-widget-tile" @click="openAddWidget"
        >Add widget</AddTile
      >

      <div v-if="boards.length === 0" class="empty-state">
        <p>No dashboards yet.</p>
        <Button variant="primary" @click="boardTabs?.askAddBoard()">Create dashboard</Button>
      </div>
      <div v-else-if="widgets.length === 0 && !editing" class="empty-state">
        <p>No widgets in this dashboard yet.</p>
        <Button variant="primary" @click="openAddWidget">Add widget</Button>
      </div>
    </template>
  </div>

  <AlertDialog
    v-model:open="deleteWidgetOpen"
    title="Delete widget"
    confirm-text="Delete"
    :description="`Are you sure you want to delete &quot;${widgetToDelete?.title ?? ''}&quot;? This can't be undone.`"
    @confirm="confirmDeleteWidget"
  />
</template>

<style scoped>
.widget-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 0 var(--padding-app);
}

.widget-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
  padding: 10px 7px 14px 14px;
  border-radius: var(--input-radius);
  background-color: var(--color-surface);
  box-shadow: var(--shadow-card);
}

.widget-card.wide {
  grid-column: 1 / -1;
  padding-right: 14px;
}

.widget-chart-placeholder {
  height: 220px;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--input-color-label);
}

.widget-card.editing {
  cursor: pointer;
}

.widget-ghost {
  opacity: 0.4;
}

.widget-top {
  display: flex;
  align-items: center;
  gap: 4px;
}

.widget-handle {
  display: inline-flex;
  padding: 8px 4px 8px 0;
  margin: -8px 0;
  color: var(--input-color-label);
  cursor: grab;
  touch-action: none;
}

.widget-handle:active {
  cursor: grabbing;
}

.widget-icon {
  flex-shrink: 0;
}

.widget-title {
  flex: 1;
  min-width: 0;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.widget-value {
  font-size: var(--font-size-h1);
  font-weight: var(--font-weight-bold);
}

.widget-meta {
  font-size: var(--font-size-sm);
  color: var(--input-color-label);
}

.add-widget-tile {
  min-height: 112px;
}

.empty-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px;
  text-align: center;
  color: var(--input-color-label);
}

.empty-state p {
  margin: 0;
}
</style>
