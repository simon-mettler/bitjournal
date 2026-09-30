<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Button from '@/shared/ui/components/Button.vue'
import Header from '@/shared/ui/components/Header.vue'
import Footer from '@/shared/ui/components/Footer.vue'
import AppShellHeader from '@/shared/ui/layout/AppShellHeader.vue'
import AppShellFooter from '@/shared/ui/layout/AppShellFooter.vue'
import WidgetForm from '@/modules/analytics/components/WidgetForm.vue'
import { createAnalyticsWidget } from '@/modules/analytics/api'
import type { WidgetAggregation, WidgetTimeframe } from '@/modules/analytics/types'
import { useToast } from '@/shared/lib/useToast'

const route = useRoute()
const router = useRouter()
const toaster = useToast()

const boardId = route.params.boardId as string

const title = ref('')
const signalId = ref<string>()
const aggregation = ref<WidgetAggregation>('total')
const timeframe = ref<WidgetTimeframe>('this_week')
const periodStart = ref<string>()
const days = ref<number>(7)
const submitting = ref(false)
const widgetFormRef = ref<InstanceType<typeof WidgetForm>>()

async function submit() {
  if (!widgetFormRef.value?.validateAll() || !signalId.value) return

  submitting.value = true
  try {
    await createAnalyticsWidget({
      board_id: boardId,
      type: 'value',
      title: title.value.trim(),
      signal_id: signalId.value,
      aggregation: aggregation.value,
      timeframe: timeframe.value,
      period_start: periodStart.value ?? null,
      days: days.value ?? null,
    })
    toaster.toast({ description: 'Widget created.', variant: 'success' })
    router.back()
  } catch {
    toaster.toast({ description: 'Could not create widget.', variant: 'danger' })
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <AppShellHeader>
    <Header heading="Create widget"></Header>
  </AppShellHeader>

  <div class="add-widget-content">
    <WidgetForm ref="widgetFormRef" v-model:title="title" v-model:signal-id="signalId"
      v-model:aggregation="aggregation" v-model:timeframe="timeframe" v-model:period-start="periodStart"
      v-model:days="days" />
  </div>

  <AppShellFooter>
    <Footer>
      <Button variant="secondary" @click="router.back()">Cancel</Button>
      <Button :disabled="submitting" variant="primary" @click="submit">
        {{ submitting ? 'Saving...' : 'Create widget' }}
      </Button>
    </Footer>
  </AppShellFooter>
</template>

<style scoped>
.add-widget-content {
  padding: 0 var(--padding-app);
}
</style>
