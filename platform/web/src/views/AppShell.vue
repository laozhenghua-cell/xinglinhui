<template>
  <div class="shell">
    <!-- 侧边栏 -->
    <div v-if="mobileOpen" class="side-mask" @click="mobileOpen = false"></div>
    <aside class="shell-side" :class="{ collapsed: isCollapsed, 'mobile-open': mobileOpen }">
      <div class="side-brand" @click="router.push('/')">
        <div class="brand-seal">杏林</div>
        <div v-show="!isCollapsed" class="brand-txt">
          <b>杏林汇</b>
          <span>智能诊疗系统</span>
        </div>
      </div>
      <el-menu :default-active="activeMenu" :collapse="isCollapsed && !mobileOpen" router class="side-menu"
               background-color="transparent" text-color="#B9C8C2" active-text-color="#FFFFFF">
        <el-menu-item index="/">
          <el-icon><Odometer /></el-icon><template #title>工作台</template>
        </el-menu-item>
        <el-menu-item index="/clinic">
          <el-icon><FirstAidKit /></el-icon><template #title>门诊诊疗</template>
        </el-menu-item>
        <el-menu-item index="/dx">
          <el-icon><MagicStick /></el-icon><template #title>症状辨证</template>
        </el-menu-item>
        <el-menu-item index="/kb">
          <el-icon><Collection /></el-icon><template #title>知识总库</template>
        </el-menu-item>
        <el-menu-item index="/learn">
          <el-icon><Reading /></el-icon><template #title>学苑</template>
        </el-menu-item>
        <el-menu-item index="/stats">
          <el-icon><TrendCharts /></el-icon><template #title>使用统计</template>
        </el-menu-item>
      </el-menu>
      <div class="side-foot" v-show="!isCollapsed || mobileOpen">
        <el-tag size="small" effect="plain" style="border-color:#3E5E56;color:#9FC0B6">全开放 · 免登录</el-tag>
      </div>
    </aside>

    <!-- 主区 -->
    <div class="shell-main">
      <header class="shell-top">
        <div class="top-left">
          <el-icon class="collapse-btn" @click="toggleSide"><Fold /></el-icon>
          <span class="top-title">{{ pageTitle }}</span>
        </div>
        <div class="top-right">
          <span class="ver-tag" title="当前版本">杏林汇 v9 · 2026-08-28</span>
          <el-button size="small" type="primary" @click="router.push('/clinic/new')">
            <el-icon><Plus /></el-icon>&nbsp;新建就诊
          </el-button>
          <el-button size="small" plain @click="router.push('/dx')">症状辨证</el-button>
        </div>
      </header>
      <main class="shell-body">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Odometer, FirstAidKit, MagicStick, Collection, Reading, TrendCharts, Fold, Plus } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const isCollapsed = ref(false)
const mobileOpen = ref(false)
const isMobile = ref(window.innerWidth < 900)
if (isMobile.value) isCollapsed.value = true
window.addEventListener('resize', () => {
  isMobile.value = window.innerWidth < 900
  if (isMobile.value) isCollapsed.value = true
  else mobileOpen.value = false
})
function toggleSide() {
  if (isMobile.value) mobileOpen.value = !mobileOpen.value
  else isCollapsed.value = !isCollapsed.value
}
const pageTitle = computed(() => route.meta.title || '杏林汇')
const activeMenu = computed(() => {
  const p = route.path
  if (p.startsWith('/clinic')) return '/clinic'
  if (p.startsWith('/dx')) return '/dx'
  if (p.startsWith('/kb')) return '/kb'
  if (p.startsWith('/learn')) return '/learn'
  if (p.startsWith('/stats')) return '/stats'
  return '/'
})
</script>

<style scoped>
.shell { display: flex; height: 100%; }
.shell-side {
  width: 216px; flex-shrink: 0; background: linear-gradient(180deg, #17332E 0%, #1F4E46 100%);
  display: flex; flex-direction: column; transition: width .2s;
}
.shell-side.collapsed { width: 64px; }
.side-brand { display: flex; align-items: center; gap: 10px; padding: 18px 16px; cursor: pointer; }
.brand-seal {
  width: 38px; height: 38px; border-radius: 10px; background: #B03A2E; color: #fff;
  display: flex; align-items: center; justify-content: center; font-family: "Songti SC", serif;
  font-size: 15px; flex-shrink: 0; box-shadow: 0 2px 8px rgba(176, 58, 46, .4);
}
.brand-txt { color: #fff; display: flex; flex-direction: column; }
.brand-txt b { font-family: "Songti SC", serif; font-size: 18px; letter-spacing: 2px; }
.brand-txt span { font-size: 11px; color: #9FC0B6; }
.side-menu { flex: 1; padding-top: 6px; }
.side-menu :deep(.el-menu-item) { height: 46px; margin: 2px 10px; border-radius: 8px; }
.side-menu :deep(.el-menu-item.is-active) { background: rgba(255,255,255,.14); }
.side-menu :deep(.el-menu-item:hover) { background: rgba(255,255,255,.08); }
.side-foot { padding: 14px 18px; border-top: 1px solid rgba(255,255,255,.08); }
.shell-main { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.shell-top {
  height: 56px; background: #fff; border-bottom: 1px solid var(--xl-line);
  display: flex; align-items: center; justify-content: space-between; padding: 0 18px; flex-shrink: 0;
}
.top-left { display: flex; align-items: center; gap: 12px; }
.collapse-btn { cursor: pointer; font-size: 17px; color: #55665F; }
.top-title { font-family: "Songti SC", serif; font-size: 16px; color: var(--xl-ink); }
.shell-body { flex: 1; overflow-y: auto; background: var(--xl-paper); }
.side-mask { display: none; }
@media (max-width: 900px) {
  .shell-side { position: fixed; left: 0; top: 0; bottom: 0; z-index: 60; transform: translateX(-100%); transition: transform .2s; }
  .shell-side.mobile-open { transform: translateX(0); width: 216px !important; }
  .side-mask { display: block; position: fixed; inset: 0; background: rgba(0,0,0,.35); z-index: 55; }
  .shell-top { padding: 0 10px; }
}
.ver-tag { font-size: 11px; color: #8A94A0; margin-right: 12px; font-family: monospace; }
</style>
