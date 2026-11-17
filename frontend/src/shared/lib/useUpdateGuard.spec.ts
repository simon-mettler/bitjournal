import { effectScope, nextTick, ref } from 'vue'
import { describe, expect, it } from 'vitest'
import { isUpdateBlocked, useUpdateGuard } from './useUpdateGuard'

describe('useUpdateGuard', () => {
  it('blocks while active and releases when inactive or disposed', async () => {
    const active = ref(false)
    const scope = effectScope()
    scope.run(() => useUpdateGuard(active))
    expect(isUpdateBlocked()).toBe(false)

    active.value = true
    await nextTick()
    expect(isUpdateBlocked()).toBe(true)

    active.value = false
    await nextTick()
    expect(isUpdateBlocked()).toBe(false)

    active.value = true
    await nextTick()
    scope.stop()
    expect(isUpdateBlocked()).toBe(false)
  })

  it('counts several guards independently', async () => {
    const a = ref(true)
    const b = ref(true)
    const scope = effectScope()
    scope.run(() => {
      useUpdateGuard(a)
      useUpdateGuard(b)
    })
    a.value = false
    await nextTick()
    expect(isUpdateBlocked()).toBe(true)
    scope.stop()
    expect(isUpdateBlocked()).toBe(false)
  })
})
