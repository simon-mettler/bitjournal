<script setup lang="ts">
import { computed } from 'vue'
import { useLocalStorage, useMediaQuery } from '@vueuse/core'
import Button from '@/shared/ui/components/Button.vue'
import Dialog from '@/shared/ui/components/Dialog.vue'

const isDesktop = useMediaQuery('(min-width: 768px)')
const acknowledged = useLocalStorage('desktop-notice-acknowledged', false)

const open = computed({
  get: () => isDesktop.value && !acknowledged.value,
  set: () => {},
})
</script>

<template>
  <Dialog
    v-model:open="open"
    title="Built for mobile"
    description="bitjournal is designed for mobile use as an installed app (PWA), not for desktop. You can still use it here, but the interface may feel out of place."
    hide-close
  >
    <template #footer>
      <Button @click="acknowledged = true">I understand</Button>
    </template>
  </Dialog>
</template>
