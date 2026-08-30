import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // ============ 统一外壳 · 杏林汇智能诊疗系统 ============
  {
    path: '/',
    component: () => import('@/views/AppShell.vue'),
    children: [
      { path: '', name: 'Dashboard', component: () => import('@/views/Dashboard.vue'),
        meta: { title: '工作台', module: 'dashboard', public: true } },
      // ---- 统一门诊 ----
      { path: 'clinic', name: 'ClinicHome', component: () => import('@/views/clinic/ClinicHome.vue'),
        meta: { title: '门诊诊疗', module: 'clinic', public: true } },
      { path: 'clinic/new', name: 'ClinicNew', component: () => import('@/views/clinic/ClinicNew.vue'),
        meta: { title: '新建就诊', module: 'clinic', public: true } },
      { path: 'clinic/:id', name: 'ClinicDetail', component: () => import('@/views/clinic/ClinicDetail.vue'),
        meta: { title: '就诊详情', module: 'clinic', public: true } },
      // ---- 病种辨证(专科库:疮疡/痔漏/儿科/丹药) ----
      { path: 'dx', name: 'DxCenter', component: () => import('@/views/dx/DxCenter.vue'),
        meta: { title: '病种辨证', module: 'dx', public: true } },
      // ---- 六体系辨证(八纲/六经/卫气营血/脏腑/三焦/经络) ----
      { path: 'systems', name: 'SystemsDx', component: () => import('@/views/dx/SystemsDx.vue'),
        meta: { title: '六体系辨证', module: 'dx', public: true } },
      // ---- 词库管理 ----
      { path: 'admin', name: 'SynonymAdmin', component: () => import('@/views/admin/SynonymAdmin.vue'),
        meta: { title: '词库管理', module: 'admin', public: true } },
      // ---- 知识总库 ----
      {
        path: 'kb',
        component: () => import('@/views/kb/KbLayout.vue'),
        redirect: 'kb',
        meta: { module: 'kb' },
        children: [
          { path: '', name: 'KbHome', component: () => import('@/views/kb/KbHome.vue'),
            meta: { title: '知识总库', module: 'kb', public: true } },
          { path: 'search', name: 'KbSearch', component: () => import('@/views/kb/KbSearch.vue'),
            meta: { title: '总库检索', module: 'kb', public: true } },
          { path: ':type', name: 'KbList', component: () => import('@/views/kb/KbList.vue'),
            meta: { title: '总库列表', module: 'kb', public: true } },
          { path: ':type/:id', name: 'KbDetail', component: () => import('@/views/kb/KbDetail.vue'),
            meta: { title: '总库详情', module: 'kb', public: true } }
        ]
      },
      // ---- 学苑 ----
      { path: 'learn', name: 'LearnHome', component: () => import('@/views/learn/LearnHome.vue'),
        meta: { title: '学苑', module: 'learn', public: true } },
      { path: 'learn/path/:id', name: 'LearnPath', component: () => import('@/views/learn/LearnPath.vue'),
        meta: { title: '学习路径', module: 'learn', public: true } },
      { path: 'learn/quiz', name: 'LearnQuiz', component: () => import('@/views/learn/Quiz.vue'),
        meta: { title: '自测练习', module: 'learn', public: true } },
      { path: 'learn/ask', name: 'LearnAsk', component: () => import('@/views/learn/Ask.vue'),
        meta: { title: 'AI 助教', module: 'learn', public: true } },
      // ---- 使用统计 ----
      { path: 'stats', name: 'Stats', component: () => import('@/views/stats/StatsView.vue'),
        meta: { title: '使用统计', module: 'stats', public: true } }
    ]
  },

