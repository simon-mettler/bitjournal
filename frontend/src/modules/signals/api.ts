import { api } from '@/shared/api'
import { markStale } from '@/shared/lib/staleness'
import type { Signal, SignalCategory } from './types'

export type CreateSignalPayload = Omit<Signal, 'id' | 'created_at' | 'updated_at' | 'is_archived'>

// Can't change type after creation
export type UpdateSignalPayload = Partial<Omit<CreateSignalPayload, 'type'>>

export type CreateCategoryPayload = Omit<SignalCategory, 'id'>
export type UpdateCategoryPayload = Partial<CreateCategoryPayload>

// Signals
export function getSignals() {
  return api.get<Signal[]>('signals/')
}

export function getSignal(id: string) {
  return api.get<Signal>(`signals/${id}/`)
}

export function createSignal(payload: CreateSignalPayload) {
  return api.post<Signal>('signals/', payload)
}

export async function updateSignal(id: string, payload: UpdateSignalPayload) {
  const res = await api.patch<Signal>(`signals/${id}/`, payload)
  markStale('journal')
  return res
}

export async function deleteSignal(id: string) {
  const res = await api.delete(`signals/${id}/`)
  markStale('journal')
  return res
}

// Categories
export function getCategories() {
  return api.get<SignalCategory[]>('categories/')
}

export function createCategory(payload: CreateCategoryPayload) {
  return api.post<SignalCategory>('categories/', payload)
}

export function updateCategory(id: string, payload: UpdateCategoryPayload) {
  return api.patch<SignalCategory>(`categories/${id}/`, payload)
}

export function deleteCategory(id: string) {
  return api.delete(`categories/${id}/`)
}
