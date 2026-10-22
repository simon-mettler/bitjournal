import { computed, ref, watchEffect } from 'vue'
import { usePreferredDark } from '@vueuse/core'

export type ThemeMode = 'system' | 'light' | 'dark'

const STORAGE_KEY = 'bitjournal-theme'

function readStoredMode(): ThemeMode {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored === 'light' || stored === 'dark') return stored
  } catch {}
  return 'system'
}

const mode = ref<ThemeMode>(readStoredMode())
const prefersDark = usePreferredDark()
const resolvedTheme = computed<'light' | 'dark'>(() =>
  mode.value === 'system' ? (prefersDark.value ? 'dark' : 'light') : mode.value,
)

function setMode(next: ThemeMode) {
  mode.value = next
  try {
    if (next === 'system') localStorage.removeItem(STORAGE_KEY)
    else localStorage.setItem(STORAGE_KEY, next)
  } catch {}
}

export function initTheme() {
  watchEffect(() => {
    document.documentElement.dataset.theme = resolvedTheme.value
  })
}

export function useTheme() {
  return { mode, resolvedTheme, setMode }
}
