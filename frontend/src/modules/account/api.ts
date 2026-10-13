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
