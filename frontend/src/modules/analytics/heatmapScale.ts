// Shared by HeatmapChart (canvas, can't read CSS custom properties) and
// HeatmapLegend. Index 0 is "no entries", 1-3 are increasing intensity.
export const HEATMAP_COLORS = ['#F1F4F8', '#C8F5EB', '#34D0BB', '#0F8E80'] as const

export function heatmapLevel(value: number, max: number): 1 | 2 | 3 {
  const ratio = max > 0 ? value / max : 1
  if (ratio > 2 / 3) return 3
  if (ratio > 1 / 3) return 2
  return 1
}
