import { createRouter, createWebHistory } from 'vue-router'

import UploadView  from '../views/UploadView.vue'
import ResultsView from '../views/ResultsView.vue'

const routes = [
  { path: '/',       name: 'Upload', component: UploadView },
  { path: '/results', name: 'Results', component: ResultsView },
]

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})
