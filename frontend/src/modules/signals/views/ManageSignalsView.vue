<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import InputText from '@/shared/ui/components/InputText.vue'
import Header from '@/shared/ui/components/Header.vue'
import Button from '@/shared/ui/components/Button.vue'
import AppShellHeader from '@/shared/ui/layout/AppShellHeader.vue'
import { resolveIcon } from '@/shared/lib/iconRegistry'
import { ChevronRight } from '@lucide/vue'
import { getSignals } from '@/modules/signals/api'
import type { Signal } from '@/modules/signals/types'

const router = useRouter()
const search = ref('')
const signals = ref<Signal[]>([])

const errorLoad = ref<string | null>(null)
async function loadSignals() {
  try {
    const { data } = await getSignals()
    signals.value = data
  } catch (e) {
    errorLoad.value = 'Faild to load signals.'
  }
}

function openSignal(signal: Signal) {
  router.push({ name: 'signal-edit', params: { id: signal.id } })
}

const signalsWithIcon = computed(() =>
  filteredSignals.value.map(signal => ({
    ...signal,
    iconComponent: resolveIcon(signal.icon),
  })),
)

const filteredSignals = computed(() => {
  const query = search.value.trim().toLowerCase()
  if (!query) return signals.value
  return signals.value.filter(signal => signal.name.toLowerCase().includes(query))
})

function addSignal() {
  router.push({ name: 'signal-add' })
}

onMounted(loadSignals)
</script>

<template>
  <AppShellHeader>
    <Header heading="Manage signals">
    </Header>
  </AppShellHeader>

  <div class="manage-signals-content">
    <Button @click="addSignal">Create signal</Button>

    <InputText v-model="search" placeholder="Search signals..." />

    <ul class="signal-list">
      <li v-for="signal in signalsWithIcon" :key="signal.id" class="signal-row" @click="openSignal(signal)">
        <span class="signal-icon" :style="{ color: signal.color }">
          <component :is="signal.iconComponent" v-if="signal.iconComponent" />
        </span>

        <div class="signal-info">
          <span class="signal-name">{{ signal.name }}</span>
          <span class="signal-type">{{ signal.type }}</span>
        </div>

        <ChevronRight :size="20" class="board-chevron" />
      </li>

      <li v-if="filteredSignals.length === 0" class="empty-state">
        No signals found.
      </li>
    </ul>
  </div>

</template>

<style scoped>
.manage-signals-content {
  display: flex;
  flex-direction: column;
  padding: var(--padding-app);
  gap: 32px;
}

.signal-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.signal-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: var(--input-radius);
  background-color: white;
  cursor: pointer;
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

.empty-state {
  padding: 16px 4px;
  color: var(--input-color-label);
  font-size: var(--font-size-sm);
  text-align: center;
}
</style>
