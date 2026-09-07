<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Modal from '@/shared/ui/components/Dialog.vue'
import Button from '@/shared/ui/components/Button.vue'
import InputText from '@/shared/ui/components/InputText.vue'
import { DialogClose } from 'reka-ui'
import { createBoard } from '@/modules/boards/api'
import type { Board } from '@/modules/boards/types'
import { useToast } from '@/shared/lib/useToast'
import { useFormValidation } from '@/shared/lib/useFormValidation'
import { required, maxLength } from '@/shared/lib/validators'

const emit = defineEmits<{ created: [board: Board] }>()
const router = useRouter()
const toaster = useToast()

const open = ref(false)
const name = ref('')
const submitting = ref(false)
const error = ref<string>()

const { errors: validationErrors, validateField, validateAll } = useFormValidation(
  { name: () => name.value },
  { name: [required('Name is required'), maxLength(100, '100 characters or fewer')] },
)

async function submit() {
  if (!validateAll()) return
  submitting.value = true
  error.value = undefined
  try {
    const { data } = await createBoard({ name: name.value.trim() })
    emit('created', data)
    open.value = false
    name.value = ''
    router.push({ name: 'board-edit', params: { id: data.id } })
  } catch (err) {
    error.value = 'Could not create board. Try again.'
    toaster.toast({ description: error.value, variant: 'danger' })
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <Modal v-model:open="open" title="Add board">
    <template #trigger>
      <slot name="trigger">
        <Button>Add board</Button>
      </slot>
    </template>

    <InputText v-model="name" label="Board name" placeholder="" @blur="validateField('name')"
      :error="validationErrors['name']" />

    <template #footer>
      <DialogClose as-child>
        <Button variant="secondary">Cancel</Button>
      </DialogClose>
      <Button variant="primary" :disabled="submitting" @click="submit">
        {{ submitting ? 'Creating...' : 'Create' }}
      </Button>
    </template>
  </Modal>
</template>
