<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Button from '@/shared/ui/components/Button.vue'
import Header from '@/shared/ui/components/Header.vue'
import Footer from '@/shared/ui/components/Footer.vue'
import AppShellHeader from '@/shared/ui/layout/AppShellHeader.vue'
import AppShellFooter from '@/shared/ui/layout/AppShellFooter.vue'
import WidgetForm from '@/modules/analytics/components/WidgetForm.vue'
import { getAnalyticsWidget, updateAnalyticsWidget } from '@/modules/analytics/api'
import {
  defaultWidgetFormState,
  formStateToPayload,
  widgetToFormState,
} from '@/modules/analytics/widgetFormState'
import { useToast } from '@/shared/lib/useToast'

const route = useRoute()
const router = useRouter()
const toaster = useToast()

const widgetId = route.params.id as string

const loaded = ref(false)
const saving = ref(false)
const form = ref(defaultWidgetFormState())
const widgetFormRef = ref<InstanceType<typeof WidgetForm>>()

async function load() {
  try {
    const { data } = await getAnalyticsWidget(widgetId)
    form.value = widgetToFormState(data)
    loaded.value = true
  } catch {
    toaster.toast({ description: 'Failed to load widget.', variant: 'danger' })
  }
}

async function save() {
  if (!widgetFormRef.value?.validateAll() || !form.value.signalId) return

  saving.value = true
  try {
    await updateAnalyticsWidget(widgetId, formStateToPayload(form.value, form.value.signalId))
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
    <WidgetForm v-if="loaded" ref="widgetFormRef" v-model="form" />
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
