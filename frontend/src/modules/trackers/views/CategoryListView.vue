<script setup lang="ts">
import { api } from '@/shared/api'
import { onMounted, ref } from 'vue'
import { isAxiosError } from 'axios'
import type { TrackerCategory } from '@/modules/trackers/types'

const categories = ref<TrackerCategory[]>([])
const categoriesError = ref('')

onMounted(() => {
  getCategories()
})

async function getCategories() {
  categoriesError.value = ''
  try {
    const { data } = await api.get<TrackerCategory[]>('/categories/')
    categories.value = data
  } catch (err) {
    if (isAxiosError(err)) {
      categoriesError.value = `error: ${err.response?.status} ${JSON.stringify(err.response?.data)}`
    } else {
      categoriesError.value = 'Unknown error'
    }
  }
}
</script>

<template>
  <div>
    <p v-if="categoriesError" style="color: red;">{{ categoriesError }}</p>
    <ul v-if="categories.length">
      <li v-for="cat in categories" :key="cat.id">
        {{ cat.icon }} {{ cat.name }} <span :style="{ color: cat.color }">●</span>
      </li>
    </ul>
    <p v-else-if="!categoriesError">No categories loaded yet.</p>
  </div>
</template>
