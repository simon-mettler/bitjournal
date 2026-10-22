import AccountView from './views/AccountView.vue'
import AppSettingsView from './views/AppSettingsView.vue'
import ConfirmEmailView from './views/ConfirmEmailView.vue'

const accountRoutes = [
  {
    path: '/settings/app',
    name: 'app-settings',
    component: AppSettingsView,
  },
  {
    path: '/account',
    name: 'account',
    component: AccountView,
  },
  {
    // public: the link is opened from a mail, possibly on another device
    path: '/confirm-email/:token',
    name: 'confirm-email',
    component: ConfirmEmailView,
    meta: { public: true, hideNav: true },
  },
]

export default accountRoutes