// ============ 肛肠痔漏模块（原华夏痔瘘诊疗系统） ============
  {
    path: '/anorectal',
    component: () => import('@/views/Layout.vue'),
    redirect: '/anorectal/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'AnorectalDashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '工作台', module: 'anorectal' }
      },
      {
        path: 'patients',
        name: 'Patients',
        component: () => import('@/views/Patients.vue'),
        meta: { title: '患者管理', module: 'anorectal' }
      },
      {
        path: 'patients/:id',
        name: 'PatientDetail',
        component: () => import('@/views/PatientDetail.vue'),
        meta: { title: '患者详情', module: 'anorectal' }
      },
      {
        path: 'consultations/new',
        name: 'ConsultationNew',
        component: () => import('@/views/ConsultationNew.vue'),
        meta: { title: '新建就诊', module: 'anorectal' }
      },
      {
        path: 'consultations/:id',
        name: 'ConsultationDetail',
        component: () => import('@/views/ConsultationNew.vue'),
        meta: { title: '就诊详情', module: 'anorectal' }
      },
      {
        path: 'diagnosis',
        name: 'Diagnosis',
        component: () => import('@/views/Diagnosis.vue'),
        meta: { title: '智能辨证', module: 'anorectal' }
      },
      {
        path: 'diagnosis/image',
        name: 'ImageDiagnosis',
        component: () => import('@/views/diagnosis/ImageDiagnosis.vue'),
        meta: { title: '影像诊断', module: 'anorectal' }
      },
      {
        path: 'knowledge',
        name: 'Knowledge',
        component: () => import('@/views/Knowledge.vue'),
        meta: { title: '知识库', module: 'anorectal' }
      },
      {
        path: 'knowledge/formulas/:id',
        name: 'FormulaDetail',
        component: () => import('@/views/Knowledge.vue'),
        meta: { title: '方剂详情', module: 'anorectal' }
      },
      {
        path: 'billing',
        name: 'Billing',
        component: () => import('@/views/billing/BillingMain.vue'),
        meta: { title: '收费管理', module: 'anorectal' }
      },
      {
        path: 'inventory',
        name: 'Inventory',
        component: () => import('@/views/inventory/InventoryMain.vue'),
        meta: { title: '库存管理', module: 'anorectal' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '系统设置', module: 'anorectal' }
      }
    ]
  },
// ============ 儿科模块（程氏家传儿科秘要） ============
  {
    path: '/pediatrics',
    component: () => import('@/modules/pediatrics/PediatricsLayout.vue'),
    redirect: '/pediatrics',
    children: [
      {
        path: '',
        name: 'PediatricsHome',
        component: () => import('@/modules/pediatrics/views/Home.vue'),
        meta: { title: '首页', module: 'pediatrics' }
      },
      {
        path: 'bianzheng',
        name: 'PediatricsBianzheng',
        component: () => import('@/modules/pediatrics/views/Bianzheng.vue'),
        meta: { title: '辨证论治', module: 'pediatrics' }
      },
      {
        path: 'zonglun',
        name: 'PediatricsZonglun',
        component: () => import('@/modules/pediatrics/views/Zonglun.vue'),
        meta: { title: '总论', module: 'pediatrics' }
      },
      {
        path: 'bazheng',
        name: 'PediatricsBazheng',
        component: () => import('@/modules/pediatrics/views/Bazheng.vue'),
        meta: { title: '八症各论', module: 'pediatrics' }
      },
      {
        path: 'tupu',
        name: 'PediatricsTupu',
        component: () => import('@/modules/pediatrics/views/Tupu.vue'),
        meta: { title: '图谱', module: 'pediatrics' }
      },
      {
        path: 'fangji',
        name: 'PediatricsFangji',
        component: () => import('@/modules/pediatrics/views/Fangji.vue'),
        meta: { title: '方剂库', module: 'pediatrics' }
      },
      {
        path: 'yongyao',
        name: 'PediatricsYongyao',
        component: () => import('@/modules/pediatrics/views/Yongyao.vue'),
        meta: { title: '用药心得', module: 'pediatrics' }
      },
      {
        path: 'weihou',
        name: 'PediatricsWeihou',
        component: () => import('@/modules/pediatrics/views/Weihou.vue'),
        meta: { title: '危候警示', module: 'pediatrics' }
      },
      {
        path: 'tuina',
        name: 'PediatricsTuina',
        component: () => import('@/modules/pediatrics/views/Tuina.vue'),
        meta: { title: '推拿代药', module: 'pediatrics' }
      },
      {
        path: 'xunjie',
        name: 'PediatricsXunjie',
        component: () => import('@/modules/pediatrics/views/Xunjie.vue'),
        meta: { title: '医道训诫', module: 'pediatrics' }
      },
      {
        path: 'zice',
        name: 'PediatricsZice',
        component: () => import('@/modules/pediatrics/views/Zice.vue'),
        meta: { title: '自测练习', module: 'pediatrics' }
      },
      {
        path: 'search',
        name: 'PediatricsSearch',
        component: () => import('@/modules/pediatrics/views/Search.vue'),
        meta: { title: '全文检索', module: 'pediatrics' }
      },
      {
        path: 'huansuan',
        name: 'PediatricsHuansuan',
        component: () => import('@/modules/pediatrics/views/Huansuan.vue'),
        meta: { title: '古方剂量换算', module: 'pediatrics' }
      },
      {
        path: 'yian',
        name: 'PediatricsYian',
        component: () => import('@/modules/pediatrics/views/Yian.vue'),
        meta: { title: '医案库', module: 'pediatrics' }
      }
    ]
  },
