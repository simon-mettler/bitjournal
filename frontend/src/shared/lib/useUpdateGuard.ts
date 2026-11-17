import { onScopeDispose, watch, type Ref } from 'vue'

// Components holding unsaved input register here so an app update never reloads
// the page underneath them (see appUpdate.ts).
let blockers = 0

export function isUpdateBlocked() {
  return blockers > 0
}

/** Blocks silent app updates while `active` is true. */
export function useUpdateGuard(active: Readonly<Ref<boolean>>) {
  let held = false
  const sync = (value: boolean) => {
    if (value === held) return
    held = value
    blockers += value ? 1 : -1
  }

  watch(active, sync, { immediate: true })
  onScopeDispose(() => sync(false))
}
