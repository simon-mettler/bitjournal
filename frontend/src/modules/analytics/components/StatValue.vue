<script setup lang="ts">
import type { StatPart } from '@/modules/analytics/format'

defineProps<{ parts: StatPart[] }>()
</script>

<template>
  <span class="stat-value">
    <span v-for="(part, i) in parts" :key="i" :class="{ 'stat-value-unit': part.unit }">{{
      part.text
    }}</span>
  </span>
</template>

<style scoped>
.stat-value-unit {
  font-size: 0.6em;
  font-weight: var(--font-weight-normal);
}
</style>
