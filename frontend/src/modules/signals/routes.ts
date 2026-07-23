import CategoryListView from '@/modules/signals/views/CategoryListView.vue'
import ManageSignalsView from '@/modules/signals/views/ManageSignalsView.vue'

const signalRoutes = [
  {
    path: '/categories',
    name: 'categories',
    component: CategoryListView,
  },
  {
    path: '/manage/signals',
    name: 'managesignals',
    component: ManageSignalsView
  }
]

export default signalRoutes
