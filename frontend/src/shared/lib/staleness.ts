// Minimal "dirty flag" registry for cached (keep-alive) views.

export type StaleKey = 'journal'

const stale = new Set<StaleKey>()

export function markStale(key: StaleKey) {
  stale.add(key)
}

export function consumeStale(key: StaleKey) {
  return stale.delete(key)
}
