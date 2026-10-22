import { reactive, watch } from 'vue'
import type { Signal } from '@/modules/signals/types'
import { useTheme } from '@/shared/lib/useTheme'

// Resolve CSS variablef fo ECharts canvas.
function read(name: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}

function resolve() {
  return {
    primary: read('--color-primary'),
    surface: read('--chart-surface'),
    gridLine: read('--chart-grid'),
    axisLabel: read('--chart-axis-label'),
    categoryLabel: read('--chart-category-label'),
    tooltipBackground: read('--chart-tooltip-bg'),
    tooltipText: read('--chart-tooltip-text'),
    heatmapEmpty: read('--chart-empty'),
  }
}

export const chartColors = reactive(resolve())

const { resolvedTheme } = useTheme()
watch(
  resolvedTheme,
  () => {
    Object.assign(chartColors, resolve())
  },
  { flush: 'post' },
)

export function signalColor(signal: Signal): string {
  return signal.color ?? chartColors.primary
}
