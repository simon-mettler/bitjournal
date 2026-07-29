import { api } from '@/shared/api'
import type { Board } from './types'

export type CreateBoardPayload = Pick<Board, 'name'>

export type UpdateBoardPayload = {
  name: Board['name']
  signal_ids: string[]
}

export type ReorderBoardsPayload = {
  board_ids: Board['id'][]
}

export function getBoards() {
  return api.get<Board[]>('boards/')
}

export function getBoard(id: string) {
  return api.get<Board>(`boards/${id}/`)
}

export function createBoard(payload: CreateBoardPayload) {
  return api.post<Board>('boards/', payload)
}

export function updateBoard(id: string, payload: UpdateBoardPayload) {
  return api.put<Board>(`boards/${id}/`, payload)
}

export function deleteBoard(id: string) {
  return api.delete(`boards/${id}/`)
}

export function reorderBoards(payload: ReorderBoardsPayload) {
  return api.post<Board[]>('boards/reorder/', payload)
}
