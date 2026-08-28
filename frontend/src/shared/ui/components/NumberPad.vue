<script setup lang="ts">
import { ArrowRight, Diff, Delete } from '@lucide/vue'
import { useNumpadGroup } from '@/shared/lib/useNumpadGroup'

const group = useNumpadGroup()
const digits = [1, 2, 3, 4, 5, 6, 7, 8, 9]

defineProps<{
  enableDecimal?: boolean
  enableNext?: boolean
  enableSign?: boolean
}>()
</script>

<template>
  <div v-if="group" class="number-pad">
    <div class="number-pad-grid">
      <button v-for="d in digits" :key="d" type="button" class="number-pad-key" :style="{ gridArea: 'd' + d }"
        @click="group.enterDigit(d)">
        {{ d }}
      </button>

      <button v-if="enableSign" type="button" class="number-pad-key number-pad-sign no-bg"
        :style="{ gridArea: enableNext ? 'sign' : 'next' }" aria-label="Toggle positive/negative"
        @click="group.toggleSign()">
        <Diff />
      </button>

      <button type="button" class="number-pad-key number-pad-delete" style="grid-area: del" aria-label="Delete digit"
        @click="group.backspace()">
        <Delete />
      </button>
      <button type="button" class="number-pad-key" style="grid-area: d0" @click="group.enterDigit(0)">
        0
      </button>
      <button :disabled="!enableDecimal" type="button" class="number-pad-key" style="grid-area: dot"
        aria-label="Decimal point" @click="group.enterDot()">
        {{ enableDecimal ? '.' : '' }}
      </button>

      <button v-if="enableNext" type="button" class="number-pad-key number-pad-nav no-bg" style="grid-area: next"
        aria-label="Jump to next field" @click="group.next()">
        <ArrowRight />
      </button>
    </div>
  </div>
</template>
<style scoped>
.number-pad {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin: 16px 0;
  padding: 16px;
  border-radius: 16px;
  background-color: var(--color-surface-muted);
}

.number-pad-header {
  font-size: var(--font-size-sm);
  color: var(--input-color-label);
  text-align: center;
}

.number-pad-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr) 1fr;
  grid-template-rows: repeat(4, 48px);
  grid-template-areas:
    'd1 d2 d3 empty'
    'd4 d5 d6 empty'
    'd7 d8 d9 sign'
    'del d0 dot next';
  gap: var(--spacing-sm);
}

.number-pad-key {
  all: unset;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--input-radius);
  font-size: var(--font-size-h1);
  cursor: pointer;
  background-color: var(--color-surface);
  border: 1px solid #e7e7e7;
}

.no-bg {
  background-color: var(--color-surface-muted);
  border: 1px solid transparent;
}

.number-pad-key:active {
  background-color: var(--color-surface-medium);
}

.number-pad-sign,
.number-pad-nav {
  color: var(--color-primary);
}

.number-pad-delete {
  color: var(--color-danger);
}

.number-pad-delete>svg {
  transform: translateX(-3px);
}
</style>
