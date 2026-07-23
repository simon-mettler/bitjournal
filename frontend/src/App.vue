<script setup lang="ts">

import { RouterLink, RouterView } from 'vue-router'
import AuthStatus from '@/components/AuthStatus.vue'
import Toast from '@/shared/ui/components/Toast.vue'

</script>


<template>
  <Toast />

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com">
  <link href="https://fonts.googleapis.com/css2?family=Work+Sans:ital,wght@0,100..900;1,100..900&display=swap"
    rel="stylesheet">

  <header>
    <nav>
      <RouterLink to="/">Home</RouterLink>
      <RouterLink :to="{ name: 'register' }">Register</RouterLink>
    </nav>
  </header>

  <AuthStatus />
  <RouterView />--

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
