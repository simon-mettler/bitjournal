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
