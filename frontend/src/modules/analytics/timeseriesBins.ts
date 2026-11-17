import type { SummaryMethod } from '@/modules/signals/types'
import { parseIsoDate } from './format'
import type { SignalStatsTimeseriesPoint, Timeframe } from './types'

// Group year timeframe into weeks (to dense charts on to read)
export const WEEKLY_BIN_TIMEFRAMES: ReadonlySet<Timeframe> = new Set(['year'])

export interface TimeseriesBin {
  start: string
  end: string
  value: number | null
  sum: number
  count: number
}

// Periods longer than this are binned into weeks.
const WEEKLY_BIN_MIN_DAYS = 100

export function periodUsesWeeklyBins(period: { start: string; end: string }): boolean {
  const days =
    (parseIsoDate(period.end).getTime() - parseIsoDate(period.start).getTime()) / 86_400_000
  return days > WEEKLY_BIN_MIN_DAYS
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

export function binTimeseriesByWeek(
  points: SignalStatsTimeseriesPoint[],
  summaryMethod: SummaryMethod,
): TimeseriesBin[] {
  const bins: TimeseriesBin[] = []

  for (const point of points) {
    const start = weekStart(point.date)
    let bin = bins[bins.length - 1]
    if (!bin || bin.start !== start) {
      bin = { start, end: point.date, value: null, sum: 0, count: 0 }
      bins.push(bin)
    }
    bin.end = point.date
    bin.sum += point.sum
    bin.count += point.count
  }

  for (const bin of bins) {
    if (summaryMethod === 'average') bin.value = bin.count > 0 ? bin.sum / bin.count : null
    else bin.value = bin.sum
  }
  return bins
}
