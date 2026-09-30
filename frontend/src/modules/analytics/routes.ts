import SignalStatsView from '@/modules/analytics/views/SignalStatsView.vue'
import DashboardView from '@/modules/analytics/views/DashboardView.vue'
import AddWidgetView from '@/modules/analytics/views/AddWidgetView.vue'
import EditWidgetView from '@/modules/analytics/views/EditWidgetView.vue'

const analyticsRoutes = [
  {
    path: '/signals/:id/stats',
    name: 'signal-stats',
    component: SignalStatsView,
    meta: { hideNav: true },
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardView,
  },
  {
    path: '/manage/analytics-boards/:boardId/widgets/add',
    name: 'analytics-widget-add',
    component: AddWidgetView,
    meta: { hideNav: true },
  },
  {
    path: '/manage/analytics-widgets/:id',
    name: 'analytics-widget-edit',
    component: EditWidgetView,
    meta: { hideNav: true },
  },
]

export default analyticsRoutes
