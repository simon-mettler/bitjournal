import type { DraftEntry } from './types'

export function durationToHours(duration: string): string {
  const [h, m, s] = duration.split(':').map(Number)
  const totalHours = h + m / 60 + s / 3600
  return (Math.round(totalHours * 100) / 100).toString()
}

export function formatDraftEntryLabel(entry: DraftEntry): string {
  if (entry.duration !== undefined) {
    return `${entry.signal.name}: ${durationToHours(entry.duration)}h`
  }
  const unit = entry.signal.value_config?.unit ?? ''
  return `${entry.signal.name}: ${entry.value}${unit}`
}
