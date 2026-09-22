<script setup lang="ts">
import { ref, type Ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { ArrowLeft, ChevronLeft, ChevronRight } from '@lucide/vue'
import { today, getLocalTimeZone, type CalendarDate } from '@internationalized/date'
import AppShellHeader from '@/shared/ui/layout/AppShellHeader.vue'
import Header from '@/shared/ui/components/Header.vue'
import IconButton from '@/shared/ui/components/IconButton.vue'
import Toggle from '@/shared/ui/components/Toggle.vue'
import Select from '@/shared/ui/components/Select.vue'
import TimeseriesChart from '@/modules/analytics/components/TimeseriesChart.vue'
import DayOfWeekChart from '@/modules/analytics/components/DayOfWeekChart.vue'
import HeatmapChart from '@/modules/analytics/components/HeatmapChart.vue'
import HeatmapLegend from '@/modules/analytics/components/HeatmapLegend.vue'
import { getSignal } from '@/modules/signals/api'
import { getSignalStats } from '@/modules/analytics/api'
import { formatStatValue, formatPeriodRange, shiftPeriod } from '@/modules/analytics/format'
import { useToast } from '@/shared/lib/useToast'
import { useSignalStatsUiStore } from '@/modules/analytics/store/signalStatsUiStore'
import type { Signal } from '@/modules/signals/types'
import type { SignalStats } from '@/modules/analytics/types'

const route = useRoute()
const router = useRouter()
const toaster = useToast()

const chartTypeOptions = [
  { value: 'bar' as const, label: 'Bar' },
  { value: 'line' as const, label: 'Line' },
]

const timeframeOptions = [
  { value: 'week', label: 'Week' },
  { value: 'month', label: 'Month' },
  { value: 'quarter', label: 'Quarter' },
  { value: 'year', label: 'Year' },
]

const signalStatsUiStore = useSignalStatsUiStore()
const { timeframe, chartType } = storeToRefs(signalStatsUiStore)
const anchorDate = ref<CalendarDate>(today(getLocalTimeZone())) as Ref<CalendarDate>

const signalId = route.params.id as string
const signal = ref<Signal | null>(null)
const stats = ref<SignalStats | null>(null)

const isNextDisabled = computed(() => {
  if (!stats.value) return true
  return today(getLocalTimeZone()).toString() < stats.value.period.end
})

async function loadSignal() {
  try {
    const { data } = await getSignal(signalId)
    signal.value = data
  } catch (err) {
    console.error(err)
    toaster.toast({ description: 'Failed to load signal', variant: 'danger' })
  }
}

async function loadStats() {
  try {
    const { data } = await getSignalStats(signalId, {
      timeframe: timeframe.value,
      periodStart: anchorDate.value.toString(),
    })
    stats.value = data
  } catch (err) {
    console.error(err)
    toaster.toast({ description: 'Failed to load signal stats', variant: 'danger' })
  }
}

function goToPreviousPeriod() {
  anchorDate.value = shiftPeriod(anchorDate.value, timeframe.value, -1)
}

function goToNextPeriod() {
  if (isNextDisabled.value) return
  anchorDate.value = shiftPeriod(anchorDate.value, timeframe.value, 1)
}

watch([timeframe, anchorDate], loadStats)

onMounted(() => {
  loadSignal()
  loadStats()
})
</script>

<template>
  <AppShellHeader>
    <Header :heading="signal?.name ?? 'Signal stats'">
      <template #actions>
        <div class="back-button-wrap">
          <IconButton variant="float" aria-label="Back" @click="router.back()">
            <ArrowLeft />
          </IconButton>
        </div>
      </template>
    </Header>
  </AppShellHeader>

  <div class="signal-stats-content">
    <div class="period-controls">
      <Select v-model="timeframe" :options="timeframeOptions" class="timeframe-select" />
      <div class="period-nav">
        <IconButton variant="tertiary" size="sm" aria-label="Previous period" @click="goToPreviousPeriod">
          <ChevronLeft />
        </IconButton>
        <span class="period-range">{{ stats ? formatPeriodRange(stats.period) : '' }}</span>
        <IconButton variant="tertiary" size="sm" aria-label="Next period" :disabled="isNextDisabled"
          @click="goToNextPeriod">
          <ChevronRight />
        </IconButton>
      </div>
    </div>

    <p v-if="!signal || !stats">Loading...</p>
    <div v-else class="stat-tiles">
      <div class="stat-tile">
        <span class="stat-tile-label">Total</span>
        <span class="stat-tile-value">{{ formatStatValue(signal, stats.total) }}</span>
      </div>
      <div class="stat-tile">
        <span class="stat-tile-label">Average</span>
        <span class="stat-tile-value">{{ formatStatValue(signal, stats.average) }}</span>
      </div>
    </div>

    <div v-if="signal && stats" class="chart-section">
      <div class="chart-section-header">
        <span class="chart-section-title">Over time</span>
        <div class="chart-type-toggle">
          <Toggle v-for="option in chartTypeOptions" :key="option.value" :model-value="chartType === option.value"
            @update:model-value="pressed => pressed && (chartType = option.value)">
            {{ option.label }}
          </Toggle>
        </div>
      </div>
      <TimeseriesChart :signal="signal" :timeseries="stats.timeseries" :chart-type="chartType" />
    </div>

    <div v-if="signal && stats" class="chart-section">
      <div class="chart-section-header">
        <span class="chart-section-title">By day of week</span>
      </div>
      <DayOfWeekChart :signal="signal" :day-of-week="stats.day_of_week" />
    </div>

    <div v-if="signal && stats" class="chart-section">
      <div class="chart-section-header">
        <span class="chart-section-title">By day &amp; hour</span>
        <HeatmapLegend />
      </div>
      <HeatmapChart :signal="signal" :heatmap="stats.heatmap" />
    </div>
  </div>
</template>

<style scoped>
.signal-stats-content {
  padding: 0 var(--padding-app) var(--spacing-lg);
  min-height: 100%;
  background-color: var(--color-app-bg);
  box-sizing: border-box;
}

.back-button-wrap {
  display: inline-flex;
}

.period-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 8px 0 32px 0;
}

.timeframe-select {
  width: auto;
  flex-shrink: 0;
}

.timeframe-select :deep(.select-trigger) {
  border: none;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-interact);
}

.period-nav {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 6px;
  border-radius: var(--radius-xl);
  background-color: var(--color-surface);
  box-shadow: var(--shadow-interact);
}

.period-range {
  min-width: 132px;
  text-align: center;
  font-size: var(--font-size-sm);
  color: var(--input-color-label);
}

.stat-tiles {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 16px;
}

.stat-tile {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  border-radius: var(--radius-md);
  background-color: var(--input-color-background);
  box-shadow: var(--shadow-card);
}

.stat-tile-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--input-color-label);
}

.stat-tile-value {
  font-size: var(--font-size-h1);
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
}

.chart-section {
  margin-top: 24px;
  padding: 16px;
  border-radius: var(--radius-md);
  background-color: var(--input-color-background);
  box-shadow: var(--shadow-card);
}

.chart-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.chart-section-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
}

.chart-type-toggle {
  display: flex;
  background-color: var(--color-surface-muted);
  border-radius: var(--radius-xl);
  padding: 2px;
}

.chart-type-toggle :deep(.toggle[data-state='on']) {
  background-color: var(--color-text);
  color: var(--color-surface);
  box-shadow: none;
}
</style>
