import { AxiosError } from 'axios'
import { createPinia, setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const post = vi.fn()
vi.mock('@/shared/api', () => ({ api: { post: (...args: unknown[]) => post(...args) } }))

import { useAuthStore } from './store'

function httpError(status: number) {
  return new AxiosError('failed', undefined, undefined, undefined, {
    status,
  } as AxiosError['response'])
}

describe('auth store refresh', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    post.mockReset()
    vi.useFakeTimers()
  })
  afterEach(() => vi.useRealTimers())

  it('dedupes concurrent refreshes into one request', async () => {
    post.mockResolvedValue({ data: { access: 'tok' } })
    const auth = useAuthStore()
    const [a, b] = await Promise.all([auth.refreshAccessToken(), auth.refreshAccessToken()])
    expect(a).toBe('tok')
    expect(b).toBe('tok')
    expect(post).toHaveBeenCalledTimes(1)
  })

  it('tryRefresh gives up immediately on 401', async () => {
    post.mockRejectedValue(httpError(401))
    const auth = useAuthStore()
    await auth.tryRefresh()
    expect(post).toHaveBeenCalledTimes(1)
    expect(auth.isAuthenticated).toBe(false)
    expect(auth.initialized).toBe(true)
  })

  it('tryRefresh retries transient failures and recovers', async () => {
    post.mockRejectedValueOnce(httpError(503)).mockResolvedValue({ data: { access: 'tok' } })
    const auth = useAuthStore()
    const done = auth.tryRefresh()
    await vi.runAllTimersAsync()
    await done
    expect(post).toHaveBeenCalledTimes(2)
    expect(auth.isAuthenticated).toBe(true)
  })
})
