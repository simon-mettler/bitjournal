<script setup lang="ts">
import { Label } from 'reka-ui'
import { useId } from 'vue'

defineProps<{
  label?: string
  placeholder?: string
  type?: string
  error?: string
}>()

const model = defineModel<string>()
const id = useId()
</script>


<template>
  <div class="field">
    <Label class="label" :for="id">
      {{ label }}
    </Label>
    <input :id="id" class="input" :type="type" :placeholder="placeholder" v-model="model">
    <p v-if="error" class="error-text">{{ error }}</p>
  </div>
</template>


<style scoped>
input {
  all: unset;
}

.field {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.label {
  padding-left: 8px;
  margin-bottom: 6px;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-normal);
  color: var(--input-color-label);
}

.input {
  display: inline-flex;
  align-items: center;
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

.error-text {
  font-size: var(--font-size-sm);
  color: var(--color-danger);
  margin: 0;
  padding-left: 8px;
}
</style>
