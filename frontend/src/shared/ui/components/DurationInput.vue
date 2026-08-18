<script setup lang="ts">
import InputNumber from '@/shared/ui/components/InputNumber.vue'

const hours = defineModel<number>('hours', { default: 0 })
const minutes = defineModel<number>('minutes', { default: 0 })
const seconds = defineModel<number>('seconds', { default: 0 })
</script>

<template>
  <div class="duration-input">
    <InputNumber v-model="hours" label="Hours" :min="0" :max="24" />
    <InputNumber v-model="minutes" label="Minutes" :min="0" :max="59" />
    <InputNumber v-model="seconds" label="Seconds" :min="0" :max="59" />
  </div>
</template>

<style scoped>
.duration-input {
  display: flex;
  gap: 12px;
}
</style>
