import { reactive } from 'vue'
import type { Rule } from '@/shared/lib/validators'

export function useFormValidation(
  fields: Record<string, () => unknown>,
  rules: Record<string, Rule[]>,
) {
  const errors = reactive<Record<string, string>>({})

  function validateField(key: string) {
    for (const rule of rules[key] ?? []) {
      const result = rule(fields[key]())
      if (result !== true) {
        errors[key] = result
        return false
      }
    }
    delete errors[key]
    return true
  }

  function validateAll() {
    return Object.keys(rules).reduce((ok, key) => validateField(key) && ok, true)
  }

  function clear(key?: string) {
    if (key) delete errors[key]
    else Object.keys(errors).forEach((k) => delete errors[k])
  }

  return { errors, validateField, validateAll, clear }
}
