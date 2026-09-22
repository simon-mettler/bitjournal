<script setup lang="ts">
import { HEATMAP_COLORS } from '@/modules/analytics/heatmapScale'
</script>

<template>
  <div class="heatmap-legend">
    <span>Less</span>
    <span v-for="color in HEATMAP_COLORS" :key="color" class="heatmap-legend-swatch"
      :style="{ backgroundColor: color }" />
    <span>More</span>
  </div>
</template>

<style scoped>
.heatmap-legend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--font-size-sm);
  color: var(--input-color-label);
}

.heatmap-legend-swatch {
  width: 14px;
  height: 14px;
  border-radius: 5px;
}

.heatmap-legend span:first-child {
  margin-right: 2px;
}

.heatmap-legend span:last-child {
  margin-left: 2px;
}
</style>
