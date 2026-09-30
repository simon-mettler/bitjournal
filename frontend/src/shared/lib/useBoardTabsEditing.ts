import { computed, ref, type Ref } from 'vue'
import { useToast } from '@/shared/lib/useToast'

interface TabBoard {
  id: string
  name: string
}

interface Options<B extends TabBoard> {
  boards: Ref<B[]>
  select: (id: string | null) => void
  create: (name: string) => Promise<B>
  rename: (board: B, name: string) => Promise<unknown>
  remove: (board: B) => Promise<unknown>
  reorder: (ids: string[]) => Promise<unknown>
  reload: () => Promise<unknown>
}

export function useBoardTabsEditing<B extends TabBoard>(options: Options<B>) {
  const { boards, select } = options
  const toaster = useToast()

  // run one after another boardwrite to prevent overwrites
  let writeQueue: Promise<unknown> = Promise.resolve()
  function enqueue<T>(task: () => Promise<T>): Promise<T> {
    const run = writeQueue.then(task)
    writeQueue = run.catch(() => undefined)
    return run
  }

  const nameDialogOpen = ref(false)
  const nameDialogMode = ref<'add' | 'rename'>('add')
  const nameDialogBusy = ref(false)
  const renameTargetId = ref<string | null>(null)
  const renameTarget = computed(() => boards.value.find((b) => b.id === renameTargetId.value))

  function askAddBoard() {
    nameDialogMode.value = 'add'
    renameTargetId.value = null
    nameDialogOpen.value = true
  }

  function askRenameBoard(id: string) {
    nameDialogMode.value = 'rename'
    renameTargetId.value = id
    nameDialogOpen.value = true
  }

  async function submitName(name: string) {
    nameDialogBusy.value = true
    try {
      const target = renameTarget.value
      if (nameDialogMode.value === 'rename' && target) {
        await enqueue(() => options.rename(target, name))
        target.name = name
      } else {
        const board = await enqueue(() => options.create(name))
        boards.value.push(board)
        select(board.id)
      }
      nameDialogOpen.value = false
    } catch {
      const action = nameDialogMode.value === 'add' ? 'create' : 'rename'
      toaster.toast({ description: `Could not ${action} board.`, variant: 'danger' })
    } finally {
      nameDialogBusy.value = false
    }
  }

  function onTabsReorder(ids: string[]) {
    const byId = new Map(boards.value.map((b) => [b.id, b]))
    boards.value = ids.map((id) => byId.get(id)).filter((b): b is B => !!b)
    enqueue(() => options.reorder(ids)).catch(() => {
      toaster.toast({ description: 'Could not save new order.', variant: 'danger' })
      options.reload()
    })
  }

  const boardToDelete = ref<B | null>(null)
  const deleteBoardOpen = ref(false)

  function askDeleteBoard(id: string) {
    boardToDelete.value = boards.value.find((b) => b.id === id) ?? null
    deleteBoardOpen.value = true
  }

  async function confirmDeleteBoard() {
    const board = boardToDelete.value
    if (!board) return
    try {
      await enqueue(() => options.remove(board))
      const index = boards.value.findIndex((b) => b.id === board.id)
      boards.value = boards.value.filter((b) => b.id !== board.id)
      select(boards.value[Math.min(index, boards.value.length - 1)]?.id ?? null)
      toaster.toast({ description: `Deleted "${board.name}".`, variant: 'success' })
    } catch {
      toaster.toast({ description: 'Could not delete board.', variant: 'danger' })
    }
  }

  return {
    enqueue,
    nameDialogOpen,
    nameDialogMode,
    nameDialogBusy,
    renameTarget,
    askAddBoard,
    askRenameBoard,
    submitName,
    onTabsReorder,
    boardToDelete,
    deleteBoardOpen,
    askDeleteBoard,
    confirmDeleteBoard,
  }
}
