import type { CalendarDate } from '@internationalized/date'
import type { Signal } from '@/modules/signals/types'
import type { AnalyticsWidget, SignalStatsPeriod, Timeframe, WidgetTimeframe } from './types'

function formatSecondsDuration(totalSeconds: number): string {
  const h = Math.floor(totalSeconds / 3600)
  const m = Math.floor((totalSeconds % 3600) / 60)
  const s = Math.floor(totalSeconds % 60)

  if (h > 0) return `${h}h ${m}m`
  if (m > 0) return `${m}min`
  return `${s}s`
}

// Format label for durations (like 45m or 1:30h).
export function formatDurationAxisLabel(totalSeconds: number): string {
  const h = Math.floor(totalSeconds / 3600)
  const m = Math.floor((totalSeconds % 3600) / 60)
  const s = Math.floor(totalSeconds % 60)

  if (h > 0) return m > 0 ? `${h}:${String(m).padStart(2, '0')}h` : `${h}h`
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

const SHIFT_BY_TIMEFRAME: Record<
  Timeframe,
  { unit: 'weeks' | 'months' | 'years'; amount: number }
> = {
  week: { unit: 'weeks', amount: 1 },
  month: { unit: 'months', amount: 1 },
  quarter: { unit: 'months', amount: 3 },
  year: { unit: 'years', amount: 1 },
}

export function shiftPeriod(
  date: CalendarDate,
  timeframe: Timeframe,
  direction: 1 | -1,
): CalendarDate {
  const { unit, amount } = SHIFT_BY_TIMEFRAME[timeframe]
  return date.add({ [unit]: amount * direction })
}

export function parseIsoDate(value: string): Date {
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
      const endFmt = new Intl.DateTimeFormat(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      })
      return `${startFmt.format(start)} - ${endFmt.format(endInclusive)}`
    }
  }
}

export const WIDGET_TIMEFRAME_LABELS: Record<WidgetTimeframe, string> = {
  today: 'Today',
  yesterday: 'Yesterday',
  this_week: 'This week',
  last_week: 'Last week',
  this_month: 'This month',
  last_month: 'Last month',
  this_quarter: 'This quarter',
  quarter: 'Earlier quarter',
  this_year: 'This year',
  year: 'Earlier year',
  last_days: 'Last X days',
}

function toIsoDate(year: number, month: number): string {
  return `${year}-${String(month).padStart(2, '0')}-01`
}

// Calculate previous quarters
export function earlierQuarterOptions(count = 12): { value: string; label: string }[] {
  const today = new Date()
  let year = today.getFullYear()
  let quarter = Math.floor(today.getMonth() / 3) + 1
  const options = []
  for (let i = 0; i < count; i++) {
    quarter -= 1
    if (quarter === 0) {
      quarter = 4
      year -= 1
    }
    options.push({ value: toIsoDate(year, (quarter - 1) * 3 + 1), label: `Q${quarter} ${year}` })
  }
  return options
}

// Calculate previous years
export function earlierYearOptions(count = 10): { value: string; label: string }[] {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: count }, (_, i) => {
    const year = currentYear - 1 - i
    return { value: toIsoDate(year, 1), label: String(year) }
  })
}

export function formatWidgetTimeframe(
  widget: Pick<AnalyticsWidget, 'timeframe' | 'period_start' | 'days'>,
): string {
  if (widget.timeframe === 'last_days') {
    return widget.days === 1 ? 'Last day' : `Last ${widget.days} days`
  }
  if (widget.period_start && (widget.timeframe === 'quarter' || widget.timeframe === 'year')) {
    const start = parseIsoDate(widget.period_start)
    return widget.timeframe === 'year'
      ? String(start.getFullYear())
      : `Q${Math.floor(start.getMonth() / 3) + 1} ${start.getFullYear()}`
  }
  return WIDGET_TIMEFRAME_LABELS[widget.timeframe]
}
