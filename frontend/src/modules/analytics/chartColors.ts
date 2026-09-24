import type { Signal } from '@/modules/signals/types'

const primary = getComputedStyle(document.documentElement).getPropertyValue('--color-primary').trim()

export const chartColors = {
  primary,
  surface: '#ffffff',
  gridLine: '#ECEEF1',
  axisLabel: '#9AA1A9',
  categoryLabel: '#6B7280',
  tooltipBackground: '#1F2937',
  tooltipText: '#ffffff',
  heatmapEmpty: '#F1F4F8',
}

export function signalColor(signal: Signal): string {
  return signal.color ?? primary
}
