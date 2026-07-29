<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import Modal from '@/shared/ui/components/Dialog.vue'
import Button from '@/shared/ui/components/Button.vue'
import InputText from '@/shared/ui/components/InputText.vue'
import { DialogClose } from 'reka-ui'
import { getSignals } from '@/modules/signals/api'
import type { Signal } from '@/modules/signals/types'

const props = defineProps<{
  excludeIds: string[]
}>()
const emit = defineEmits<{ add: [signals: Signal[]] }>()

const open = ref(false)
const search = ref('')
const allSignals = ref<Signal[]>([])
const selectedIds = ref<Set<string>>(new Set())

async function loadSignals() {
  const { data } = await getSignals()
  allSignals.value = data
}

const availableSignals = computed(() =>
  allSignals.value.filter(s => !props.excludeIds.includes(s.id))
)

const filteredSignals = computed(() => {
  const query = search.value.trim().toLowerCase()
  if (!query) return availableSignals.value
  return availableSignals.value.filter(s => s.name.toLowerCase().includes(query))
})

function toggle(id: string) {
  if (selectedIds.value.has(id)) selectedIds.value.delete(id)
  else selectedIds.value.add(id)
}

function confirmAdd() {
  const chosen = allSignals.value.filter(s => selectedIds.value.has(s.id))
  emit('add', chosen)
  selectedIds.value = new Set()
  open.value = false
}

onMounted(loadSignals)
</script>

<template>
  <Modal v-model:open="open" title="Add signals">
    <template #trigger>
      <slot name="trigger">
        <Button>Add signal</Button>
      </slot>
    </template>

    <InputText v-model="search" placeholder="Search signals..." />

    <ul class="picker-list">
      <li v-for="signal in filteredSignals" :key="signal.id" class="picker-row"
        :class="{ selected: selectedIds.has(signal.id) }" @click="toggle(signal.id)">
        <span class="picker-name">{{ signal.name }}</span>
        <span class="picker-type">{{ signal.type }}</span>
      </li>
      <li v-if="filteredSignals.length === 0" class="empty-state">No signals found.</li>
    </ul>

    <template #footer>
      <DialogClose as-child>
        <Button variant="secondary">Cancel</Button>
      </DialogClose>
      <Button variant="primary" :disabled="selectedIds.size === 0" @click="confirmAdd">
        Add {{ selectedIds.size || '' }}
      </Button>
    </template>
  </Modal>
</template>

<style scoped>
.picker-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.picker-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: var(--input-radius);
  cursor: pointer;
}

.picker-row:hover {
  background-color: var(--color-surface-muted);
}

.picker-row.selected {
  background-color: var(--color-primary);
  color: white;
}

.picker-type {
  color: var(--input-color-label);
  font-size: var(--font-size-sm);
}

.picker-row.selected .picker-type {
  color: white;
  opacity: 0.85;
}

.empty-state {
  padding: 16px;
  text-align: center;
  color: var(--input-color-label);
}
</style>
