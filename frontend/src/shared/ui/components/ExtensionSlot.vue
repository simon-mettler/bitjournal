<script setup lang="ts">
import { slotComponents, type ExtensionSlotName } from '@/shared/lib/extensions'

defineProps<{ name: ExtensionSlotName }>()
</script>

<template>
  <component :is="component" v-for="(component, index) in slotComponents(name)" :key="index" />
</template>
