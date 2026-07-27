<script setup lang="ts">
import AuthStatus from '@/components/AuthStatus.vue'
import Toast from '@/shared/ui/components/Toast.vue'
import AppShell from '@/shared/ui/layout/AppShell.vue'
</script>


<template>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com">
  <link href="https://fonts.googleapis.com/css2?family=Work+Sans:ital,wght@0,100..900;1,100..900&display=swap"
    rel="stylesheet">

  <AuthStatus />
  <Toast />
  <AppShell />
</template>


<style>
body {
  background-color: var(--color-app-bg);
  padding: var(--padding-app);
  margin: 0px;
  font-family: "Work sans", sans-serif;
}

:focus-visible {
  outline: none;
  box-shadow: var(--input-shadow-focus) !important;
  border: var(--input-border-focus) !important;
}
</style>
