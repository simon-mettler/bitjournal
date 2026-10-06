export interface InstanceConfig {
  registration_enabled: boolean
  email_enabled: boolean
  notice: string
  extra: Record<string, unknown>
}
