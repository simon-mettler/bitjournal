<script setup lang="ts">
import { useId, computed, ref } from 'vue'
import Drawer from '@/shared/ui/components/Drawer.vue'
import InputNumber from '@/shared/ui/components/InputNumber.vue'
import NumberPad from '@/shared/ui/components/NumberPad.vue'
import Button from '@/shared/ui/components/Button.vue'
import { provideNumpadGroup } from '@/shared/lib/useNumpadGroup'
import {
  Label,
  TimeFieldInput,
  TimeFieldRoot,
  type TimeValue,
} from 'reka-ui'
import { Time } from '@internationalized/date'

const props = withDefaults(
  defineProps<{
    label?: string
    granularity?: 'hour' | 'minute' | 'second'
  }>(),
  {
    granularity: 'minute',
  },
)

const drawerOpen = ref(false)
function openDrawer() {
  drawerOpen.value = true
}

const id = useId()
const model = defineModel<TimeValue>()

provideNumpadGroup(true)

function updateField(field: 'hour' | 'minute' | 'second', value: number) {
  const base = model.value ?? new Time(0, 0, 0)
  model.value = base.set({ [field]: value })
}

const hours = computed({
  get: () => model.value?.hour ?? 0,
  set: (v: number) => updateField('hour', v),
})
const minutes = computed({
  get: () => model.value?.minute ?? 0,
  set: (v: number) => updateField('minute', v),
})
const seconds = computed({
  get: () => model.value?.second ?? 0,
  set: (v: number) => updateField('second', v),
})
</script>

<template>
  <div class="time-field-wrapper" @click="openDrawer">
    <Label v-if="label" :for="id" class="time-field-label">
      {{ label }}
    </Label>

    <TimeFieldRoot :model-value="model" :id="id" v-slot="{ segments }" :granularity="granularity" :hourCycle="24"
      readonly class="time-field">
      <template v-for="item in segments" :key="item.part">
        <TimeFieldInput v-if="item.part === 'literal'" :part="item.part" class="time-field-literal">
          {{ item.value }}
        </TimeFieldInput>
        <TimeFieldInput v-else :part="item.part" class="time-field-segment">
          {{ item.value }}
        </TimeFieldInput>
      </template>
    </TimeFieldRoot>

    <Drawer v-model:open="drawerOpen" title="Select time">
      <div class="time-numpad-inputs">
        <InputNumber v-model="hours" label="Hours" :min="0" :max="23" :max-length="2" />
        <InputNumber v-model="minutes" label="Minutes" :min="0" :max="59" :max-length="2" />
        <InputNumber v-if="granularity === 'second'" v-model="seconds" label="Seconds" :min="0" :max="59"
          :max-length="2" />
      </div>
      <NumberPad enable-next />

      <template #footer>
        <div class="footer">
          <Button variant="primary" @click="drawerOpen = false">
            Done
          </Button>
        </div>
      </template>

    </Drawer>
  </div>
</template>

<style scoped>
.time-field-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.time-field {
  display: flex;
  align-items: center;
  text-align: center;
  user-select: none;
  box-sizing: border-box;
  padding: 0 10px;
  border-radius: var(--input-radius);
  color: var(--input-color-text);
  background-color: var(--input-color-background);
  border: var(--input-border);
}

.time-field-label {
  padding-left: 8px;
  margin-bottom: 6px;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-normal);
  color: var(--input-color-label);
}

.time-field-literal,
.time-field-segment {
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  min-height: calc(var(--input-height) - 4px);
}

.time-numpad-inputs {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
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
