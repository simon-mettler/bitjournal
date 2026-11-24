import { api } from '@/shared/api'

export interface ChangePasswordPayload {
  current_password: string
  new_password: string
}

export function changePassword(payload: ChangePasswordPayload) {
  return api.post<void>('users/me/password/', payload)
}

export function logoutAll() {
  return api.post<void>('users/me/logout-all/')
}

export interface ChangeEmailPayload {
  new_email: string
  current_password: string
}

export interface ChangeEmailResult {
  status: 'changed' | 'confirmation_sent'
  email?: string
}

export function getMe() {
  return api.get<{ id: string; email: string }>('users/me/')
}

export function changeEmail(payload: ChangeEmailPayload) {
  return api.post<ChangeEmailResult>('users/me/email/', payload)
}

export function confirmEmailChange(payload: { token: string }) {
  return api.post<{ email: string }>('users/me/email/confirm/', payload)
}

export async function exportData() {
  const response = await api.get<Blob>('users/me/export/', { responseType: 'blob' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(response.data)
  link.download = `bitjournal-export-${new Date().toISOString().slice(0, 10)}.json`
  link.click()
  URL.revokeObjectURL(link.href)
}

export function importData(file: File, password: string) {
  const body = new FormData()
  body.append('file', file)
  body.append('password', password)
  return api.post<void>('users/me/import/', body)
}
