<script setup lang="ts">
import { useId } from 'vue'
import {
  Label,
  TimeFieldInput,
  TimeFieldRoot,
  type TimeValue,
} from 'reka-ui'

withDefaults(
  defineProps<{
    label?: string
    granularity?: 'hour' | 'minute' | 'second'
  }>(),
  {
    granularity: 'minute',
  },
)

const id = useId()
const model = defineModel<TimeValue>()
</script>

<template>
  <div class="time-field-wrapper">
    <Label v-if="label" :for="id" class="time-field-label">
      {{ label }}
    </Label>

    <TimeFieldRoot v-model="model" :id="id" v-slot="{ segments }" :granularity="granularity" :hourCycle="24"
      class="time-field">
      <template v-for="item in segments" :key="item.part">
        <TimeFieldInput v-if="item.part === 'literal'" :part="item.part" class="time-field-literal">
          {{ item.value }}
        </TimeFieldInput>

        <TimeFieldInput v-else :part="item.part" class="time-field-segment">
          {{ item.value }}
        </TimeFieldInput>
      </template>
    </TimeFieldRoot>
  </div>
</template>

<style scoped>
.time-field-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.time-field-label {
  padding-left: 8px;
  margin-bottom: 6px;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-normal);
  color: var(--input-color-label);
}

.time-field {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  border-radius: 0.25rem;
  background-color: #fff;
  text-align: center;
  user-select: none;
}

.time-field-literal,
.time-field-segment {
  padding: 0.25rem;
}
</style>
