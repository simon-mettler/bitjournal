import RegisterView from './views/RegisterView.vue'
import LoginView from './views/LoginView.vue'

const authenticationRoutes = [
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: {
      public: true,
    }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: {
      public: true,
    }
  },
]

export default authenticationRoutes
