import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '工作台' }
      },
      {
        path: 'patients',
        name: 'Patients',
        component: () => import('@/views/Patients.vue'),
        meta: { title: '患者管理' }
      },
      {
        path: 'patients/:id',
        name: 'PatientDetail',
        component: () => import('@/views/PatientDetail.vue'),
        meta: { title: '患者详情' }
      },
      {
        path: 'consultations/new',
        name: 'ConsultationNew',
        component: () => import('@/views/ConsultationNew.vue'),
        meta: { title: '新建就诊' }
      },
      {
        path: 'consultations/:id',
        name: 'ConsultationDetail',
        component: () => import('@/views/ConsultationNew.vue'),
        meta: { title: '就诊详情' }
      },
      {
        path: 'diagnosis',
        name: 'Diagnosis',
        component: () => import('@/views/Diagnosis.vue'),
        meta: { title: '智能辨证' }
      },
      {
        path: 'diagnosis/image',
        name: 'ImageDiagnosis',
        component: () => import('@/views/diagnosis/ImageDiagnosis.vue'),
        meta: { title: '影像诊断' }
      },
      {
        path: 'knowledge',
        name: 'Knowledge',
        component: () => import('@/views/Knowledge.vue'),
        meta: { title: '知识库' }
      },
      {
        path: 'knowledge/formulas/:id',
        name: 'FormulaDetail',
        component: () => import('@/views/Knowledge.vue'),
        meta: { title: '方剂详情' }
      },
      {
        path: 'billing',
        name: 'Billing',
        component: () => import('@/views/billing/BillingMain.vue'),
        meta: { title: '收费管理' }
      },
      {
        path: 'inventory',
        name: 'Inventory',
        component: () => import('@/views/inventory/InventoryMain.vue'),
        meta: { title: '库存管理' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '系统设置' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (!to.meta.public && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
