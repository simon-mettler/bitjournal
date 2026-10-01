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
import { defaultWidgetFormState, formStateToPayload } from '@/modules/analytics/widgetFormState'
import { useToast } from '@/shared/lib/useToast'

const route = useRoute()
const router = useRouter()
const toaster = useToast()

const boardId = route.params.boardId as string

const form = ref(defaultWidgetFormState())
const submitting = ref(false)
const widgetFormRef = ref<InstanceType<typeof WidgetForm>>()

async function submit() {
  if (!widgetFormRef.value?.validateAll() || !form.value.signalId) return

  submitting.value = true
  try {
    await createAnalyticsWidget({
      board_id: boardId,
      ...formStateToPayload(form.value, form.value.signalId),
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
    <WidgetForm ref="widgetFormRef" v-model="form" />
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
