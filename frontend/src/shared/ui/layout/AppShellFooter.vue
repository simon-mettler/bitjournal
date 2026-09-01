<script setup lang="ts">
import { APP_SHELL_FOOTER_ID } from '@/shared/lib/appShellSlots'
</script>

<template>
  <Teleport :to="`#${APP_SHELL_FOOTER_ID}`" defer>
    <slot />
  </Teleport>
</template>
