<script setup lang="ts">
import InputNumber from '@/shared/ui/components/InputNumber.vue'
import NumberPad from '@/shared/ui/components/NumberPad.vue'
import { provideNumpadGroup } from '@/shared/lib/useNumpadGroup'

const props = withDefaults(defineProps<{ numpad?: boolean }>(), { numpad: false })

const hours = defineModel<number>('hours', { default: 0 })
const minutes = defineModel<number>('minutes', { default: 0 })
const seconds = defineModel<number>('seconds', { default: 0 })

provideNumpadGroup(props.numpad)
</script>

<template>
  <div class="duration-input">
    <InputNumber v-model="hours" label="Hours" :min="0" :max="24" :max-length="2" />
    <InputNumber v-model="minutes" label="Minutes" :min="0" :max="59" :max-length="2" />
    <InputNumber v-model="seconds" label="Seconds" :min="0" :max="59" :max-length="2" />
  </div>

  <NumberPad enable-next v-if="numpad" />

</template>

<style scoped>
.duration-input {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
}
</style>
