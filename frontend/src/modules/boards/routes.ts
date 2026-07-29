import BoardListView from "./views/BoardListView.vue"
import EditBoardView from "./views/EditBoardView.vue"
import BoardTrackView from "./views/BoardTrackView.vue"

const boardRoutes = [
  {
    path: '/manage/boards',
    name: 'manage-boards',
    component: BoardListView,
  },
  {
    path: '/manage/boards/:id',
    name: 'board-edit',
    component: EditBoardView,
  },
  {
    path: '/track',
    name: 'track',
    component: BoardTrackView,
  },
]

export default boardRoutes
