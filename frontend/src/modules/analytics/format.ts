import type { CalendarDate } from '@internationalized/date'
import type { Signal } from '@/modules/signals/types'
import type { SignalStatsPeriod, Timeframe } from './types'

function formatSecondsDuration(totalSeconds: number): string {
  const h = Math.floor(totalSeconds / 3600)
  const m = Math.floor((totalSeconds % 3600) / 60)
  const s = Math.floor(totalSeconds % 60)

  if (h > 0) return `${h}h ${m}m`
  if (m > 0) return `${m}min`
  return `${s}s`
}

// Format label for durations (like 45m or 2h).
export function formatDurationAxisLabel(totalSeconds: number): string {
  const h = Math.floor(totalSeconds / 3600)
  const m = Math.floor((totalSeconds % 3600) / 60)
  const s = Math.floor(totalSeconds % 60)

  if (h > 0) return m > 0 ? `${h}h ${m}m` : `${h}h`
  if (m > 0) return s > 0 ? `${m}m ${s}s` : `${m}m`
  return `${s}s`
}

const DURATION_AXIS_STEPS = [
  1, 5, 10, 15, 30, 60, 120, 300, 600, 900, 1800, 3600, 7200, 10800, 21600, 43200, 86400,
]
const MAX_AXIS_TICKS = 5

// Snap y-axis to whole seconds/minutes/hours
export function durationAxisScale(maxSeconds: number): { max: number; interval: number } {
  const target = Math.max(maxSeconds, 60) / MAX_AXIS_TICKS
  let interval = DURATION_AXIS_STEPS.find((step) => step >= target)
  if (interval === undefined) interval = Math.ceil(target / 86400) * 86400
  return { max: Math.ceil(Math.max(maxSeconds, 60) / interval) * interval, interval }
}

function roundTo2(value: number): number {
  return Math.round(value * 100) / 100
}

export function formatStatValue(signal: Signal, value: number): string {
  if (signal.type === 'duration') {
    return formatSecondsDuration(value)
  }
  if (signal.type === 'tally') {
    return `${roundTo2(value)}`
  }
  const unit = signal.value_config?.unit ?? ''
  return `${roundTo2(value)}${unit}`
}

const SHIFT_BY_TIMEFRAME: Record<Timeframe, { unit: 'weeks' | 'months' | 'years'; amount: number }> = {
  week: { unit: 'weeks', amount: 1 },
  month: { unit: 'months', amount: 1 },
  quarter: { unit: 'months', amount: 3 },
  year: { unit: 'years', amount: 1 },
}

export function shiftPeriod(date: CalendarDate, timeframe: Timeframe, direction: 1 | -1): CalendarDate {
  const { unit, amount } = SHIFT_BY_TIMEFRAME[timeframe]
  return date.add({ [unit]: amount * direction })
}

function parseIsoDate(value: string): Date {
  const [year, month, day] = value.split('-').map(Number)
  return new Date(year, month - 1, day)
}

export function formatPeriodRange(period: SignalStatsPeriod): string {
  const start = parseIsoDate(period.start)
  const endInclusive = parseIsoDate(period.end)
  endInclusive.setDate(endInclusive.getDate() - 1)

  switch (period.timeframe) {
    case 'year':
      return String(start.getFullYear())
    case 'quarter': {
      const quarter = Math.floor(start.getMonth() / 3) + 1
      return `Q${quarter} ${start.getFullYear()}`
    }
    case 'month':
      return new Intl.DateTimeFormat(undefined, { month: 'long', year: 'numeric' }).format(start)
    case 'week':
    default: {
      const startFmt = new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric' })
      const endFmt = new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
      return `${startFmt.format(start)} - ${endFmt.format(endInclusive)}`
    }
  }
}
