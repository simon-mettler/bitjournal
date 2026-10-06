import { nextTick, watch, type Ref } from 'vue'
import { useSortable } from '@vueuse/integrations/useSortable'
import type { UseSortableOptions } from '@vueuse/integrations/useSortable'

type SortableListOptions = Omit<UseSortableOptions, 'onEnd' | 'disabled'> & {
  enabled?: Ref<boolean>
  onSorted: () => void
}

// Wait for nextTick, so onSorted can read reordered list.
export function useSortableList<T>(
  el: Ref<HTMLElement | null>,
  list: Ref<T[]>,
  { enabled, onSorted, ...options }: SortableListOptions,
) {
  const sortable = useSortable(el, list, {
    animation: 150,
    watchElement: true, // the element may be rendered conditionally
    disabled: enabled ? !enabled.value : false,
    ...options,
    onEnd: () => {
      void nextTick().then(onSorted)
    },
  })

  if (enabled) watch(enabled, (on) => sortable.option('disabled', !on))
  return sortable
}
