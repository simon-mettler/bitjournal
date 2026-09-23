import type { SummaryMethod } from '@/modules/signals/types'
import type { SignalStatsTimeseriesPoint, Timeframe } from './types'

// Group year timeframe into weeks (to dense charts on to read)
export const WEEKLY_BIN_TIMEFRAMES: ReadonlySet<Timeframe> = new Set(['year'])

export interface TimeseriesBin {
  start: string
  end: string
  value: number | null
}

function parseIsoDate(value: string): Date {
  const [year, month, day] = value.split('-').map(Number)
  return new Date(year, month - 1, day)
}

function toIsoDate(date: Date): string {
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${date.getFullYear()}-${m}-${d}`
}

function weekStart(value: string): string {
  const date = parseIsoDate(value)
  date.setDate(date.getDate() - ((date.getDay() + 6) % 7))
  return toIsoDate(date)
}

// Groups daily points into monday-based calendar weeks.
// Uses 'total' or 'average' based on signal setting a
export function binTimeseriesByWeek(
  points: SignalStatsTimeseriesPoint[],
  summaryMethod: SummaryMethod,
): TimeseriesBin[] {
  const bins: (TimeseriesBin & { present: number[] })[] = []

  for (const point of points) {
    const start = weekStart(point.date)
    let bin = bins[bins.length - 1]
    if (!bin || bin.start !== start) {
      bin = { start, end: point.date, value: null, present: [] }
      bins.push(bin)
    }
    bin.end = point.date
    if (point.value !== null) bin.present.push(point.value)
  }

  return bins.map(({ start, end, present }) => {
    if (present.length === 0) return { start, end, value: null }
    const sum = present.reduce((acc, v) => acc + v, 0)
    return { start, end, value: summaryMethod === 'average' ? sum / present.length : sum }
  })
}
