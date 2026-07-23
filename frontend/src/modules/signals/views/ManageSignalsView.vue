<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import AddSignalDialog from '@/modules/signals/components/AddSignalDialog.vue'
import EditSignalDialog from '@/modules/signals/components/EditSignalDialog.vue'
import AlertDialog from '@/shared/ui/components/AlertDialog.vue'
import Button from '@/shared/ui/components/Button.vue'
import InputText from '@/shared/ui/components/InputText.vue'
import type { Signal } from '@/modules/signals/types'
import { deleteSignal, getSignals } from '@/modules/signals/api'
import { useToast } from '@/shared/lib/useToast'
const { toast } = useToast()

import { Pencil, Trash2 } from '@lucide/vue'
const signals = ref<Signal[]>([])
const search = ref('')
const loading = ref(false)
const deletingId = ref<number | null>(null)
import { resolveIcon } from '@/shared/lib/iconRegistry'

const signalsWithIcon = computed(() =>
  filteredSignals.value.map(t => ({
    ...t,
    iconComponent: resolveIcon(t.icon),
  })),
)

const filteredSignals = computed(() => {
  const query = search.value.trim().toLowerCase()
  if (!query) return signals.value
  return signals.value.filter(t => t.name.toLowerCase().includes(query))
})

const errorLoad = ref<string | null>(null)
async function loadSignals() {
  loading.value = true
  try {
    const { data } = await getSignals()
    signals.value = data
  } catch (e) {
    errorLoad.value = 'Faild to load signals.'
  } finally {
    loading.value = false
  }
}

async function onDeleteConfirm(signal: Signal) {
  deletingId.value = signal.id
  try {
    await deleteSignal(signal.id)
    signals.value = signals.value.filter(t => t.id !== signal.id)
    toast({ description: `${signal.name} deleted`, variant: 'success' })
  } catch (err) {
    toast({
      title: 'Delete failed',
      description: `Faild to delete signal ${signal.name}`,
      variant: 'error',
    })
    console.error('Failed to delete signal.', err)
  } finally {
    deletingId.value = null
  }
}

function onSignalCreated(signal: Signal) {
  signals.value.push(signal)
}

function onSignalUpdated(updated: Signal) {
  const i = signals.value.findIndex(t => t.id === updated.id)
  if (i !== -1) signals.value[i] = updated
}

onMounted(loadSignals)
</script>

<template>
  <h1>Manage signals</h1>

  <div class="card">
    <InputText v-model="search" placeholder="Search signals..." />

    <ul class="signal-list">
      <li v-for="signal in signalsWithIcon" :key="signal.id" class="signal-row">
        <span class="signal-icon" :style="{ color: signal.color }">
          <component :is="signal.iconComponent" v-if="signal.iconComponent" />
        </span>

        <div class="signal-info">
          <span class="signal-name">{{ signal.name }}</span>
          <span class="signal-type">{{ signal.type }}</span>
        </div>

        <EditSignalDialog :signal="signal" @updated="onSignalUpdated">
          <template #trigger>
            <button type="button" class="icon-btn" :aria-label="`Edit ${signal.name}`">
              <Pencil />
            </button>
          </template>
        </EditSignalDialog>

        <AlertDialog title="Delete signal" confirmText="Delete"
          :description="`Are you sure you want to delete ${signal.name}? This action can't be undone.`"
          @confirm="onDeleteConfirm(signal)">
          <template #trigger>
            <button type="button" class="icon-btn icon-btn-danger" :aria-label="`Delete ${signal.name}`">
              <Trash2 />
            </button>
          </template>
        </AlertDialog>
      </li>

      <li v-if="!loading && filteredSignals.length === 0" class="empty-state">
        No signals found.
      </li>
    </ul>
  </div>

  <AddSignalDialog @created="onSignalCreated" />
</template>

<style scoped>
.card {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  border-radius: var(--input-radius);
  border: var(--input-border);
  background-color: var(--input-color-background);
  margin-bottom: 16px;
}

.signal-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.signal-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 4px;
  border-bottom: var(--input-border);
}

.signal-row:last-child {
  border-bottom: none;
}

.signal-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  font-size: 20px;
}

.signal-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.signal-name {
  font-size: var(--font-size-base);
  color: var(--input-color-text);
}

.signal-type {
  font-size: var(--font-size-sm);
  color: var(--input-color-label);
  text-transform: capitalize;
}

.icon-btn {
  all: unset;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--input-radius);
  cursor: pointer;
  color: var(--input-color-text);
  flex-shrink: 0;
}

.icon-btn:hover {
  background-color: var(--color-surface-muted);
}

.icon-btn-danger:hover {
  color: var(--color-danger);
}

.empty-state {
  padding: 16px 4px;
  color: var(--input-color-label);
  font-size: var(--font-size-sm);
  text-align: center;
}
</style>
