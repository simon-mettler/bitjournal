<script setup lang="ts">
import { ref, computed } from 'vue'
import Dialog from '@/shared/ui/components/Dialog.vue'

import {
  Camera, Heart, Star, Book, Coffee, Dumbbell, Droplet, Moon, Sun, Smile,
  Music, Pencil, Target, Wallet, ShoppingCart, Utensils, Bike, Car, Plane,
  Home, Briefcase, Brain, Pill, BedDouble, Flame, Leaf, Dog, Cat, Gamepad2,
} from '@lucide/vue'

const icons = {
  Camera, Heart, Star, Book, Coffee, Dumbbell, Droplet, Moon, Sun, Smile,
  Music, Pencil, Target, Wallet, ShoppingCart, Utensils, Bike, Car, Plane,
  Home, Briefcase, Brain, Pill, BedDouble, Flame, Leaf, Dog, Cat, Gamepad2,
} as const

type IconName = keyof typeof icons

const model = defineModel<string>()
const open = ref<boolean>(false)
const search = ref<string>('')

const currentIcon = computed(() =>
  model.value && model.value in icons
    ? icons[model.value as IconName]
    : null,
)

const filteredIcons = computed(() => {
  const query = search.value.trim().toLowerCase()
  const names = Object.keys(icons) as IconName[]
  if (!query) return names
  return names.filter((name) => name.toLowerCase().includes(query))
})

function selectIcon(name: IconName) {
  model.value = name
  open.value = false
}
</script>

<template>
  <Dialog v-model:open="open" title="Choose icon">
    <template #trigger>
      <button type="button" class="icon-trigger">
        <component :is="currentIcon" v-if="currentIcon" :size="24" />
        <span v-else class="icon-trigger-placeholder">Icon</span>
      </button>
    </template>

    <div class="icon-picker">
      <input v-model="search" type="text" placeholder="Search icons..." class="icon-picker-search" />
      <div class="icon-picker-grid">
        <button v-for="name in filteredIcons" :key="name" type="button" class="icon-picker-item"
          :class="{ 'icon-picker-item-selected': modelValue === name }" :title="name" @click="selectIcon(name)">
          <component :is="icons[name]" :size="24" />
        </button>
        <p v-if="filteredIcons.length === 0" class="icon-picker-empty">
          No icons found
        </p>
      </div>
    </div>
  </Dialog>
</template>

<style scoped>
.icon-trigger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: var(--input-radius);
  border: var(--input-border);
  background-color: var(--input-color-background);
  color: var(--input-color-text);
  cursor: pointer;
}

.icon-trigger:hover {
  background: #f9fafb;
}

.icon-trigger-placeholder {
  font-size: var(--font-size-sm);
  margin-bottom: 2px;
  color: var(--color-text-light);
}

.icon-picker {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  width: 100%;
}

.icon-picker-search {
  border-radius: var(--input-radius);
  padding: 0 10px;
  height: var(--input-height);
  font-size: var(--font-size-base);
  line-height: 1;
  color: var(--input-color-text);
  background-color: var(--input-color-background);
  border: var(--input-border);

  &:focus {
    box-shadow: var(--input-shadow-focus);
    border: var(--input-border-focus);
  }
}

.icon-picker-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  grid-auto-rows: 40px;
  gap: var(--spacing-xs);
  height: 200px;
  padding: 4px;
  overflow-y: auto;
  border: 2px solid transparent;
  border-radius: var(--radius-sm);
}

.icon-picker-item {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid transparent;
  border-radius: var(--radius-sm);
  background: none;
  cursor: pointer;

  &:hover {
    background: var(--color-surface-muted);
  }
}

.icon-picker-item-selected {
  background: var(--color-surface-muted);
  border: var(--input-border);
}

.icon-picker-empty {
  grid-column: 1 / -1;
  text-align: center;
  color: var(--color-text-light);
  font-size: var(--font-size-sm);
}
</style>
