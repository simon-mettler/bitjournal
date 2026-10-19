import RegisterView from './views/RegisterView.vue'
import LoginView from './views/LoginView.vue'
import ForgotPasswordView from './views/ForgotPasswordView.vue'
import ResetPasswordView from './views/ResetPasswordView.vue'

const authenticationRoutes = [
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: {
      public: true,
      hideNav: true,
    },
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: {
      public: true,
      hideNav: true,
    },
  },
  {
    path: '/forgot-password',
    name: 'forgot-password',
    component: ForgotPasswordView,
    meta: {
      public: true,
      hideNav: true,
    },
  },
  {
    path: '/reset-password/:uid/:token',
    name: 'reset-password',
    component: ResetPasswordView,
    meta: {
      public: true,
      hideNav: true,
    },
  },
]

export default authenticationRoutes
