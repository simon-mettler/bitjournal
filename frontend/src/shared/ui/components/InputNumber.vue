<script setup lang="ts">
import {
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
  NumberFieldRoot,
} from 'reka-ui'
import { Plus, Minus } from '@lucide/vue';
import { useId } from 'vue'

withDefaults(
  defineProps<{
    label: string
    placeholder?: string
    error?: string
    min?: number
    max?: number
    step?: number
    disabled?: boolean
  }>(),
  {
    step: 1,
  },
)

const model = defineModel<number>()
const id = useId()
</script>

<template>
  <div class="field">
    <label class="label" :for="id">
      {{ label }}
    </label>
    <NumberFieldRoot :id="id" v-model="model" class="number-root" :min="min" :max="max" :step="step"
      :disabled="disabled">
      <NumberFieldDecrement class="number-btn">
        <Minus />
      </NumberFieldDecrement>
      <NumberFieldInput class="number-input" :placeholder="placeholder" />
      <NumberFieldIncrement class="number-btn">
        <Plus />
      </NumberFieldIncrement>
    </NumberFieldRoot>
    <p v-if="error" class="error-text">{{ error }}</p>
  </div>
</template>

<style scoped>
.field {
  display: flex;
  flex-direction: column;
}

.label {
  padding-left: 8px;
  margin-bottom: 6px;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-normal);
  color: var(--input-color-label);
}

.number-root {
  display: flex;
  align-items: center;
  border-radius: var(--input-radius);
  height: var(--input-height);
  color: var(--input-color-text);
  background-color: var(--input-color-background);
  border: var(--input-border);

  &:focus {
    box-shadow: var(--input-shadow-focus);
    border: var(--input-border-focus);
  }
}

.number-input {
  all: unset;
  flex: 1;
  text-align: center;
  font-size: var(--font-size-base);
  border-radius: var(--input-radius);
  height: 100%;
}

.number-btn {
  all: unset;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 10px;
  height: 100%;
  color: var(--color-surface-medium);
}

.error-text {
  font-size: var(--font-size-sm);
  color: var(--color-danger);
  margin: 0;
  padding-left: 8px;
}
</style>
