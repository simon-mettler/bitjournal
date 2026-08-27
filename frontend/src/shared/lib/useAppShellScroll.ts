import { inject, type InjectionKey } from 'vue'
import type { UseScrollReturn } from '@vueuse/core'

export const SCROLL_KEY: InjectionKey<UseScrollReturn> = Symbol('app-shell-scroll')

export function useAppShellScroll() {
  const scroll = inject(SCROLL_KEY)
  if (!scroll) {
    throw new Error('useAppShellScroll() must be used inside AppShell')
  }
  return scroll
}
