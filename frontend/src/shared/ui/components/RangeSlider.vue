<script setup lang="ts">
import { computed } from 'vue'
import { SliderRange, SliderRoot, SliderThumb, SliderTrack } from 'reka-ui'

const props = defineProps<{
  min: number
  max: number
  minLabel?: string
  maxLabel?: string
}>()

const model = defineModel<number>({ required: true })

// reka ui always works with an array of thumb position, even for singel thumb slider
const sliderValue = computed<number[]>({
  get: () => [model.value],
  set: (v) => {
    if (v.length) model.value = v[0]
  },
})
</script>

<template>
  <div class="range-slider">
    <div class="range-slider-value">{{ model }}</div>

    <SliderRoot v-model="sliderValue" @pointerdown.stop @touchstart.stop class="range-slider-root" :min="min" :max="max"
      :step="1">
      <SliderTrack class="range-slider-track">
        <SliderRange class="range-slider-range" />
      </SliderTrack>
      <SliderThumb class="range-slider-thumb" />
    </SliderRoot>

    <div v-if="minLabel || maxLabel" class="range-slider-labels">
      <span>{{ minLabel }}</span>
      <span>{{ maxLabel }}</span>
    </div>
  </div>
</template>

<style scoped>
.range-slider {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
  width: 100%;
}

.range-slider-value {
  font-size: 2rem;
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
}

.range-slider-root {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
  height: 20px;
  touch-action: none;
  user-select: none;
}

.range-slider-track {
  position: relative;
  flex: 1;
  height: 6px;
  border-radius: 999px;
  background-color: var(--input-color-border);
}

.range-slider-range {
  position: absolute;
  height: 100%;
  border-radius: 999px;
  background-color: var(--color-primary);
}

.range-slider-thumb {
  display: block;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background-color: var(--color-primary);
  box-shadow: 0 0 0 4px oklab(from var(--color-primary) l a b / 0.2);
  cursor: pointer;
}

.range-slider-labels {
  display: flex;
  justify-content: space-between;
  width: 100%;
  font-size: var(--font-size-sm);
  color: var(--input-color-label);
}
</style>
