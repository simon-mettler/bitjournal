<script setup lang="ts" generic="B extends { id: string; name: string }">
import { computed, ref } from 'vue'
import EditableTabs from '@/shared/ui/components/EditableTabs.vue'
import NameDialog from '@/shared/ui/components/NameDialog.vue'
import AlertDialog from '@/shared/ui/components/AlertDialog.vue'
import type { TabItem } from '@/shared/ui/components/Tabs.vue'
import { enqueueBoardWrite } from '@/shared/lib/boardWriteQueue'
import { useToast } from '@/shared/lib/useToast'

// Board tabs with the add / rename / reorder / delete flow of the board pages. The page supplies the API calls.
const props = withDefaults(defineProps<{
  noun?: 'board' | 'dashboard'
  editing: boolean
  showTabs: boolean
  pinned?: TabItem[]
  create: (name: string) => Promise<B>
  rename: (board: B, name: string) => Promise<unknown>
  remove: (board: B) => Promise<unknown>
  reorder: (ids: string[]) => Promise<unknown>
  reload: () => Promise<unknown>
  deleteDescription?: (board: B) => string
}>(), { noun: 'board' })

const boards = defineModel<B[]>('boards', { required: true })
const active = defineModel<string | null>('active', { required: true })
const toaster = useToast()

const nounCap = computed(() => props.noun.charAt(0).toUpperCase() + props.noun.slice(1))

const items = computed(() => boards.value.map((b) => ({ value: b.id, label: b.name })))

const nameDialogOpen = ref(false)
const nameDialogMode = ref<'add' | 'rename'>('add')
const nameDialogBusy = ref(false)
const renameTargetId = ref<string | null>(null)
const renameTarget = computed(() => boards.value.find((b) => b.id === renameTargetId.value))

function askAddBoard() {
  nameDialogMode.value = 'add'
  renameTargetId.value = null
  nameDialogOpen.value = true
}

function askRenameBoard(id: string) {
  nameDialogMode.value = 'rename'
  renameTargetId.value = id
  nameDialogOpen.value = true
}

async function submitName(name: string) {
  nameDialogBusy.value = true
  try {
    const target = renameTarget.value
    if (nameDialogMode.value === 'rename' && target) {
      await enqueueBoardWrite(() => props.rename(target, name))
      target.name = name
    } else {
      const board = await enqueueBoardWrite(() => props.create(name))
      boards.value.push(board)
      active.value = board.id
    }
    nameDialogOpen.value = false
  } catch {
    toaster.toast({ description: `Could not ${nameDialogMode.value === 'add' ? 'create' : 'rename'} ${props.noun}.`, variant: 'danger' })
  } finally {
    nameDialogBusy.value = false
  }
}

function onReorder(ids: string[]) {
  const byId = new Map(boards.value.map((b) => [b.id, b]))
  boards.value = ids.map((id) => byId.get(id)).filter((b): b is B => !!b)
  enqueueBoardWrite(() => props.reorder(ids)).catch(() => {
    toaster.toast({ description: 'Could not save new order.', variant: 'danger' })
    props.reload()
  })
}

const boardToDelete = ref<B | null>(null)
const deleteOpen = ref(false)
const deleteText = computed(() => {
  const board = boardToDelete.value
  if (!board) return ''
  return props.deleteDescription?.(board) ?? `Are you sure you want to delete the ${props.noun} "${board.name}"? This can't be undone.`
})

function askDeleteBoard(id: string) {
  boardToDelete.value = boards.value.find((b) => b.id === id) ?? null
  deleteOpen.value = true
}

async function confirmDelete() {
  const board = boardToDelete.value
  if (!board) return
  try {
    await enqueueBoardWrite(() => props.remove(board))
    const index = boards.value.findIndex((b) => b.id === board.id)
    boards.value = boards.value.filter((b) => b.id !== board.id)
    active.value = boards.value[Math.min(index, boards.value.length - 1)]?.id ?? null
    toaster.toast({ description: `Deleted "${board.name}".`, variant: 'success' })
  } catch {
    toaster.toast({ description: `Could not delete ${props.noun}.`, variant: 'danger' })
  }
}

defineExpose({ askAddBoard })
</script>

<template>
  <EditableTabs v-if="showTabs" :model-value="active ?? ''" :items="items" :pinned="pinned" :editing="editing"
    :add-label="`Add ${noun}`" class="board-tabs" @update:model-value="active = $event" @add="askAddBoard"
    @rename="askRenameBoard" @delete="askDeleteBoard" @reorder="onReorder" />

  <NameDialog v-model:open="nameDialogOpen" :busy="nameDialogBusy" :label="`${nounCap} name`"
    :title="`${nameDialogMode === 'add' ? 'Add' : 'Rename'} ${noun}`"
    :confirm-text="nameDialogMode === 'add' ? 'Create' : 'Save'" :initial-name="renameTarget?.name"
    @submit="submitName" />

  <AlertDialog v-model:open="deleteOpen" :title="`Delete ${noun}`" confirm-text="Delete" :description="deleteText"
    @confirm="confirmDelete" />
</template>

<style scoped>
.board-tabs {
  width: 100vw;
  margin: 10px 0 0 -16px;
}
</style>
