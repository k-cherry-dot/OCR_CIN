import { createRouter, createWebHistory } from 'vue-router'
import UploadView from '../views/UploadView.vue'
import ResultsView from '../views/ResultsView.vue'

const routes = [
  {
    path: '/',
    name: 'Upload',
    component: UploadView
  },
  {
    path: '/results',
    name: 'Results',
    component: ResultsView,
    // we’ll pass the resultId via query string: /results?resultId=13
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
