import { api } from '@/shared/api'
import type { InstanceConfig } from './types'

export function getInstanceConfig() {
  return api.get<InstanceConfig>('config/')
}
