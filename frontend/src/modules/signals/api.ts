import { api } from '@/shared/api'
import type {
  Signal,
  SignalCategory,
} from './types'

export type CreateSignalPayload = Omit<
  Signal,
  'id' | 'created_at' | 'updated_at' | 'is_archived'
>

// Can't change type after creation
export type UpdateSignalPayload = Partial<Omit<CreateSignalPayload, 'type'>>

export type CreateCategoryPayload = Omit<SignalCategory, 'id'>
export type UpdateCategoryPayload = Partial<CreateCategoryPayload>

// Signals
export function getSignals() {
  return api.get<Signal[]>('signals/')
}

export function getSignal(id: number) {
  return api.get<Signal>(`signals/${id}/`)
}

export function createSignal(payload: CreateSignalPayload) {
  return api.post<Signal>('signals/', payload)
}

export function updateSignal(id: number, payload: UpdateSignalPayload) {
  return api.patch<Signal>(`signals/${id}/`, payload)
}

export function deleteSignal(id: number) {
  return api.delete(`signals/${id}/`)
}

// Categories
export function getCategories() {
  return api.get<SignalCategory[]>('categories/')
}

export function createCategory(payload: CreateCategoryPayload) {
  return api.post<SignalCategory>('categories/', payload)
}

export function updateCategory(id: number, payload: UpdateCategoryPayload) {
  return api.patch<SignalCategory>(`categories/${id}/`, payload)
}

export function deleteCategory(id: number) {
  return api.delete(`categories/${id}/`)
}
