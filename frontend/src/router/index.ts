import { createRouter, createWebHistory } from 'vue-router'
import authenticationRoutes from '@/modules/authentication/routes'
import signalRoutes from '@/modules/signals/routes'
import boardRoutes from '@/modules/boards/routes'
import journalRoutes from '@/modules/journal/routes'
import analyticsRoutes from '@/modules/analytics/routes'

import { useAuthStore } from '@/modules/authentication/store'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: { name: 'track' } },

    ...authenticationRoutes,
    ...signalRoutes,
    ...boardRoutes,
    ...journalRoutes,
    ...analyticsRoutes,
  ],
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  if (!auth.initialized) {
    await auth.tryRefresh()
  }

  if (to.matched.some(record => record.meta.public)) {
    next()
  } else if (auth.isAuthenticated) {
    next()
  } else {
    next('/login')
  }
})
export default router
