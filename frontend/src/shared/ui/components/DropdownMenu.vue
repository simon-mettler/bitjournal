<script setup lang="ts">
import {
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuItemIndicator,
  DropdownMenuLabel,
  DropdownMenuPortal,
  DropdownMenuRoot,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from 'reka-ui'
import { Check } from '@lucide/vue'

export interface DropdownMenuOption {
  type?: 'item' | 'separator' | 'label'
  label?: string
  value?: string
  disabled?: boolean
  icon?: any
  onSelect?: () => void
}

const props = withDefaults(
  defineProps<{
    options: DropdownMenuOption[]
    align?: 'start' | 'center' | 'end'
    side?: 'top' | 'right' | 'bottom' | 'left'
    sideOffset?: number
    modelValue?: string
  }>(),
  {
    align: 'start',
    side: 'bottom',
    sideOffset: 2,
  },
)

const emit = defineEmits<{
  select: [value: string | undefined, option: DropdownMenuOption]
  'update:modelValue': [value: string | undefined]
}>()

function handleSelect(option: DropdownMenuOption) {
  if (option.disabled)
    return
  option.onSelect?.()
  emit('select', option.value, option)
  emit('update:modelValue', option.value)
}
</script>

<template>
  <DropdownMenuRoot>
    <DropdownMenuTrigger as-child>
      <slot name="trigger" />
    </DropdownMenuTrigger>

    <DropdownMenuPortal>
      <DropdownMenuContent class="dropdown-content" :align="props.align" :side="props.side"
        :side-offset="props.sideOffset">
        <template v-for="(option, index) in props.options" :key="option.value ?? index">
          <DropdownMenuSeparator v-if="option.type === 'separator'" class="dropdown-separator" />

          <DropdownMenuLabel v-else-if="option.type === 'label'" class="dropdown-label">
            {{ option.label }}
          </DropdownMenuLabel>

          <DropdownMenuItem v-else class="dropdown-item"
            :class="{ 'dropdown-item--checked': option.value !== undefined && option.value === props.modelValue }"
            :disabled="option.disabled" @select="handleSelect(option)">
            <DropdownMenuItemIndicator class="dropdown-item-indicator">
              <Check :size="14" />
            </DropdownMenuItemIndicator>

            <component :is="option.icon" v-if="option.icon" class="dropdown-item-icon" :size="16" />

            <span class="dropdown-item-label">{{ option.label }}</span>
          </DropdownMenuItem>
        </template>
      </DropdownMenuContent>
    </DropdownMenuPortal>
  </DropdownMenuRoot>
</template>

<style>
.dropdown-content {
  min-width: 200px;
  margin: 0 var(--padding-app);
  padding: 5px;
  border-radius: var(--input-radius, 8px);
  border: var(--input-border, 1px solid #e2e2e2);
  box-shadow: var(--shadow-md, 0 10px 38px -10px rgba(22, 23, 24, 0.35), 0 10px 20px -15px rgba(22, 23, 24, 0.2));
  background-color: var(--color-surface, #ffffff);
  animation-duration: 500ms;
  animation-timing-function: cubic-bezier(0.16, 1, 0.3, 1);
  will-change: transform, opacity;
}

.dropdown-content[data-side='top'] {
  animation-name: slideDownAndFade;
}

.dropdown-content[data-side='right'] {
  animation-name: slideLeftAndFade;
}

.dropdown-content[data-side='bottom'] {
  animation-name: slideUpAndFade;
}

.dropdown-content[data-side='left'] {
  animation-name: slideRightAndFade;
}

.dropdown-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  height: 40px;
  padding: 0 35px 0 10px;
  font-size: var(--font-size-base);
  line-height: 1;
  color: var(--input-color-text);
  border-radius: calc(var(--input-radius) - 5px);
  user-select: none;
  outline: none;
}

.dropdown-item[data-highlighted] {
  background-color: var(--color-surface-muted);
}

.dropdown-item[data-disabled] {
  color: var(--input-color-placeholder);
  pointer-events: none;
}

.dropdown-item-label {
  flex: 1;
  align-content: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  height: 100%;
}

.dropdown-item-indicator {
  position: absolute;
  left: 0;
  width: 30px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
}

.dropdown-item[data-highlighted] .dropdown-item-indicator {
  color: var(--color-surface);
}

.dropdown-item-icon {
  color: var(--color-surface-medium);
  flex-shrink: 0;
}

.dropdown-item[data-highlighted] .dropdown-item-icon {
  color: inherit;
}

.dropdown-label {
  padding: 9px 8px 0px 13px;
  margin-bottom: 4px;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-normal);
  color: var(--input-color-label);
}

.dropdown-separator {
  height: 1px;
  margin: 5px 8px;
  background-color: var(--input-border);
}

@keyframes slideUpAndFade {
  from {
    opacity: 0;
    transform: translateY(2px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideRightAndFade {
  from {
    opacity: 0;
    transform: translateX(-2px);
  }

  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideDownAndFade {
  from {
    opacity: 0;
    transform: translateY(-2px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideLeftAndFade {
  from {
    opacity: 0;
    transform: translateX(2px);
  }

  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>
