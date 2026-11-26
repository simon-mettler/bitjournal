<script setup lang="ts">
import CalculationSetting from '@/modules/analytics/components/settings/CalculationSetting.vue'
import type { ValueWidgetConfig } from '@/modules/analytics/types'
import type { Signal } from '@/modules/signals/types'

defineProps<{ signal?: Signal }>()
const config = defineModel<ValueWidgetConfig>({ required: true })
</script>

<template>
  <CalculationSetting v-model="config.calculation" :signal="signal" />
</template>
