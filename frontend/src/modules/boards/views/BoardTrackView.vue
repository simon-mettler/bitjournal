<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getBoards } from '../api';
import type { Board } from '@/modules/boards/types'

const boards = ref<Board[]>([])

async function loadBoards() {
  const { data } = await getBoards()
  boards.value = data
}
function navigateToBoard(board: Board) {
  console.log('output board: ', board)
}

onMounted(loadBoards)
</script>

<template>
  <ul ref="listEl" class="board-list">
    <!-- TODO:  tabs navigation -->
    <li v-for="board in boards" :key="board.id" class="board-row" @click="navigateToBoard(board)">
      <div class="board-info">
        <span class="board-name">{{ board.name }}</span>
      </div>
    </li>

    <li v-if="boards.length === 0" class="empty-state">
      No boards yet.
    </li>
  </ul>
  <!-- TODO: signals of the active board -->
</template>
