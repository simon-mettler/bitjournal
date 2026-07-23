import { ref } from 'vue'

export interface ToastOptions {
  title?: string
  description: string
  variant?: 'default' | 'success' | 'error'
  duration?: number
  actionLabel?: string
  actionAltText?: string
  onAction?: () => void
}

export interface ToastItem extends ToastOptions {
  id: number
}

const toasts = ref<ToastItem[]>([])
let nextId = 0

export function useToast() {
  function toast(options: ToastOptions) {
    const id = nextId++
    toasts.value.push({ variant: 'default', ...options, id })
    return id
  }

  function dismiss(id: number) {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  return { toasts, toast, dismiss }
}
