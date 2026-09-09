import type { DraftEntry } from './types'
import type { SignalEventEntry } from './types'

export function formatDuration(duration: string): string {
  const [h, m, s] = duration.split(':').map(Number)

  if (h > 0) return `${h}h ${m}m`
  if (m > 0) return `${m}min`
  return `${s}s`
}

export function formatDraftEntryLabel(entry: DraftEntry | SignalEventEntry): string {
  if (entry.signal.type === 'tally') {
    return entry.signal.name
  }
  if (entry.signal.type === 'duration' && entry.duration !== undefined) {
    return `${entry.signal.name}: ${formatDuration(entry.duration)}`
  }
  const unit = entry.signal.value_config?.unit ?? ''
  return `${entry.signal.name}: ${Number(entry.value)}${unit}`
}
