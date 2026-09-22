import SignalStatsView from '@/modules/analytics/views/SignalStatsView.vue'

const analyticsRoutes = [
  {
    path: '/signals/:id/stats',
    name: 'signal-stats',
    component: SignalStatsView,
    meta: { hideNav: true },
  },
]

export default analyticsRoutes
