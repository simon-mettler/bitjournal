<script setup lang="ts">
import { computed, ref } from 'vue'

const props = withDefaults(
  defineProps<{
    variant?: 'full' | 'mark'
    animate?: boolean
  }>(),
  { variant: 'full', animate: true },
)

const FINALS = [
  [0, 0.4, 0.7, 0.95],
  [0, 0.5, 0.85, 0.65],
  [0, 0, 0, 0.9],
  [0, 0.45, 0.7, 0],
  [0, 0, 0, 1],
]
const CELL = 63
const STEP = 79
const ORIGIN_X = 83
const ORIGIN_Y = 58

function buildCells() {
  return FINALS.flatMap((row, r) =>
    row.map((opacity, c) => {
      const duration = 1.2 + Math.random() * 0.3
      const end = 1.5 + Math.random() * 0.7
      return {
        key: `${r}-${c}`,
        x: ORIGIN_X + c * STEP,
        y: ORIGIN_Y + r * STEP,
        style: {
          '--o': opacity || 'var(--logo-idle)',
          '--t': `${duration.toFixed(2)}s`,
          '--d': `${(end - duration).toFixed(2)}s`,
        },
      }
    }),
  )
}

const cells = ref(buildCells())
const run = ref(0)
const viewBox = computed(() => (props.variant === 'mark' ? '64 40 330 416' : '0 0 1890 510'))

function replay() {
  cells.value = buildCells()
  run.value++
}

defineExpose({ replay })
</script>

<template>
  <svg
    :key="run"
    class="logo"
    :class="{ animate }"
    :viewBox="viewBox"
    role="img"
    aria-label="bitjournal"
    @click="replay"
  >
    <rect
      v-for="cell in cells"
      :key="cell.key"
      class="cell"
      :x="cell.x"
      :y="cell.y"
      :width="CELL"
      :height="CELL"
      rx="14"
      :style="cell.style"
    />
    <text v-if="variant === 'full'" class="word" x="515" y="352">bitjournal</text>
  </svg>
</template>

<style scoped>
.logo {
  --logo-idle: 0.08;

  display: block;
  height: auto;
  overflow: visible;
  color: var(--color-primary);
}

:global([data-theme='dark']) .logo {
  --logo-idle: 0.13;
}

.cell {
  fill: currentcolor;
  opacity: var(--o);
}

.word {
  fill: currentcolor;
  font-family: Figtree, 'Helvetica Neue', Arial, sans-serif;
  font-weight: 600;
  font-size: 296px;
}

.animate .cell {
  opacity: var(--logo-idle);
  animation: pulse var(--t) ease-in-out var(--d) forwards;
}

@keyframes pulse {
  0% {
    opacity: var(--logo-idle);
  }

  33% {
    opacity: 1;
  }

  66% {
    opacity: 0.2;
  }

  100% {
    opacity: var(--o);
  }
}

@media (prefers-reduced-motion: reduce) {
  .animate .cell {
    animation: none;
    opacity: var(--o);
  }
}
</style>
