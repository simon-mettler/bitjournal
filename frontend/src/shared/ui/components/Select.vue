<script setup lang="ts">
import { Label } from 'reka-ui'
import { useId } from 'vue'
import {
  SelectContent,
  SelectIcon,
  SelectItem,
  SelectItemIndicator,
  SelectItemText,
  SelectPortal,
  SelectRoot,
  SelectScrollDownButton,
  SelectScrollUpButton,
  SelectTrigger,
  SelectValue,
  SelectViewport,
} from 'reka-ui'

import {
  ChevronDown,
  ChevronsDown,
  ChevronsUp,
  Check,
} from '@lucide/vue'
export interface SelectOption {
  value: string
  label: string
  disabled?: boolean
}

const props = defineProps<{
  options: SelectOption[]
  placeholder?: string
  disabled?: boolean
  label?: string
  error?: string
  variant?: 'default' | 'float'
}>()

const model = defineModel<string>()
const id = useId()
</script>

<template>
  <div class="field">
    <Label v-if="props.label" class="label" :for="id">
      {{ props.label }}
    </Label>

    <SelectRoot v-model="model" :disabled="props.disabled">
      <SelectTrigger :id="id" class="select-trigger" :class="props.variant">
        <SelectValue class="select-value" :placeholder="props.placeholder ?? 'Select...'" />
        <SelectIcon class="select-icon">
          <ChevronDown />
        </SelectIcon>
      </SelectTrigger>

      <SelectPortal>
        <SelectContent class="select-content" :class="props.variant" position="popper">
          <SelectScrollUpButton class="select-scroll-button">
            <ChevronsUp />
          </SelectScrollUpButton>

          <SelectViewport class="select-viewport">
            <SelectItem v-for="option in props.options" :key="option.value" class="select-item" :value="option.value"
              :disabled="option.disabled">
              <SelectItemText>{{ option.label }}</SelectItemText>
              <SelectItemIndicator class="select-item-indicator">
                <Check />
              </SelectItemIndicator>
            </SelectItem>
          </SelectViewport>

          <SelectScrollDownButton class="select-scroll-button">
            <ChevronsDown />
          </SelectScrollDownButton>
        </SelectContent>
      </SelectPortal>
    </SelectRoot>

    <p v-if="props.error" class="error-text">{{ props.error }}</p>
  </div>
</template>

<style>
.select-content {
  width: var(--reka-select-trigger-width);
  padding: 5px;
  max-height: var(--reka-select-content-available-height);
  border-radius: var(--input-radius);
  border: var(--input-border);
  box-shadow: var(--shadow-card);
  color: var(--input-color-text);
  background-color: var(--color-surface);
}

.select-content.float {
  margin-top: 4px;
  border: none;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-interact);
}

.select-content.float .select-item {
  border-radius: calc(var(--radius-lg) - 5px);
}
</style>

<style scoped>
button {
  all: unset;
}

.field {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.label {
  font-size: var(--font-size-sm);
  padding-left: 8px;
  margin-bottom: 6px;
  font-weight: var(--font-weight-normal);
  color: var(--input-color-label);
}

.select-trigger {
  box-shadow: var(--shadow-fields);
  display: inline-flex;
  box-sizing: border-box;
  align-items: center;
  justify-content: space-between;
  padding: 0 10px;
  font-size: var(--font-size-base);
  line-height: 1;
  height: var(--input-height);
  background-color: var(--input-color-background);
  color: var(--input-color-text);
  border: var(--input-border);
  border-radius: var(--input-radius);

  &:focus {
    box-shadow: var(--input-shadow-focus);
    border: var(--input-border-focus);
  }
}

.select-trigger.float {
  border: 2px solid transparent;
  border-radius: var(--radius-xl);
  background-color: var(--color-surface);
  box-shadow: var(--shadow-interact);
  gap: 6px;
  padding: 0 14px;

  &:focus {
    box-shadow: var(--input-shadow-focus);
    border: var(--input-border-focus);
  }
}

.select-trigger.float[data-state="open"] {
  border: 2px solid transparent;
}

.select-trigger[data-disabled] {
  color: var(--input-color-text-disabled);
  background-color: var(--input-color-background-disabled);
  border: var(--input-border-disabled);
  box-shadow: none;
  cursor: not-allowed;

  .select-icon {
    color: var(--input-color-text-disabled);
  }
}

.select-trigger[data-placeholder] {
  color: var(--input-color-placeholder);
}

.select-trigger[data-state="open"] {
  border: var(--input-border-focus);
}

.select-icon {
  color: var(--color-surface-medium);
  height: 24px;
}

.select-item {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  height: 40px;
  padding: 0 35px 0 10px;
  font-size: var(--font-size-base);
  line-height: 1;
  border-radius: calc(var(--input-radius) - 5px);
  font-size: var(--font-size-base);
  color: var(--input-color-text);
  user-select: none;

  &:hover {
    background-color: var(--color-surface-muted);
  }
}

.select-item[data-disabled] {
  color: red;
}

.select-label {
  padding-left: 8px;
  margin-bottom: 6px;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-normal);
  min-height: var(--font-size-sm);
  color: var(--input-color-label);
}

.select-item-indicator {
  width: 24px;
  height: 24px;
  color: var(--color-primary);
}

.select-scroll-button {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 25px;
  color: black;
  cursor: default;
}

.error-text {
  font-size: var(--font-size-sm);
  color: var(--color-danger);
  margin: 0;
  padding-left: 8px;
}
</style>
