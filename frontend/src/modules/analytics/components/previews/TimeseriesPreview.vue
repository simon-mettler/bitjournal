<script setup lang="ts">
const BAR_HEIGHTS = [26, 40, 32, 52, 22, 46, 58]
const BASELINE = 66
</script>

<template>
  <svg viewBox="0 0 120 72" aria-hidden="true">
    <rect
      v-for="(height, index) in BAR_HEIGHTS"
      :key="index"
      class="bar"
      :x="12 + index * 14"
      :y="BASELINE - height"
      width="10"
      :height="height"
      rx="3"
    />
    <line class="axis" x1="8" :y1="BASELINE" x2="112" :y2="BASELINE" />
  </svg>
</template>

<style scoped>
.bar {
  fill: var(--color-primary);
}

.axis {
  stroke: var(--color-surface-medium);
  stroke-opacity: 0.35;
}
</style>
