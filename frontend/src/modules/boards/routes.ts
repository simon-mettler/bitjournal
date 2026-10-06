import BoardTrackView from './views/BoardTrackView.vue'

const boardRoutes = [
  // boards are managed inline on the track view now
  { path: '/manage/boards', redirect: { name: 'track' } },
  { path: '/manage/boards/:id', redirect: { name: 'track' } },
  {
    path: '/track',
    name: 'track',
    component: BoardTrackView,
  },
  {
    path: '/track/:eventId?',
    name: 'track',
    component: BoardTrackView,
  },
]

export default boardRoutes
