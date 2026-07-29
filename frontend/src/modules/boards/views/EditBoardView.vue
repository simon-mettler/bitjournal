<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, GripVertical, Trash2 } from '@lucide/vue'
import { useSortable } from '@vueuse/integrations/useSortable'
import type { UseSortableOptions } from '@vueuse/integrations/useSortable'
import Button from '@/shared/ui/components/Button.vue'
import InputText from '@/shared/ui/components/InputText.vue'
import AlertDialog from '@/shared/ui/components/AlertDialog.vue'
import SignalCard from '@/shared/ui/components/SignalCard.vue'
import SignalPickerDialog from '@/modules/boards/components/SignalPickerDialog.vue'
import { deleteBoard, getBoard, updateBoard } from '@/modules/boards/api'
import type { Signal } from '@/modules/signals/types'
import { useToast } from '@/shared/lib/useToast'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const boardId = route.params.id as string

const boardName = ref('')
const signals = ref<Signal[]>([])
const gridEl = ref<HTMLElement | null>(null)
const saving = ref(false)
const loading = ref(true)

useSortable(gridEl, signals, {
  handle: '.drag-handle',
  animation: 300,
} as UseSortableOptions)

async function load() {
  loading.value = true
  try {
    const { data } = await getBoard(boardId)
    boardName.value = data.name
    signals.value = data.board_signals.map(bs => bs.signal)
  } finally {
    loading.value = false
  }
}

function onSignalsAdded(added: Signal[]) {
  signals.value.push(...added)
}

function removeSignal(id: string) {
  signals.value = signals.value.filter(s => s.id !== id)
}

async function save() {
  saving.value = true
  try {
    await updateBoard(boardId, {
      name: boardName.value.trim(),
      signal_ids: signals.value.map(s => s.id),
    })
    toast.toast({ description: 'Board saved.', variant: 'success' })
    router.push({ name: 'manage-boards' })
  } catch {
    toast.toast({ description: 'Could not save board.', variant: 'error' })
  } finally {
    saving.value = false
  }
}

async function confirmDeleteBoard() {
  try {
    await deleteBoard(boardId)
    router.push({ name: 'manage-boards' })
  } catch {
    toast.toast({ description: 'Could not delete board.', variant: 'error' })
  }
}

onMounted(load)
</script>

<template>
  <div class="edit-board-header">
    <button type="button" class="back-btn" aria-label="Back to boards" @click="router.push({ name: 'manage-boards' })">
      <ArrowLeft :size="22" />
    </button>
    <h1>Edit board</h1>
    <Button variant="primary" :disabled="saving || loading" @click="save">
      {{ saving ? 'Saving...' : 'Save' }}
    </Button>
  </div>

  <div v-if="!loading" class="card">
    <InputText v-model="boardName" label="Board name" placeholder="" />

    <div class="board-actions">
      <AlertDialog title="Delete board" confirm-text="Delete"
        :description="`Are you sure you want to delete &quot;${boardName}&quot;? This can't be undone.`"
        @confirm="confirmDeleteBoard">
        <template #trigger>
          <Button variant="secondary" class="danger-btn">Delete board</Button>
        </template>
        <template #cancel>
          <Button variant="secondary">Cancel</Button>
        </template>
        <template #action>
          <Button variant="primary">Delete</Button>
        </template>
      </AlertDialog>

      <SignalPickerDialog :exclude-ids="signals.map(s => s.id)" @add="onSignalsAdded" />
    </div>
  </div>

  <div ref="gridEl" class="signal-grid">
    <SignalCard v-for="signal in signals" :key="signal.id" :signal="signal">
      <template #handle>
        <span class="drag-handle">
          <GripVertical :size="18" />
        </span>
      </template>
      <template #actions>
        <button type="button" class="icon-btn icon-btn-danger" :aria-label="`Remove ${signal.name} from board`"
          @click="removeSignal(signal.id)">
          <Trash2 :size="18" />
        </button>
      </template>
    </SignalCard>
  </div>
</template>

<style scoped>
.edit-board-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.edit-board-header h1 {
  flex: 1;
  margin: 0;
}

.back-btn {
  all: unset;
  display: inline-flex;
  cursor: pointer;
  color: var(--color-primary);
}

.card {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  border-radius: var(--input-radius);
  background-color: var(--input-color-background);
  margin-bottom: 16px;
}

.board-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.danger-btn {
  color: var(--color-danger);
  border-color: var(--color-danger);
}

.signal-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.drag-handle {
  display: inline-flex;
  color: var(--input-color-label);
  cursor: grab;
  touch-action: none;
}

.drag-handle:active {
  cursor: grabbing;
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
  color: var(--color-danger);
}

.icon-btn-danger:hover {
  background-color: var(--color-surface-muted);
}
</style>
