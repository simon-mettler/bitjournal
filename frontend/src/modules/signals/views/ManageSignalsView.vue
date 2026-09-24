<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import InputText from '@/shared/ui/components/InputText.vue'
import Header from '@/shared/ui/components/Header.vue'
import Button from '@/shared/ui/components/Button.vue'
import AppShellHeader from '@/shared/ui/layout/AppShellHeader.vue'
import AppShellFooter from '@/shared/ui/layout/AppShellFooter.vue'
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

  <AppShellFooter>
    <div class="add-signal-anchor">
      <Button variant="float" class="add-signal-button" @click="addSignal">Create signal</Button>
    </div>
  </AppShellFooter>

  <div class="manage-signals-content">
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
  padding-bottom: calc(var(--spacing-md) * 2 + 48px);
  gap: 32px;
}

.add-signal-anchor {
  position: relative;
  height: 0;
}

.add-signal-button {
  position: absolute;
  bottom: var(--spacing-md);
  left: 0;
  right: 0;
  margin-inline: auto;
  width: fit-content;
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
  box-shadow: var(--shadow-card);
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
