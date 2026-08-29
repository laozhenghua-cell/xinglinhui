<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Document, FirstAidKit, Reading, Collection, Picture, Box, Notebook,
  Warning, MagicStick, School, EditPen, Expand, Fold, Menu as MenuIcon,
  Search, ScaleToOriginal, Stamp, HomeFilled,
} from '@element-plus/icons-vue'
import './theme.css'

const route = useRoute()
const router = useRouter()
const collapsed = ref(false)
const drawerOpen = ref(false)
const isMobile = ref(false)

function onResize() {
  isMobile.value = window.matchMedia('(max-width: 768px)').matches
  if (!isMobile.value) drawerOpen.value = false
}
onMounted(() => {
  onResize()
  window.addEventListener('resize', onResize)
})
onBeforeUnmount(() => window.removeEventListener('resize', onResize))

const navs = [
  { path: '/pediatrics', label: '首页', icon: Document },
  { path: '/pediatrics/bianzheng', label: '辨证论治', icon: FirstAidKit },
  { path: '/pediatrics/zonglun', label: '总论', icon: Reading },
  { path: '/pediatrics/bazheng', label: '八症各论', icon: Collection },
  { path: '/pediatrics/tupu', label: '图谱', icon: Picture },
  { path: '/pediatrics/fangji', label: '方剂库', icon: Box },
  { path: '/pediatrics/yongyao', label: '用药心得', icon: Notebook },
  { path: '/pediatrics/yian', label: '医案库', icon: Stamp },
  { path: '/pediatrics/weihou', label: '危候警示', icon: Warning },
  { path: '/pediatrics/tuina', label: '推拿代药', icon: MagicStick },
  { path: '/pediatrics/xunjie', label: '医道训诫', icon: School },
  { path: '/pediatrics/zice', label: '自测练习', icon: EditPen },
  {
    label: '工具',
    icon: ScaleToOriginal,
    children: [
      { path: '/pediatrics/search', label: '全文检索', icon: Search },
      { path: '/pediatrics/huansuan', label: '剂量换算', icon: ScaleToOriginal },
    ],
  },
]

const active = computed(() => route.path)

function backToPortal() {
  router.push('/')
}
function navTo() {
  drawerOpen.value = false
}
</script>

