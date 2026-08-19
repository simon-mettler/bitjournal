<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ChevronRight, GripVertical } from '@lucide/vue'
import { useSortable, type UseSortableOptions } from '@vueuse/integrations/useSortable'
import AddBoardDialog from '@/modules/boards/components/AddBoardDialog.vue'
import { getBoards, reorderBoards } from '@/modules/boards/api'
import type { Board } from '@/modules/boards/types'
import { useToast } from '@/shared/lib/useToast'

const router = useRouter()
const toast = useToast()

const boards = ref<Board[]>([])
const listEl = ref<HTMLElement | null>(null)

async function loadBoards() {
  const { data } = await getBoards()
  boards.value = data
}

function onBoardCreated(board: Board) {
  boards.value.push(board)
}

function openBoard(board: Board) {
  router.push({ name: 'board-edit', params: { id: board.id } })
}

async function persistOrder() {
  try {
    await reorderBoards({ board_ids: boards.value.map(b => b.id) })
  } catch {
    toast.toast({ description: 'Could not save new order.', variant: 'error' })
    loadBoards()
  }
}

useSortable(listEl, boards, {
  handle: '.drag-handle',
  animation: 150,
  onEnd: persistOrder,
} as UseSortableOptions)

onMounted(loadBoards)
</script>

<template>
  <h1>Signal boards</h1>

  <div class="card">
    <ul ref="listEl" class="board-list">
      <li v-for="board in boards" :key="board.id" class="board-row" @click="openBoard(board)">
        <span class="drag-handle" @click.stop>
          <GripVertical :size="18" />
        </span>

        <div class="board-info">
          <span class="board-name">{{ board.name }}</span>
          <span class="board-count">{{ board.board_signals.length }} signals</span>
        </div>

        <ChevronRight :size="20" class="board-chevron" />
      </li>

      <li v-if="boards.length === 0" class="empty-state">
        No boards yet.
      </li>
    </ul>
  </div>

  <AddBoardDialog @created="onBoardCreated" />
</template>

<style scoped>
.card {
  display: flex;
  flex-direction: column;
  padding: 8px;
  border-radius: var(--input-radius);
  background-color: var(--color-surface-muted, transparent);
  margin-bottom: 16px;
}

.board-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.board-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: var(--input-radius);
  background-color: white;
  cursor: pointer;
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

.board-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 2px;
}

.board-name {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
}

.board-count {
  font-size: var(--font-size-sm);
  color: var(--input-color-label);
}

.board-chevron {
  color: var(--input-color-label);
  flex-shrink: 0;
}

.empty-state {
  padding: 24px;
  text-align: center;
  color: var(--input-color-label);
  font-size: var(--font-size-sm);
}
</style>
