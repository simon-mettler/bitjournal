import { api } from '@/shared/api'

export function requestPasswordReset(payload: { email: string }) {
  return api.post<void>('password-reset/', payload)
}

export function confirmPasswordReset(payload: {
  uid: string
  token: string
  new_password: string
}) {
  return api.post<void>('password-reset/confirm/', payload)
}
