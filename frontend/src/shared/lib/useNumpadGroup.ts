import { ref, computed, provide, inject, type InjectionKey, type Ref } from 'vue'

export interface NumpadField {
  id: string
  value: Ref<number | undefined>
  min?: number
  max?: number
  maxLength?: number // e.g. 2 for a "59" style field
  label?: string
}

export interface NumpadGroup {
  enabled: boolean
  activeId: Ref<string | null>
  activeLabel: Ref<string | undefined>
  register: (field: NumpadField) => void
  unregister: (id: string) => void
  focus: (id: string) => void
  next: () => void
  prev: () => void
  enterDigit: (digit: number) => void
  enterDot: () => void
  toggleSign: () => void
  backspace: () => void
}

const NumpadGroupKey: InjectionKey<NumpadGroup> = Symbol('numpad-group')

export function provideNumpadGroup(enabled: boolean): NumpadGroup {
  const fields: NumpadField[] = []
  const activeId = ref<string | null>(null)
  const activeLabel = computed(() => activeField()?.label)

  let freshEntry = true
  // String representation of what's being typed for the active field.
  // Kept separate from field.value so partial input like "-" or "1." isn't lost to parseFloat.
  let buffer = ''

  function activeField(): NumpadField | undefined {
    return fields.find(f => f.id === activeId.value)
  }

  function currentIndex() {
    return fields.findIndex(f => f.id === activeId.value)
  }

  function register(field: NumpadField) {
    fields.push(field)
    if (activeId.value === null) {
      activeId.value = field.id
    }
  }

  function unregister(id: string) {
    const i = fields.findIndex(f => f.id === id)
    if (i !== -1) fields.splice(i, 1)
    if (activeId.value === id) {
      activeId.value = fields[0]?.id ?? null
    }
  }

  function focus(id: string) {
    activeId.value = id
    freshEntry = true
    buffer = ''
  }

  function next() {
    const i = currentIndex()
    if (i === -1 || fields.length === 0) return
    focus(fields[(i + 1) % fields.length].id)
  }

  function prev() {
    const i = currentIndex()
    if (i === -1 || fields.length === 0) return
    focus(fields[(i - 1 + fields.length) % fields.length].id)
  }

  function commitBuffer(field: NumpadField) {
    let n = parseFloat(buffer)
    if (Number.isNaN(n)) n = 0
    if (field.max !== undefined && n > field.max) n = field.max
    if (field.min !== undefined && n < field.min) n = field.min
    field.value.value = n
  }

  function withActiveField(fn: (field: NumpadField) => void) {
    const field = activeField()
    if (field) fn(field)
  }

  function enterDigit(digit: number) {
    withActiveField(field => {
      if (freshEntry) {
        buffer = ''
        freshEntry = false
      }

      // limit the entered number to 2 decimal places
      if (buffer.includes('.') && buffer.split('.')[1].length >= 2) return

      const hasDecimal = buffer.includes('.')
      const digitsSoFar = buffer.replace('-', '').length
      if (field.maxLength && !hasDecimal && digitsSoFar >= field.maxLength) {
        buffer = ''
      }

      buffer += String(digit)
      commitBuffer(field)

      const nowFull = field.maxLength && !buffer.includes('.') &&
        buffer.replace('-', '').length >= field.maxLength
      if (nowFull && fields.length > 1) next()
    })
  }

  function enterDot() {
    withActiveField(field => {
      if (buffer.includes('.')) return

      if (freshEntry) {
        buffer = '0'
        freshEntry = false
      }

      buffer += '.'
      commitBuffer(field)
    })
  }

  function toggleSign() {
    withActiveField(field => {
      if (freshEntry) {
        buffer = String(field.value.value ?? 0)
        freshEntry = false
      }

      buffer = buffer.startsWith('-') ? buffer.slice(1) : '-' + buffer
      commitBuffer(field)
    })
  }

  function backspace() {
    withActiveField(field => {
      if (freshEntry || buffer === '') {
        field.value.value = field.min ?? 0
        buffer = ''
        freshEntry = true
        return
      }

      buffer = buffer.slice(0, -1)
      if (buffer === '' || buffer === '-') {
        field.value.value = field.min ?? 0
      } else {
        commitBuffer(field)
      }
    })
  }

  const group: NumpadGroup = {
    enabled,
    activeId,
    activeLabel,
    register,
    unregister,
    focus,
    next,
    prev,
    enterDigit,
    enterDot,
    toggleSign,
    backspace,
  }

  provide(NumpadGroupKey, group)
  return group
}

export function useNumpadGroup(): NumpadGroup | null {
  return inject(NumpadGroupKey, null)
}
