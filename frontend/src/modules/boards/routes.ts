import BoardListView from "./views/BoardListView.vue"
import EditBoardView from "./views/EditBoardView.vue"

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
]

export default boardRoutes
