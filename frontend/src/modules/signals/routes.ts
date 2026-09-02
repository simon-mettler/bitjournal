import CategoryListView from '@/modules/signals/views/CategoryListView.vue'
import ManageSignalsView from '@/modules/signals/views/ManageSignalsView.vue'
import EditSignalView from '@/modules/signals/views/EditSignalView.vue'
import AddSignalView from '@/modules/signals/views/AddSignalView.vue'

const signalRoutes = [
  {
    path: '/categories',
    name: 'categories',
    component: CategoryListView,
  },
  {
    path: '/manage/signals',
    name: 'manage-signals',
    component: ManageSignalsView,
  },
  {
    path: '/manage/signals/add',
    name: 'signal-add',
    component: AddSignalView,
    meta: { hideNav: true },

  },
  {
    path: '/manage/signals/:id',
    name: 'signal-edit',
    component: EditSignalView,
    meta: { hideNav: true },
  },
]

export default signalRoutes
