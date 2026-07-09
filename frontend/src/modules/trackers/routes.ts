import CategoryListView from '@/modules/trackers/views/CategoryListView.vue'

const trackerRoutes = [
  {
    path: '/categories',
    name: 'categories',
    component: CategoryListView,
    meta: {
      public: true,
    }
  },
]

export default trackerRoutes
