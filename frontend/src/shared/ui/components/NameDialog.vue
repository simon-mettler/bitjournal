<script setup lang="ts">
import { ref, watch } from 'vue'
import { DialogClose } from 'reka-ui'
import Modal from '@/shared/ui/components/Dialog.vue'
import Button from '@/shared/ui/components/Button.vue'
import InputText from '@/shared/ui/components/InputText.vue'
import { useFormValidation } from '@/shared/lib/useFormValidation'
import { required, maxLength } from '@/shared/lib/validators'

const props = defineProps<{
  title: string
  label: string
  confirmText: string
  initialName?: string
  busy?: boolean
}>()

const emit = defineEmits<{ submit: [name: string] }>()

const open = defineModel<boolean>('open', { default: false })
const name = ref('')

const { errors, validateField, validateAll, clear } = useFormValidation(
  { name: () => name.value },
  { name: [required('Name is required'), maxLength(100, '100 characters or fewer')] },
)

watch(open, (isOpen) => {
  if (!isOpen) return
  name.value = props.initialName ?? ''
  clear()
})

function submit() {
  if (props.busy || !validateAll()) return
  emit('submit', name.value.trim())
}
</script>

<template>
  <Modal v-model:open="open" :title="title">
    <div @keydown.enter.prevent="submit">
      <InputText
        v-model="name"
        :label="label"
        placeholder=""
        :error="errors['name']"
        @blur="validateField('name')"
      />
    </div>

    <template #footer>
      <DialogClose as-child>
        <Button variant="secondary">Cancel</Button>
      </DialogClose>
      <Button variant="primary" :disabled="busy" @click="submit">
        {{ busy ? 'Saving...' : confirmText }}
      </Button>
    </template>
  </Modal>
</template>
