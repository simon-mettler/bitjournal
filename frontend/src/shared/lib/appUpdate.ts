import { readonly, ref } from 'vue'
import { registerSW } from 'virtual:pwa-register'
import type { Router } from 'vue-router'
import { waitForRefresh } from '@/modules/authentication/store'
import { isUpdateBlocked } from '@/shared/lib/useUpdateGuard'

// Silent app updates for the installed PWA.
// Detection does not depend on service worker events alone: /version.json is probed
// on launch, resume, reconnect and on a timer, and also ask the browser to re-check sw.js.
// Applying is silent but only at safe points, never over unsaved input.

const CHECK_THROTTLE_MS = 30_000
const CHECK_INTERVAL_MS = 15 * 60_000
const RESUME_AFTER_HIDDEN_MS = 30_000
const LAUNCH_WINDOW_MS = 8_000
const RELOAD_FALLBACK_MS = 2_500
const LOOP_GUARD_MS = 60_000
const LOOP_GUARD_KEY = 'bitjournal-update-applied-at'

export type SwState = 'unsupported' | 'none' | 'installing' | 'waiting' | 'active'
export type CheckResult = 'current' | 'updating' | 'error'

const updateAvailable = ref(false)
const lastCheckedAt = ref<number | null>(null)
const checking = ref(false)
const swState = ref<SwState>('unsupported')

const launchedAt = Date.now()
let interacted = false
let hiddenAt: number | null = null
let applying = false
let lastCheckStarted = 0
let registration: ServiceWorkerRegistration | undefined
let updateSW: ((reloadPage?: boolean) => Promise<void>) | undefined
let router: Router | undefined

function readGuard() {
  try {
    return Number(sessionStorage.getItem(LOOP_GUARD_KEY)) || 0
  } catch {
    return 0
  }
}

function writeGuard() {
  try {
    sessionStorage.setItem(LOOP_GUARD_KEY, String(Date.now()))
  } catch {}
}

function refreshSwState() {
  if (!('serviceWorker' in navigator)) swState.value = 'unsupported'
  else if (!registration) swState.value = 'none'
  else if (registration.waiting) swState.value = 'waiting'
  else if (registration.installing) swState.value = 'installing'
  else swState.value = registration.active ? 'active' : 'none'
}

async function fetchLatestBuildId(): Promise<string | null> {
  try {
    const response = await fetch(`/version.json?t=${Date.now()}`, { cache: 'no-store' })
    if (!response.ok) return null
    const data = (await response.json()) as { buildId?: unknown }
    return typeof data.buildId === 'string' ? data.buildId : null
  } catch {
    return null
  }
}

function markUpdateAvailable() {
  updateAvailable.value = true
  refreshSwState()
}

/** Probes the server for a newer build. Returns null when the probe failed. */
async function runCheck(): Promise<boolean | null> {
  lastCheckStarted = Date.now()
  checking.value = true
  try {
    const [latest] = await Promise.all([
      fetchLatestBuildId(),
      // Lets the browser install a new service worker so it is ready to activate.
      registration?.update().catch(() => {}),
    ])
    lastCheckedAt.value = Date.now()
    if (latest !== null && latest !== __BUILD_ID__) markUpdateAvailable()
    refreshSwState()
    return latest === null ? null : updateAvailable.value
  } finally {
    checking.value = false
  }
}

function checkThrottled() {
  if (Date.now() - lastCheckStarted < CHECK_THROTTLE_MS) return Promise.resolve(null)
  return runCheck()
}

function isBusy() {
  return isUpdateBlocked() || !!router?.currentRoute.value.meta.hideNav
}

async function hardRefresh() {
  // Only proceed when the network just proved reachable; otherwise retry later.
  try {
    const probe = await fetch('/', { cache: 'no-store' })
    if (!probe.ok) throw new Error('unreachable')
  } catch {
    applying = false
    return
  }
  try {
    const registrations = await navigator.serviceWorker?.getRegistrations()
    await Promise.all((registrations ?? []).map((r) => r.unregister()))
  } catch {
    // reload regardless
  }
  window.location.reload()
}

function waitForInstall(timeoutMs = 6_000): Promise<void> {
  const worker = registration?.installing
  if (!worker || worker.state === 'installed') return Promise.resolve()
  return new Promise((resolve) => {
    const done = () => {
      worker.removeEventListener('statechange', onChange)
      clearTimeout(timer)
      resolve()
    }
    const onChange = () => {
      if (worker.state === 'installed' || worker.state === 'redundant') done()
    }
    const timer = setTimeout(done, timeoutMs)
    worker.addEventListener('statechange', onChange)
  })
}

async function applyUpdate(force = false) {
  if (applying || !updateAvailable.value) return
  if (!force && Date.now() - readGuard() < LOOP_GUARD_MS) return
  applying = true
  await waitForRefresh()
  writeGuard()

  await waitForInstall()
  refreshSwState()
  if (registration?.waiting && updateSW) {
    setTimeout(() => window.location.reload(), RELOAD_FALLBACK_MS)
    void updateSW(true)
  } else {
    await hardRefresh()
  }
}

type SafePoint = 'launch' | 'resume' | 'navigation'

function safePoint(point: SafePoint) {
  if (!updateAvailable.value || applying || isBusy()) return
  if (point === 'launch' && (interacted || Date.now() - launchedAt > LAUNCH_WINDOW_MS)) return
  void applyUpdate()
}

/** User-initiated check (settings). Applies immediately when something newer exists. */
export async function checkNow(): Promise<CheckResult> {
  const result = await runCheck()
  if (result === null) return 'error'
  if (!result) return 'current'
  void applyUpdate(true)
  return 'updating'
}

export function useAppUpdate() {
  return {
    buildId: __BUILD_ID__,
    version: __APP_VERSION__,
    updateAvailable: readonly(updateAvailable),
    lastCheckedAt: readonly(lastCheckedAt),
    checking: readonly(checking),
    swState: readonly(swState),
    checkNow,
  }
}

export function installAppUpdate(appRouter: Router) {
  router = appRouter

  updateSW = registerSW({
    immediate: true,
    onNeedRefresh: markUpdateAvailable,
    onRegisteredSW(_url, reg) {
      registration = reg
      refreshSwState()
    },
  })

  const markInteracted = () => {
    interacted = true
  }
  window.addEventListener('pointerdown', markInteracted, { once: true, capture: true })
  window.addEventListener('keydown', markInteracted, { once: true, capture: true })

  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
      hiddenAt = Date.now()
      return
    }
    const wasAway = hiddenAt !== null && Date.now() - hiddenAt >= RESUME_AFTER_HIDDEN_MS
    hiddenAt = null
    void checkThrottled().then(() => {
      if (wasAway) safePoint('resume')
    })
  })
  // iOS restores suspended PWAs from the back/forward cache without visibilitychange
  window.addEventListener('pageshow', (event) => {
    if (event.persisted) void checkThrottled().then(() => safePoint('resume'))
  })
  window.addEventListener('online', () => void checkThrottled())
  setInterval(() => {
    if (document.visibilityState === 'visible') void checkThrottled()
  }, CHECK_INTERVAL_MS)

  // Apply on the next navigation, once nothing is being edited.
  router.afterEach((_to, from) => {
    if (from.matched.length === 0) return
    safePoint('navigation')
  })

  window.addEventListener('vite:preloadError', (event) => {
    event.preventDefault()
    if (Date.now() - readGuard() < LOOP_GUARD_MS) return
    writeGuard()
    window.location.reload()
  })

  void runCheck().then(() => safePoint('launch'))
}
