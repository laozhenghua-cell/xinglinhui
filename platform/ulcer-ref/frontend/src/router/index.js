import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/patients',
    name: 'Patients',
    component: () => import('../views/Patients.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/ulcers/new',
    name: 'NewConsultation',
    component: () => import('../views/ulcers/NewConsultation.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/ulcers/:id',
    name: 'ConsultationDetail',
    component: () => import('../views/ulcers/ConsultationDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/expert/queue',
    name: 'ExpertQueue',
    component: () => import('../views/expert/Queue.vue'),
    meta: { requiresAuth: true, role: 'expert' }
  },
  {
    path: '/knowledge',
    name: 'Knowledge',
    component: () => import('../views/Knowledge.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.token) {
    next('/login')
  } else if (to.meta.role && authStore.user?.role !== to.meta.role) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
