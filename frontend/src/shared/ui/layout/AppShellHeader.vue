<script setup lang="ts">
import { APP_SHELL_HEADER_ID } from '@/shared/lib/appShellSlots'
</script>

<template>
  <Teleport :to="`#${APP_SHELL_HEADER_ID}`" defer>
    <slot />
  </Teleport>
</template>
