<template>
  <div class="app-shell dan-shell">
    <!-- 桌面侧边栏 -->
    <aside class="sidebar">
      <div class="brand">
        <div class="t1">中国炼丹术与丹药</div>
        <div class="t2">张觉人 著 · 数字化研究参考系统</div>
      </div>
      <nav>
        <div class="s-item back-item" @click="backToPortal">
          <span>🏛️</span><span>返回平台门户</span>
        </div>
        <div v-for="item in navItems" :key="item.path" class="s-item"
             :class="{ active: isActive(item.path) }" @click="go(item.path)">
          <span>{{ item.icon }}</span><span>{{ item.title }}</span>
        </div>
      </nav>
      <div class="footnote">
        仅供中医外科专业人士与研究者<br />学术参考 · 严禁自行配制与内服
      </div>
    </aside>

    <div class="main-area">
      <!-- 移动端顶栏 -->
      <header class="mobile-header">
        <span @click="backToPortal" style="cursor:pointer">🏛️</span>
        <span class="title">中国炼丹术与丹药</span>
        <span @click="backToPortal" style="cursor:pointer;font-size:0.75rem">门户</span>
      </header>

      <main class="content">
        <router-view />
        <div class="footer-note">
          中国炼丹术与丹药 · 张觉人著 · 四川人民出版社 1984 · 数字化研究参考系统<br />
          丹药多为汞、砷等剧毒化合物，现代已严格限制使用。本系统仅供学术研究，严禁自行配制、严禁内服。
        </div>
      </main>

      <!-- 移动端底部导航 -->
      <nav class="bottom-nav">
        <div v-for="item in mobileNav" :key="item.path" class="nav-item"
             :class="{ active: isActive(item.path) }" @click="go(item.path)">
          <span class="icon">{{ item.icon }}</span>
          <span>{{ item.title }}</span>
        </div>
        <div class="nav-item" :class="{ active: moreActive }" @click="drawer = true">
          <span class="icon">☰</span>
          <span>更多</span>
        </div>
      </nav>
    </div>

    <!-- 移动端"更多"抽屉 -->
    <el-drawer v-model="drawer" direction="btt" size="62%" :with-header="true" title="更多栏目">
      <div v-for="item in moreItems" :key="item.path" class="card" style="cursor:pointer" @click="go(item.path)">
        <span style="margin-right:8px">{{ item.icon }}</span>{{ item.title }}
        <span style="float:right;color:#b9a87e">{{ item.desc }}</span>
      </div>
      <div class="safety-banner">
        <strong>安全声明：</strong>本系统为学术研究参考。丹药多为汞、砷剧毒化合物，严禁自行配制、严禁内服。
      </div>
    </el-drawer>

    <!-- 首次访问安全声明弹窗 -->
    <el-dialog v-model="safetyVisible" title="⚠️ 安全声明" width="min(92vw, 480px)" :close-on-click-modal="false">
      <div style="font-size:0.92rem;line-height:1.9">
        <p style="margin-top:0">本系统数字化自张觉人《中国炼丹术与丹药》（四川人民出版社，1984），定位为<strong>中医外科专业学术研究参考</strong>。</p>
        <p>书中所载丹药（轻粉、红升丹、白降丹、三仙丹等）均为<strong>汞、砷等剧毒化合物制剂</strong>，历史上用于疮疡外科的腐蚀、拔毒、提脓、生肌。现代医学已对这些制剂严格限制或淘汰。</p>
        <p style="color:#b35309"><strong>严禁自行按方配制；严禁内服；严禁用于任何非专业用途。</strong>临床使用必须遵循现行药事法规与专业规范。中毒风险极高，请务必知悉。</p>
      </div>
      <template #footer>
        <el-button type="danger" @click="acceptSafety">我已了解，进入系统</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import './main.css'

const route = useRoute()
const router = useRouter()
const drawer = ref(false)
const safetyVisible = ref(!localStorage.getItem('dan_safety_accepted'))

const navItems = [
  { path: '/alchemy', icon: '🏠', title: '首页' },
  { path: '/alchemy/chapters', icon: '📜', title: '总论 · 源流' },
  { path: '/alchemy/assist', icon: '🩺', title: '辨证选方' },
  { path: '/alchemy/formulas', icon: '🧪', title: '丹药方剂库' },
  { path: '/alchemy/dulong', icon: '🐉', title: '毒龙丹引药' },
  { path: '/alchemy/timeline', icon: '🕰️', title: '炼丹时间线' },
  { path: '/alchemy/glossary', icon: '📖', title: '术语表' },
  { path: '/alchemy/original', icon: '🖼️', title: '原书对照' },
  { path: '/alchemy/search', icon: '🔍', title: '全文检索' },
  { path: '/alchemy/quiz', icon: '✍️', title: '知识测验' },
  { path: '/alchemy/safety', icon: '⚠️', title: '安全与法规' },
]

const mobileNav = [
  { path: '/alchemy', icon: '🏠', title: '首页' },
  { path: '/alchemy/assist', icon: '🩺', title: '辨证' },
  { path: '/alchemy/chapters', icon: '📜', title: '总论' },
  { path: '/alchemy/formulas', icon: '🧪', title: '方剂' },
]

const moreItems = [
  { path: '/alchemy/dulong', icon: '🐉', title: '毒龙丹引药', desc: '245条一药多引' },
  { path: '/alchemy/timeline', icon: '🕰️', title: '时间线', desc: '炼丹两千年脉络' },
  { path: '/alchemy/glossary', icon: '📖', title: '术语表', desc: '炼丹术语释义' },
  { path: '/alchemy/original', icon: '🖼️', title: '原书对照', desc: '转录与原文图像' },
  { path: '/alchemy/search', icon: '🔍', title: '全文检索', desc: '搜索全书内容' },
  { path: '/alchemy/quiz', icon: '✍️', title: '知识测验', desc: '自测掌握程度' },
  { path: '/alchemy/safety', icon: '⚠️', title: '安全与法规', desc: '现代法规与毒理' },
]

const moreActive = computed(() =>
  ['/alchemy/dulong', '/alchemy/timeline', '/alchemy/glossary', '/alchemy/original', '/alchemy/search', '/alchemy/quiz', '/alchemy/safety'].some((p) => route.path.startsWith(p))
)

function isActive(path) {
  if (path === '/alchemy') return route.path === '/alchemy'
  return route.path.startsWith(path)
}

function go(path) {
  drawer.value = false
  router.push(path)
}

function backToPortal() {
  router.push('/')
}

function acceptSafety() {
  localStorage.setItem('dan_safety_accepted', '1')
  safetyVisible.value = false
}
</script>
