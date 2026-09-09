import type { Event } from '@/modules/events/types'

export interface JournalDayGroup {
  key: string
  label: string
  events: Event[]
}

const timeFormatter = new Intl.DateTimeFormat(undefined, {
  hour: 'numeric',
  minute: '2-digit',
})

const dayFormatter = new Intl.DateTimeFormat(undefined, {
  month: 'long',
  day: 'numeric',
  year: 'numeric',
})

function dayKey(date: Date): string {
  return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`
}

function isSameDay(a: Date, b: Date): boolean {
  return dayKey(a) === dayKey(b)
}

export function formatEventTime(occurredAt: string): string {
  return timeFormatter.format(new Date(occurredAt))
}

export function formatDayLabel(date: Date): string {
  const now = new Date()
  const yesterday = new Date(now)
  yesterday.setDate(now.getDate() - 1)

  if (isSameDay(date, now)) return 'Today'
  if (isSameDay(date, yesterday)) return 'Yesterday'
  return dayFormatter.format(date)
}

// Groups events by calendar day, newest day first, newest event first within a day.
export function groupEventsByDay(events: Event[]): JournalDayGroup[] {
  const sorted = [...events].sort(
    (a, b) => new Date(b.occurred_at).getTime() - new Date(a.occurred_at).getTime(),
  )

  const groups: JournalDayGroup[] = []
  const indexByKey = new Map<string, number>()

  for (const event of sorted) {
    const date = new Date(event.occurred_at)
    const key = dayKey(date)
    let index = indexByKey.get(key)
    if (index === undefined) {
      index = groups.length
      indexByKey.set(key, index)
      groups.push({ key, label: formatDayLabel(date), events: [] })
    }
    groups[index].events.push(event)
  }

  return groups
}