<template>
  <div class="peds-shell">
    <el-container class="shell">
      <el-aside v-if="!isMobile" :width="collapsed ? '64px' : '208px'" class="aside no-print">
        <div class="brand">
          <span class="seal">程氏儿科</span>
          <span v-if="!collapsed" class="brand-txt">
            <b>程氏家传儿科秘要</b>
            <i>辅助诊疗系统</i>
          </span>
        </div>
        <el-menu :default-active="active" :collapse="collapsed" router class="menu">
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <template #title>返回平台门户</template>
          </el-menu-item>
          <template v-for="n in navs" :key="n.label">
            <el-sub-menu v-if="n.children" :index="'sub-' + n.label">
              <template #title>
                <el-icon><component :is="n.icon" /></el-icon>
                <span>{{ n.label }}</span>
              </template>
              <el-menu-item v-for="c in n.children" :key="c.path" :index="c.path">
                <el-icon><component :is="c.icon" /></el-icon>
                <template #title>{{ c.label }}</template>
              </el-menu-item>
            </el-sub-menu>
            <el-menu-item v-else :index="n.path">
              <el-icon><component :is="n.icon" /></el-icon>
              <template #title>{{ n.label }}</template>
            </el-menu-item>
          </template>
        </el-menu>
        <div class="aside-foot" v-if="!collapsed">
          <p>清·程康圃 著</p>
          <p>仅供教学与临床参考</p>
        </div>
      </el-aside>

      <!-- 移动端抽屉导航 -->
      <el-drawer v-if="isMobile" v-model="drawerOpen" direction="ltr" size="240px" :with-header="false" class="m-drawer no-print">
        <div class="brand">
          <span class="seal">程氏儿科</span>
          <span class="brand-txt">
            <b>程氏家传儿科秘要</b>
            <i>辅助诊疗系统</i>
          </span>
        </div>
        <el-menu :default-active="active" router class="menu" @select="navTo">
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <template #title>返回平台门户</template>
          </el-menu-item>
          <template v-for="n in navs" :key="'m-' + n.label">
            <el-sub-menu v-if="n.children" :index="'sub-' + n.label">
              <template #title>
                <el-icon><component :is="n.icon" /></el-icon>
                <span>{{ n.label }}</span>
              </template>
              <el-menu-item v-for="c in n.children" :key="c.path" :index="c.path">
                <el-icon><component :is="c.icon" /></el-icon>
                <template #title>{{ c.label }}</template>
              </el-menu-item>
            </el-sub-menu>
            <el-menu-item v-else :index="n.path">
              <el-icon><component :is="n.icon" /></el-icon>
              <template #title>{{ n.label }}</template>
            </el-menu-item>
          </template>
        </el-menu>
      </el-drawer>

      <el-container>
        <el-header class="header no-print">
          <el-button v-if="isMobile" text class="fold-btn" @click="drawerOpen = true">
            <el-icon size="20"><MenuIcon /></el-icon>
          </el-button>
          <el-button v-else text @click="collapsed = !collapsed" class="fold-btn">
            <el-icon size="18"><Expand v-if="collapsed" /><Fold v-else /></el-icon>
          </el-button>
          <el-button text class="fold-btn" @click="backToPortal" title="返回平台门户">
            <el-icon size="18"><HomeFilled /></el-icon>
            <span style="font-size:12px;margin-left:4px">平台门户</span>
          </el-button>
          <span class="header-title">{{ route.meta.title ?? '' }}</span>
          <span class="header-note">八症六字 · 平肝 补脾 泻心</span>
        </el-header>
        <el-main class="main">
          <router-view />
          <div class="site-footer no-print">
            内容据《程氏家传儿科秘要》整理 · 仅供教学与临床参考
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<style scoped>
.shell {
  min-height: 100vh;
}
.aside {
  background: linear-gradient(180deg, #f5eedd 0%, #efe5cf 100%);
  border-right: 1px solid var(--line);
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  transition: width 0.2s;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px 12px 14px;
  border-bottom: 1px solid var(--line);
}
.brand-txt {
  display: flex;
  flex-direction: column;
  line-height: 1.4;
}
.brand-txt b {
  font-family: var(--font-kai);
  font-size: 15px;
  color: var(--ink);
}
.brand-txt i {
  font-style: normal;
  font-size: 11.5px;
  color: var(--vermilion);
}
.menu {
  border-right: none;
  background: transparent;
  flex: 1;
  --el-menu-bg-color: transparent;
  --el-menu-hover-bg-color: #eadfc6;
  --el-menu-active-color: #b03a2e;
  --el-menu-text-color: #4a4235;
}
.aside-foot {
  padding: 10px 16px;
  font-size: 11px;
  color: #8a7c5f;
  border-top: 1px solid var(--line);
  line-height: 1.7;
}
.aside-foot p {
  margin: 0;
}
.header {
  display: flex;
  align-items: center;
  gap: 10px;
  height: 52px;
  background: rgba(247, 241, 227, 0.92);
  border-bottom: 1px solid var(--line);
  backdrop-filter: blur(4px);
  position: sticky;
  top: 0;
  z-index: 20;
}
.header-title {
  font-family: var(--font-kai);
  font-size: 17px;
  font-weight: 700;
  color: var(--ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.header-note {
  margin-left: auto;
  font-size: 12.5px;
  color: var(--vermilion);
  font-family: var(--font-kai);
  white-space: nowrap;
}
.main {
  padding: 0;
}
.site-footer {
  text-align: center;
  padding: 10px 12px 26px;
  font-size: 11.5px;
  color: #a0845a;
  border-top: 1px dashed var(--line);
  margin-top: 20px;
}

@media (max-width: 768px) {
  .header {
    height: 46px;
    padding: 0 8px;
    gap: 6px;
  }
  .header-title {
    font-size: 15px;
  }
  .header-note {
    display: none;
  }
  .fold-btn {
    padding: 6px;
  }
}
</style>

<style>
/* 移动端抽屉内部样式（teleport 到 body，需全局作用域） */
.m-drawer .el-drawer__body {
  padding: 0;
  background: linear-gradient(180deg, #f5eedd 0%, #efe5cf 100%);
  display: flex;
  flex-direction: column;
}
</style>