// ============ 丹药研究模块（中国炼丹术与丹药） ============
  {
    path: '/alchemy',
    component: () => import('@/modules/alchemy/AlchemyLayout.vue'),
    children: [
      {
        path: '',
        name: 'AlchemyHome',
        component: () => import('@/modules/alchemy/views/HomeView.vue'),
        meta: { title: '首页', module: 'alchemy' }
      },
      {
        path: 'chapters',
        name: 'AlchemyChapters',
        component: () => import('@/modules/alchemy/views/ChaptersView.vue'),
        meta: { title: '总论', module: 'alchemy' }
      },
      {
        path: 'chapter/:id',
        name: 'AlchemyChapter',
        component: () => import('@/modules/alchemy/views/ChapterView.vue'),
        meta: { title: '章节', module: 'alchemy' }
      },
      {
        path: 'formulas',
        name: 'AlchemyFormulas',
        component: () => import('@/modules/alchemy/views/FormulasView.vue'),
        meta: { title: '方剂', module: 'alchemy' }
      },
      {
        path: 'formula/:id',
        name: 'AlchemyFormula',
        component: () => import('@/modules/alchemy/views/FormulaDetailView.vue'),
        meta: { title: '方剂详情', module: 'alchemy' }
      },
      {
        path: 'timeline',
        name: 'AlchemyTimeline',
        component: () => import('@/modules/alchemy/views/TimelineView.vue'),
        meta: { title: '时间线', module: 'alchemy' }
      },
      {
        path: 'glossary',
        name: 'AlchemyGlossary',
        component: () => import('@/modules/alchemy/views/GlossaryView.vue'),
        meta: { title: '术语', module: 'alchemy' }
      },
      {
        path: 'search',
        name: 'AlchemySearch',
        component: () => import('@/modules/alchemy/views/SearchView.vue'),
        meta: { title: '检索', module: 'alchemy' }
      },
      {
        path: 'quiz',
        name: 'AlchemyQuiz',
        component: () => import('@/modules/alchemy/views/QuizView.vue'),
        meta: { title: '测验', module: 'alchemy' }
      },
      {
        path: 'original',
        name: 'AlchemyOriginal',
        component: () => import('@/modules/alchemy/views/OriginalView.vue'),
        meta: { title: '原书对照', module: 'alchemy' }
      },
      {
        path: 'assist',
        name: 'AlchemyAssist',
        component: () => import('@/modules/alchemy/views/AssistHomeView.vue'),
        meta: { title: '辨证选方', module: 'alchemy' }
      },
      {
        path: 'assist/professional',
        name: 'AlchemyAssistProfessional',
        component: () => import('@/modules/alchemy/views/ProfessionalFlowView.vue'),
        meta: { title: '专业辨证', module: 'alchemy' }
      },
      {
        path: 'assist/public',
        name: 'AlchemyAssistPublic',
        component: () => import('@/modules/alchemy/views/PublicGuideView.vue'),
        meta: { title: '科普自测', module: 'alchemy' }
      },
      {
        path: 'dulong',
        name: 'AlchemyDulong',
        component: () => import('@/modules/alchemy/views/DulongView.vue'),
        meta: { title: '毒龙丹引药', module: 'alchemy' }
      },
      {
        path: 'safety',
        name: 'AlchemySafety',
        component: () => import('@/modules/alchemy/views/SafetyView.vue'),
        meta: { title: '安全与法规', module: 'alchemy' }
      }
    ]
  },
