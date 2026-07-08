import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AboutView from '@/views/AboutView.vue'
import authenticationRoutes from '@/modules/authentication/routes'

import { useAuthStore } from '@/modules/authentication/store'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      component: AboutView
    },

    ...authenticationRoutes,
  ],
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.matched.some(record => record.meta.public)) {
    next()
  } else {
    if (auth.isAuthenticated) {
      next()
    } else {
      next('/login')
    }
  }
})
export default router
