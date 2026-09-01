import { onMounted, onUnmounted } from 'vue'

export function useViewportHeight() {
  const update = () => {
    const vv = window.visualViewport

    const height = vv?.height ?? window.innerHeight
    const offsetTop = vv?.offsetTop ?? 0

    document.documentElement.style.setProperty(
      '--visual-viewport-height',
      `${height}px`,
    )

    document.documentElement.style.setProperty(
      '--visual-viewport-offset-top',
      `${offsetTop}px`,
    )
  }

  onMounted(() => {
    update()
    window.visualViewport?.addEventListener('resize', update)
    window.visualViewport?.addEventListener('scroll', update)
    window.addEventListener('resize', update)
  })

  onUnmounted(() => {
    window.visualViewport?.removeEventListener('resize', update)
    window.visualViewport?.removeEventListener('scroll', update)
    window.removeEventListener('resize', update)
  })
}
