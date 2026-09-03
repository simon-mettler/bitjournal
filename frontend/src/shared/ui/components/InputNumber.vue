<script setup lang="ts">
import {
  NumberFieldInput,
  NumberFieldRoot,
} from 'reka-ui'
import { Diff } from '@lucide/vue';
import { computed, onMounted, onUnmounted, useId } from 'vue'
import { useNumpadGroup } from '@/shared/lib/useNumpadGroup'

const props = withDefaults(
  defineProps<{
    label: string
    placeholder?: string
    error?: string
    min?: number
    max?: number
    step?: number
    disabled?: boolean
    signToggle?: boolean
    maxLength?: number // digit cap when driven by the numpad, e.g. 2 for "59"
  }>(),
  {
    step: 1,
    signToggle: false,
  },
)

const model = defineModel<number>()
const id = useId()

const group = useNumpadGroup()
const numpadActive = computed(() => !!group?.enabled)
const isActiveField = computed(() => numpadActive.value && group?.activeId.value === id)

onMounted(() => {
  group?.register({
    id,
    value: model,
    min: props.min,
    max: props.max,
    maxLength: props.maxLength,
    label: props.label,
  })
})
onUnmounted(() => group?.unregister(id))

function focusField() {
  if (numpadActive.value) group?.focus(id)
}

// stop the native focus/keyboard from firing at all when the numpad drives input
function blockNative(e: Event) {
  if (numpadActive.value) e.preventDefault()
}

function toggleSign() {
  if (model.value) {
    model.value = model.value === null ? model.value : -model.value
  }
}
</script>

<template>
  <div class="field">
    <label class="label" :for="id">
      {{ label }}
    </label>
    <NumberFieldRoot :id="id" v-model="model" class="number-root" :class="{ 'number-root-active': isActiveField }"
      :min="min" :max="max" :step="step" :disabled="disabled" @click="focusField"
      :format-options="{ useGrouping: false, maximumFractionDigits: 2 }">
      <button v-if="signToggle && !numpadActive" class="number-sign-toggle" type="button" tabindex="-1" aria-label="Toggle positive or
        negative" @click="toggleSign">
        <Diff :size="20" />
      </button>
      <NumberFieldInput class="number-input" :placeholder="placeholder" :readonly="numpadActive"
        :inputmode="numpadActive ? 'none' : 'decimal'" :tabindex="numpadActive ? -1 : undefined"
        @mousedown="blockNative" @focus="focusField" />
    </NumberFieldRoot>
    <p v-if="error" class="error-text">{{ error }}</p>
  </div>
</template>

<style scoped>
.field {
  display: flex;
  flex-direction: column;
  flex: 1 1 0;
  min-width: 0;
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
  width: 100%;
  box-sizing: border-box;
  min-height: var(--input-height);
  border-radius: var(--input-radius);
  color: var(--input-color-text);
  background-color: var(--input-color-background);
  border: var(--input-border);

  &:focus {
    box-shadow: var(--input-shadow-focus);
    border: var(--input-border-focus);
  }
}

.number-root-active {
  border: var(--input-border-focus);
  box-shadow: var(--input-shadow-focus);
}

.number-input {
  all: unset;
  flex: 1;
  min-width: 0;
  width: 100%;
  text-align: center;
  font-size: var(--font-size-base);
  border-radius: var(--input-radius);
  height: calc(var(--input-height) - 2px);
  box-sizing: border-box;
}

.number-sign-toggle {
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
