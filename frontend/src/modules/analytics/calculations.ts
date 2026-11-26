import type { Signal } from '@/modules/signals/types'
import type { WidgetCalculation } from './types'

export const CALCULATION_LABELS: Record<WidgetCalculation, string> = {
  total: 'Total',
  daily_average: 'Daily average',
  average: 'Average per entry',
}

const SHORT_LABELS: Record<WidgetCalculation, string> = {
  total: 'Total',
  daily_average: 'Daily avg',
  average: 'Avg per entry',
}

export const CALCULATIONS = Object.keys(CALCULATION_LABELS) as WidgetCalculation[]

export function availableCalculations(signal: Signal | undefined): WidgetCalculation[] {
  return signal?.type === 'tally' ? ['total', 'daily_average'] : CALCULATIONS
}

export function defaultCalculation(signal: Signal): WidgetCalculation {
  return signal.summary_method === 'average' ? 'daily_average' : 'total'
}

export function countsEmptyDaysAsZero(signal: Signal): boolean {
  return signal.summary_method === 'total' || signal.empty_days_as_zero
}

export function showsEmptyDaysAsZero(signal: Signal, calculation: WidgetCalculation): boolean {
  return (
    calculation === 'daily_average' &&
    signal.summary_method === 'average' &&
    signal.empty_days_as_zero
  )
}

export function calculationOptions(signal: Signal | undefined) {
  return availableCalculations(signal).map((value) => ({ value, label: SHORT_LABELS[value] }))
}

export function calculationHint(calculation: WidgetCalculation, signal: Signal | undefined) {
  if (calculation === 'total') return 'All entries added up.'
  if (calculation === 'average') return 'The mean of all entries.'
  if (!signal) return 'The mean of the daily values.'
  const daily = signal.summary_method === 'average' ? 'average' : 'total'
  return countsEmptyDaysAsZero(signal)
    ? `Each day's ${daily}, averaged over days. Days without entries count as 0.`
    : `Each day's ${daily}, averaged over the days with entries.`
}

export function isLevel(signal: Signal, calculation: WidgetCalculation): boolean {
  return (
    calculation === 'average' ||
    (calculation === 'daily_average' && signal.summary_method === 'average')
  )
}
