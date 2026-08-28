<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { CirclePlus, CircleCheck } from '@lucide/vue'
import Drawer from '@/shared/ui/components/Drawer.vue'
import Button from '@/shared/ui/components/Button.vue'
import RangeSlider from '@/shared/ui/components/RangeSlider.vue'
import DurationInput from '@/shared/ui/components/DurationInput.vue'
import NumberPad from '@/shared/ui/components/NumberPad.vue'
import InputNumber from '@/shared/ui/components/InputNumber.vue'
import { provideNumpadGroup } from '@/shared/lib/useNumpadGroup'
import { resolveIcon } from '@/shared/lib/iconRegistry'
import type { Signal } from '@/modules/signals/types'
import type { DraftEntry } from '@/modules/events/types'

const props = defineProps<{
  signal: Signal
  initialValue?: number
  initialDuration?: string
  editing?: boolean
  numpad?: boolean // false = native number keyboard, true = custom pad
}>()

// covers the lone "value" field; DurationInput provides its own nested
// group for hours/minutes/seconds, which shadows this one for its children.
provideNumpadGroup(props.numpad ?? false)

const emit = defineEmits<{ save: [entry: DraftEntry] }>()
const open = defineModel<boolean>('open', { default: false })

const icon = computed(() => resolveIcon(props.signal.icon))
const defaultRange = computed(() => props.signal.range_config?.min_value ?? 0)

const numberValue = ref(0)
const rangeValue = ref(defaultRange.value)
const hours = ref(0)
const minutes = ref(0)
const seconds = ref(0)

watch(open, (isOpen) => {
  if (!isOpen) return

  numberValue.value = props.initialValue ?? 0
  rangeValue.value = props.initialValue ?? defaultRange.value

  const [h = 0, m = 0, s = 0] = props.initialDuration?.split(':').map(Number) ?? []

  hours.value = h
  minutes.value = m
  seconds.value = s
})

const duration = computed(() =>
  [hours.value, minutes.value, seconds.value]
    .map(value => String(value).padStart(2, '0'))
    .join(':'),
)

function submit() {
  const entry: DraftEntry = {
    signal: props.signal,
    id: '',
  }

  switch (props.signal.type) {
    case 'duration':
      entry.duration = duration.value
      break

    case 'tally':
      entry.value = 1
      break

    case 'range':
      entry.value = rangeValue.value
      break

    case 'value':
      entry.value = Number(numberValue.value)
      break
  }

  emit('save', entry)
  open.value = false
}
</script>

<template>
  <Drawer v-model:open="open" :title="signal.name">
    <template v-if="icon" #icon>
      <component :is="icon" :size="24" :style="{ color: signal.color }" />
    </template>

    <InputNumber v-if="signal.type === 'value'" v-model="numberValue" :label="signal.value_config?.unit ?? ''" />

    <RangeSlider v-else-if="signal.type === 'range'" v-model="rangeValue" :min="signal.range_config?.min_value ?? 0"
      :max="signal.range_config?.max_value ?? 100" :min-label="signal.range_config?.min_label"
      :max-label="signal.range_config?.max_label" />

    <DurationInput v-else-if="signal.type === 'duration'" v-model:hours="hours" v-model:minutes="minutes"
      v-model:seconds="seconds" :numpad="numpad" />

    <p v-else class="tally-note">
      Tap add to log this.
    </p>

    <NumberPad v-if="numpad && signal.type === 'value'" enable-decimal enable-sign />

    <template #footer>
      <div class="footer">

        <Button variant="secondary" @click="open = false">
          Cancel
        </Button>

        <Button variant="primary" @click="submit">
          <template #icon>
            <CircleCheck v-if="editing" :size="18" />
            <CirclePlus v-else :size="18" />
          </template>
          {{ editing ? 'Save' : 'Add' }}
        </Button>

      </div>
    </template>

  </Drawer>
</template>

<style scoped>
.tally-note {
  text-align: center;
  color: var(--input-color-label);
  padding: var(--spacing-lg) 0;
}

.footer {
  display: flex;
  width: 100%;
  gap: var(--spacing-md);
}

button {
  flex: 1;
}
</style>
