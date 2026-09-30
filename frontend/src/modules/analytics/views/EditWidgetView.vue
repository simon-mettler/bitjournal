<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Button from '@/shared/ui/components/Button.vue'
import Header from '@/shared/ui/components/Header.vue'
import Footer from '@/shared/ui/components/Footer.vue'
import AppShellHeader from '@/shared/ui/layout/AppShellHeader.vue'
import AppShellFooter from '@/shared/ui/layout/AppShellFooter.vue'
import WidgetForm from '@/modules/analytics/components/WidgetForm.vue'
import {
  getAnalyticsWidget,
  updateAnalyticsWidget,
} from '@/modules/analytics/api'
import type { WidgetAggregation, WidgetTimeframe } from '@/modules/analytics/types'
import { useToast } from '@/shared/lib/useToast'

const route = useRoute()
const router = useRouter()
const toaster = useToast()

const widgetId = route.params.id as string

const loaded = ref(false)
const saving = ref(false)
const title = ref('')
const signalId = ref<string>()
const aggregation = ref<WidgetAggregation>('total')
const timeframe = ref<WidgetTimeframe>('this_week')
const periodStart = ref<string>()
const days = ref<number>()
const widgetFormRef = ref<InstanceType<typeof WidgetForm>>()

async function load() {
  try {
    const { data } = await getAnalyticsWidget(widgetId)
    title.value = data.title
    signalId.value = data.signal.id
    aggregation.value = data.aggregation
    timeframe.value = data.timeframe
    periodStart.value = data.period_start ?? undefined
    days.value = data.days ?? 7
    loaded.value = true
  } catch {
    toaster.toast({ description: 'Failed to load widget.', variant: 'danger' })
  }
}

async function save() {
  if (!widgetFormRef.value?.validateAll() || !signalId.value) return

  saving.value = true
  try {
    await updateAnalyticsWidget(widgetId, {
      type: 'value',
      title: title.value.trim(),
      signal_id: signalId.value,
      aggregation: aggregation.value,
      timeframe: timeframe.value,
      period_start: periodStart.value ?? null,
      days: days.value ?? null,
    })
    toaster.toast({ description: 'Widget saved.', variant: 'success' })
    router.back()
  } catch {
    toaster.toast({ description: 'Could not save widget.', variant: 'danger' })
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <AppShellHeader>
    <Header heading="Edit widget" />
  </AppShellHeader>

  <div class="edit-widget-content">
    <WidgetForm v-if="loaded" ref="widgetFormRef" v-model:title="title" v-model:signal-id="signalId"
      v-model:aggregation="aggregation" v-model:timeframe="timeframe" v-model:period-start="periodStart"
      v-model:days="days" />
  </div>

  <AppShellFooter>
    <Footer>
      <Button variant="secondary" @click="router.back()">Cancel</Button>
      <Button variant="primary" :disabled="saving || !loaded" @click="save">
        {{ saving ? 'Saving...' : 'Save' }}
      </Button>
    </Footer>
  </AppShellFooter>
</template>

<style scoped>
.edit-widget-content {
  padding: 0 var(--padding-app);
}
</style>
