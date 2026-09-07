<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { GripVertical, Trash2 } from '@lucide/vue'
import { useSortable } from '@vueuse/integrations/useSortable'
import type { UseSortableOptions } from '@vueuse/integrations/useSortable'
import AppShellHeader from '@/shared/ui/layout/AppShellHeader.vue'
import AppShellFooter from '@/shared/ui/layout/AppShellFooter.vue'
import Button from '@/shared/ui/components/Button.vue'
import IconButton from '@/shared/ui/components/IconButton.vue'
import InputText from '@/shared/ui/components/InputText.vue'
import AlertDialog from '@/shared/ui/components/AlertDialog.vue'
import Header from '@/shared/ui/components/Header.vue'
import SignalCard from '@/shared/ui/components/SignalCard.vue'
import SignalPickerDialog from '@/modules/boards/components/SignalPickerDialog.vue'
import Footer from '@/shared/ui/components/Footer.vue'
import { deleteBoard, getBoard, updateBoard } from '@/modules/boards/api'
import type { Signal } from '@/modules/signals/types'
import { useToast } from '@/shared/lib/useToast'
import { useFormValidation } from '@/shared/lib/useFormValidation'
import { required, maxLength } from '@/shared/lib/validators'

const route = useRoute()
const router = useRouter()
const toaster = useToast()

const boardId = route.params.id as string

const name = ref('')
const signals = ref<Signal[]>([])
const gridEl = ref<HTMLElement | null>(null)
const saving = ref(false)
const loading = ref(true)

const { errors: validationErrors, validateField, validateAll } = useFormValidation(
  { name: () => name.value },
  { name: [required('Name is required'), maxLength(100, '100 characters or fewer')] },
)

useSortable(gridEl, signals, {
  handle: '.drag-handle',
  animation: 300,
} as UseSortableOptions)

async function load() {
  loading.value = true
  try {
    const { data } = await getBoard(boardId)
    name.value = data.name
    signals.value = data.board_signals.map(bs => bs.signal)
  } finally {
    loading.value = false
  }
}

function onSignalsAdded(added: Signal[]) {
  signals.value.push(...added)
}

function removeSignal(id: string) {
  signals.value = signals.value.filter(s => s.id !== id)
}

async function save() {
  if (!validateAll()) return
  saving.value = true
  try {
    await updateBoard(boardId, {
      name: name.value.trim(),
      signal_ids: signals.value.map(s => s.id),
    })
    toaster.toast({ description: 'Board saved.', variant: 'success' })
    router.push({ name: 'manage-boards' })
  } catch {
    toaster.toast({ description: 'Could not save board.', variant: 'danger' })
  } finally {
    saving.value = false
  }
}

async function confirmDeleteBoard() {
  try {
    await deleteBoard(boardId)
    router.push({ name: 'manage-boards' })
  } catch {
    toaster.toast({ description: 'Could not delete board.', variant: 'danger' })
  }
}

onMounted(load)
</script>

<template>

  <AppShellHeader>
    <Header heading="Edit board">
    </Header>
  </AppShellHeader>

  <div class="edit-board-content">
    <div v-if="!loading" class="card">
      <InputText v-model="name" label="Board name" placeholder="" @blur="validateField('name')"
        :error="validationErrors['name']" />

      <div class="board-actions">
        <AlertDialog title="Delete board" confirm-text="Delete"
          :description="`Are you sure you want to delete &quot;${name}&quot;? This can't be undone.`"
          @confirm="confirmDeleteBoard">
          <template #trigger>
            <Button variant="secondary" class="danger-btn">Delete board</Button>
          </template>
          <template #cancel>
            <Button variant="secondary">Cancel</Button>
          </template>
          <template #action>
            <Button variant="primary">Delete</Button>
          </template>
        </AlertDialog>

        <SignalPickerDialog :exclude-ids="signals.map(s => s.id)" @add="onSignalsAdded">
          <template #trigger>
            <Button variant="tertiary">Add signal</Button>
          </template>
        </SignalPickerDialog>
      </div>
    </div>

    <div ref="gridEl" class="signal-grid">
      <SignalCard class="drag-handle" v-for="signal in signals" :key="signal.id" :signal="signal">
        <template #handle>
          <span>
            <GripVertical :size="20" />
          </span>
        </template>
        <template #actions>
          <IconButton class="danger" variant="tertiary" size="sm" @click="removeSignal(signal.id)"
            :aria-label="`Remove ${signal.name} from board`">
            <Trash2 />
          </IconButton>
        </template>
      </SignalCard>
    </div>

  </div>

  <AppShellFooter>
    <Footer>
      <Button variant="secondary" @click="router.back()">
        Cancel
      </Button>
      <Button variant="primary" :disabled="saving || loading" @click="save">
        {{ saving ? 'Saving...' : 'Save' }}
      </Button>
    </Footer>
  </AppShellFooter>

</template>

<style scoped>
.edit-board-content {
  padding: 0 var(--padding-app);
}

.card {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  border-radius: var(--input-radius);
  background-color: var(--input-color-background);
  margin-bottom: 16px;
}

.board-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.board-actions button {
  flex: 1;
}

.signal-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.drag-handle {
  display: inline-flex;
  color: var(--input-color-label);
  cursor: grab;
  touch-action: none;
}

.drag-handle:active {
  cursor: grabbing;
}

.danger>svg {
  color: var(--color-danger);
}
</style>
