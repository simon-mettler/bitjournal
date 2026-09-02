import EditBoardView from "./views/EditBoardView.vue"
import BoardTrackView from "./views/BoardTrackView.vue"
import ManageBoardsView from "./views/ManageBoardsView.vue"

const boardRoutes = [
  {
    path: '/manage/boards',
    name: 'manage-boards',
    component: ManageBoardsView,
  },
  {
    path: '/manage/boards/:id',
    name: 'board-edit',
    component: EditBoardView,
    meta: { hideNav: true },
  },
  {
    path: '/track',
    name: 'track',
    component: BoardTrackView,
  },
]

export default boardRoutes
