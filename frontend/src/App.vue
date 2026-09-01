<script setup lang="ts">
import Toast from '@/shared/ui/components/Toast.vue'
import AppShell from '@/shared/ui/layout/AppShell.vue'
import { useViewportHeight } from './shared/lib/useViewportHeight';

useViewportHeight()
</script>


<template>
  <meta name="viewport"
    content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover" />
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com">
  <link href="https://fonts.googleapis.com/css2?family=Work+Sans:ital,wght@0,100..900;1,100..900&display=swap"
    rel="stylesheet">

  <Toast />
  <AppShell />
</template>


<style>
body {
  background-color: var(--color-app-bg);
  margin: 0px;
  font-family: "Work sans", sans-serif;
}

:focus-visible {
  outline: none;
  box-shadow: var(--input-shadow-focus) !important;
  border: var(--input-border-focus) !important;
}

html,
body {
  -webkit-user-select: none;
  user-select: none;
  touch-action: pan-x pan-y;
}

input,
textarea {
  -webkit-user-select: text;
  user-select: text;
}

a {
  color: var(--color-primary);
  text-decoration: underline;
}
</style>
