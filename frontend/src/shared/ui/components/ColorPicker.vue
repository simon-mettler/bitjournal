<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useId } from 'vue'
import { Label } from 'reka-ui'
import type { Color } from 'reka-ui'
import {
  ColorAreaArea,
  ColorAreaRoot,
  ColorAreaThumb,
  ColorFieldInput,
  ColorFieldRoot,
  ColorSliderRoot,
  ColorSliderThumb,
  ColorSliderTrack,
  ColorSwatch,
  colorToString,
  normalizeColor,
  DialogClose,
} from 'reka-ui'
import Dialog from '@/shared/ui/components/Dialog.vue'

const model = defineModel<string>({ default: '#4f46e5' })

const colorObj = computed<Color>({
  get: () => normalizeColor(model.value),
  set: (val) => {
    model.value = colorToString(val, 'hex')
  },
})

const hexColor = computed(() => colorToString(colorObj.value, 'hex'))

function handleColorUpdate(newColor: Color) {
  colorObj.value = newColor
}

function handleHexUpdate(hex: string) {
  colorObj.value = normalizeColor(hex)
}

const hueId = useId()
const alphaId = useId()
const hexId = useId()
</script>

<template>
  <Dialog title="Color">

    <template #trigger>
      <button type="button" class="swatch-trigger">
        <ColorSwatch :color="hexColor" class="swatch-preview"
          :style="{ backgroundColor: 'var(--reka-color-swatch-color)' }" />
      </button>
    </template>

    <div class="picker">

      <!-- 2D color area (saturation/lightness) -->
      <ColorAreaRoot v-slot="{ style }" :model-value="colorObj" color-space="hsl" x-channel="saturation"
        y-channel="lightness" @update:color="handleColorUpdate">
        <ColorAreaArea class="area" :style="style">
          <ColorAreaThumb class="area-thumb" />
        </ColorAreaArea>
      </ColorAreaRoot>

      <!-- Hue slider -->
      <div class="field-group">
        <Label class="field-label" :for="hueId">Hue</Label>
        <ColorSliderRoot :model-value="colorObj" :id="hueId" channel="hue" color-space="hsl" class="slider-root"
          @update:color="handleColorUpdate">
          <ColorSliderTrack class="slider-track hue-gradient" />
          <ColorSliderThumb class="slider-thumb" />
        </ColorSliderRoot>
      </div>

      <!-- Alpha slider -->
      <div class="field-group">
        <Label class="field-label" :for="alphaId">Alpha</Label>
        <ColorSliderRoot :model-value="colorObj" :id="alphaId" channel="alpha" color-space="hsl" class="slider-root"
          @update:color="handleColorUpdate">
          <ColorSliderTrack class="slider-track checkerboard-bg" />
          <ColorSliderThumb class="slider-thumb" />
        </ColorSliderRoot>
      </div>

      <!-- HEX value field -->
      <div class="field-group">
        <Label class="field-label" :id="hexId">HEX</Label>
        <ColorFieldRoot :model-value="hexColor" :id="hexId" class="field-hex" @update:model-value="handleHexUpdate">
          <ColorFieldInput class="field-input" placeholder="#000000" />
        </ColorFieldRoot>
      </div>

    </div>

    <template #footer>
      <DialogClose as-child>
        <button type="button" class="Button green">Done</button>
      </DialogClose>
    </template>

  </Dialog>
</template>

<style scoped>
.swatch-trigger {
  background-color: transparent;
  padding: 0;
  width: 44px;
  min-width: 44px;
  height: 44px;
  border-radius: var(--input-radius);
  border: var(--input-border);
  cursor: pointer;
  overflow: hidden;
}

.swatch-preview {
  width: 100%;
  height: 100%;
}

.picker {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.area {
  position: relative;
  height: 140px;
  border-radius: 8px;
  border: 2px solid var(--colorpicker-area-color-border);
}

.area-thumb {
  display: block;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: white;
  border: 2px solid white;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.3), 0 1px 3px rgba(0, 0, 0, 0.4);
  cursor: pointer;
  transition: transform 0.15s;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-normal);
  color: var(--input-color-label);
}

.slider-root {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
  height: 16px;
  touch-action: none;
  user-select: none;
}

.slider-track {
  position: relative;
  flex: 1;
  height: 8px;
  border-radius: 999px;
  overflow: hidden;
}

.hue-gradient {
  background: linear-gradient(to right,
      #ff0000 0%, #ffff00 17%, #00ff00 33%,
      #00ffff 50%, #0000ff 67%, #ff00ff 83%, #ff0000 100%);
}

.checkerboard-bg {
  background-image:
    linear-gradient(45deg, #808080 25%, transparent 25%),
    linear-gradient(-45deg, #808080 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, #808080 75%),
    linear-gradient(-45deg, transparent 75%, #808080 75%);
  background-size: 8px 8px;
  background-position: 0 0, 0 4px, 4px -4px, -4px 0px;
  background-color: #404040;
}

.slider-thumb {
  display: block;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: white;
  border: 2px solid white;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.3), 0 1px 3px rgba(0, 0, 0, 0.4);
  cursor: pointer;
  transition: transform 0.15s;
  top: calc(50% - 8px);
}

.slider-thumb:hover {
  transform: scale(1.1);
}

.field-hex {
  display: block;
  width: 100%;
}

.field-input {
  display: inline-flex;
  width: 100%;
  box-sizing: border-box;
  padding: 0 10px;
  font-size: var(--font-size-base);
  border: var(--input-border);
  border-radius: var(--input-radius);
  color: var(--input-color-text);
  background-color: var(--input-color-background);
  height: var(--input-height);
}

.field-input:focus {
  box-shadow: var(--input-shadow-focus);
  border: var(--input-border-focus);
}
</style>
