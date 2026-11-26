import SignalStatsView from '@/modules/analytics/views/SignalStatsView.vue'
import DashboardView from '@/modules/analytics/views/DashboardView.vue'
import WidgetGalleryView from '@/modules/analytics/views/WidgetGalleryView.vue'
import AddWidgetView from '@/modules/analytics/views/AddWidgetView.vue'
import EditWidgetView from '@/modules/analytics/views/EditWidgetView.vue'
import { findWidgetDefinition } from '@/modules/analytics/widgetRegistry'
import type { RouteLocationNormalized } from 'vue-router'

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
    meta: { wide: true },
  },
  {
    path: '/manage/analytics-boards/:boardId/widgets/add',
    name: 'analytics-widget-gallery',
    component: WidgetGalleryView,
    meta: { hideNav: true },
  },
  {
    path: '/manage/analytics-boards/:boardId/widgets/add/:type',
    name: 'analytics-widget-add',
    component: AddWidgetView,
    meta: { hideNav: true },
    beforeEnter: (to: RouteLocationNormalized) =>
      findWidgetDefinition(to.params.type)
        ? true
        : { name: 'analytics-widget-gallery', params: { boardId: to.params.boardId } },
  },
  {
    path: '/manage/analytics-widgets/:id',
    name: 'analytics-widget-edit',
    component: EditWidgetView,
    meta: { hideNav: true },
  },
]

export default analyticsRoutes
