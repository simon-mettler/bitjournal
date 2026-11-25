import { useMediaQuery } from '@vueuse/core'

/**
 * Layout breakpoints. Keep in sync with the `@media` queries in CSS
 */
export const BREAKPOINT_TABLET = 768
export const BREAKPOINT_DESKTOP = 1024

export function useIsTabletUp() {
  return useMediaQuery(`(min-width: ${BREAKPOINT_TABLET}px)`)
}

export function useIsDesktopUp() {
  return useMediaQuery(`(min-width: ${BREAKPOINT_DESKTOP}px)`)
}
