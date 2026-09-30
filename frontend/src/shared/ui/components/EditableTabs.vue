<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { ArrowLeft, ArrowRight, MoreVertical, Pencil, Plus, Trash2 } from '@lucide/vue'
import Tabs from '@/shared/ui/components/Tabs.vue'
import type { TabItem } from '@/shared/ui/components/Tabs.vue'
import IconButton from '@/shared/ui/components/IconButton.vue'
import DropdownMenu from '@/shared/ui/components/DropdownMenu.vue'
import { useSortableList } from '@/shared/lib/useSortableList'
import type { DropdownMenuOption } from '@/shared/ui/components/DropdownMenu.vue'

const props = defineProps<{
  items: TabItem[]
  pinned?: TabItem[] // fixed tabs (like 'All')
  editing: boolean
  addLabel?: string
}>()

const emit = defineEmits<{
  add: []
  rename: [id: string]
  delete: [id: string]
  reorder: [ids: string[]]
}>()

const model = defineModel<string>({ required: true })

const listEl = ref<HTMLElement | null>(null)
const list = ref<TabItem[]>([...props.items])
watch(
  () => props.items,
  (items) => (list.value = [...items]),
)

const allItems = computed(() => [...(props.pinned ?? []), ...props.items])

useSortableList(listEl, list, {
  delay: 200,
  delayOnTouchOnly: true,
  touchStartThreshold: 5,
  onSorted: () => emit('reorder', list.value.map((i) => i.value)),
})

function move(id: string, offset: -1 | 1) {
  const ids = props.items.map((i) => i.value)
  const from = ids.indexOf(id)
  const to = from + offset
  if (from === -1 || to < 0 || to >= ids.length) return
  ids.splice(to, 0, ids.splice(from, 1)[0])
  emit('reorder', ids)
}

function menuOptions(item: TabItem, index: number): DropdownMenuOption[] {
  const options: DropdownMenuOption[] = [
    { label: 'Rename', value: 'rename', icon: Pencil, onSelect: () => emit('rename', item.value) },
  ]
  if (index > 0) {
    options.push({ label: 'Move left', value: 'left', icon: ArrowLeft, onSelect: () => move(item.value, -1) })
  }
  if (index < props.items.length - 1) {
    options.push({ label: 'Move right', value: 'right', icon: ArrowRight, onSelect: () => move(item.value, 1) })
  }
  options.push(
    { type: 'separator' },
    { label: 'Delete', value: 'delete', icon: Trash2, onSelect: () => emit('delete', item.value) },
  )
  return options
}
</script>

<template>
  <Tabs v-if="!editing" v-model="model" :items="allItems" />

  <div v-else class="edit-tabs">
    <button v-for="item in pinned" :key="item.value" type="button" class="chip"
      :class="{ active: model === item.value }" :aria-pressed="model === item.value" @click="model = item.value">
      {{ item.label }}
    </button>

    <div ref="listEl" class="edit-tabs-list">
      <div v-for="(item, index) in list" :key="item.value" class="chip editable"
        :class="{ active: model === item.value }">
        <button type="button" class="chip-label" :aria-pressed="model === item.value" @click="model = item.value">
          {{ item.label }}
        </button>
        <DropdownMenu v-if="model === item.value" :options="menuOptions(item, index)" align="start">
          <template #trigger>
            <IconButton variant="tertiary" size="sm" class="chip-menu" :aria-label="`Options for ${item.label}`">
              <MoreVertical :size="16" />
            </IconButton>
          </template>
        </DropdownMenu>
      </div>
    </div>

    <button type="button" class="chip add" @click="emit('add')">
      <Plus :size="16" />
      {{ addLabel ?? 'Add' }}
    </button>
  </div>
</template>

<style scoped>
.edit-tabs {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow-x: auto;
  scrollbar-width: none;
  padding: 0 16px;
  box-sizing: border-box;
}

.edit-tabs::-webkit-scrollbar {
  display: none;
}

.edit-tabs-list {
  display: flex;
  gap: 8px;
}

.chip {
  all: unset;
  box-sizing: border-box;
  display: inline-flex;
  align-items: center;
  flex-shrink: 0;
  padding: 8px 16px;
  border-radius: var(--radius-xl);
  border: 1px solid #62656B;
  font-size: var(--font-size-sm);
  color: var(--input-color-text);
  white-space: nowrap;
  cursor: pointer;
}

.chip:focus-visible {
  box-shadow: var(--input-shadow-focus);
}

.chip.editable {
  padding: 0;
  cursor: grab;
  touch-action: pan-x;
}

.chip.editable:active {
  cursor: grabbing;
}

.chip-label {
  all: unset;
  padding: 8px 16px;
  display: inline-flex;
  align-items: center;
  cursor: inherit;
}

.chip.active {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
  color: var(--color-surface);
  font-weight: var(--font-weight-bold);
}

.chip.editable.active .chip-label {
  padding-right: 4px;
}

.chip-menu {
  margin-block: -8px;
}

.chip.active :deep(svg) {
  color: var(--color-surface);
}

.chip.add {
  gap: 4px;
  padding: 8px 14px 8px 10px;
  border-style: dashed;
}
</style>