// ============ 外科疮疡模块 ============
  {
    path: '/surgery',
    component: () => import('@/modules/surgery/SurgeryLayout.vue'),
    redirect: '/surgery/diseases',
    children: [
      {
        path: 'diseases',
        name: 'SurgeryDiseases',
        component: () => import('@/modules/surgery/views/DiseaseList.vue'),
        meta: { title: '疾病库', module: 'surgery' }
      },
      {
        path: 'diseases/:id',
        name: 'SurgeryDiseaseDetail',
        component: () => import('@/modules/surgery/views/DiseaseDetail.vue'),
        meta: { title: '疾病详情', module: 'surgery' }
      },
      {
        path: 'formulas',
        name: 'SurgeryFormulas',
        component: () => import('@/modules/surgery/views/FormulaList.vue'),
        meta: { title: '方剂库', module: 'surgery' }
      },
      {
        path: 'cases',
        name: 'SurgeryCases',
        component: () => import('@/modules/surgery/views/CaseList.vue'),
        meta: { title: '医案库', module: 'surgery' }
      },
      {
        path: 'cases/:id',
        name: 'SurgeryCaseDetail',
        component: () => import('@/modules/surgery/views/CaseDetail.vue'),
        meta: { title: '医案详情', module: 'surgery' }
      },
      {
        path: 'expert',
        name: 'SurgeryExpert',
        component: () => import('@/modules/surgery/views/ExpertView.vue'),
        meta: { title: '名医经验', module: 'surgery' }
      },
      {
        path: 'diagnosis',
        name: 'SurgeryDiagnosis',
        component: () => import('@/modules/surgery/views/DiagnosisView.vue'),
        meta: { title: '辨证诊断', module: 'surgery' }
      },
      {
        path: 'treatment',
        name: 'SurgeryTreatment',
        component: () => import('@/modules/surgery/views/TreatmentView.vue'),
        meta: { title: '治法规则', module: 'surgery' }
      },
      {
        path: 'tips',
        name: 'SurgeryTips',
        component: () => import('@/modules/surgery/views/TipsView.vue'),
        meta: { title: '临床要诀', module: 'surgery' }
      },
      {
        path: 'overview',
        name: 'SurgeryOverview',
        component: () => import('@/modules/surgery/views/OverviewView.vue'),
        meta: { title: '统计概览', module: 'surgery' }
      }
    ]
  },
  // 兜底：未匹配路径回到门户
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

// ============ 全开放：不再做登录门禁 ============

function inferModule(path) {
  const seg = (path || '').split('/')[1] || ''
  const known = { anorectal: 'anorectal', pediatrics: 'pediatrics', alchemy: 'alchemy', surgery: 'surgery' }
  if (known[seg]) return known[seg]
  if (path === '/') return 'portal'
  if (path.startsWith('/stats')) return 'stats'
  return seg || 'portal'
}

// ============ 访问统计埋点：afterEach 上报一次（同会话去重） ============
router.afterEach((to) => {
  const module = to.meta.module || inferModule(to.path)
  const key = `visit:${module}:${to.path}`
  try {
    if (sessionStorage.getItem(key)) return
    sessionStorage.setItem(key, '1')
  } catch (e) {
    /* sessionStorage 不可用时忽略去重 */
  }
  // 免鉴权上报，失败静默
  fetch('/api/v1/visits', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ module, path: to.path, referrer: document.referrer || undefined })
  }).catch(() => {})
})

export default router
