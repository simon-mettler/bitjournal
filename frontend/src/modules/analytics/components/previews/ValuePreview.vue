<template>
  <svg viewBox="0 0 120 72" aria-hidden="true">
    <rect class="muted" x="34" y="14" width="52" height="6" rx="3" />
    <text class="number" x="60" y="48" text-anchor="middle">42</text>
    <rect class="muted" x="42" y="58" width="36" height="5" rx="2.5" />
  </svg>
</template>

<style scoped>
.muted {
  fill: var(--color-surface-medium);
  opacity: 0.35;
}

.number {
  fill: var(--color-primary);
  font-size: 28px;
  font-weight: var(--font-weight-bold);
}
</style>
