<template>
  <el-container class="layout-container">
    <!-- 移动端遮罩 -->
    <div
      v-if="isMobile && mobileDrawer"
      class="mobile-mask"
      @click="mobileDrawer = false"
    ></div>

    <el-aside
      :width="isMobile ? '220px' : isCollapsed ? '64px' : '220px'"
      class="layout-aside"
      :class="{ 'mobile-open': isMobile && mobileDrawer }"
    >
      <div class="logo-area">
        <img src="/favicon.svg" alt="logo" class="logo-icon" />
        <span v-show="isMobile || !isCollapsed" class="logo-text">杏林汇 · 肛肠痔漏模块</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="!isMobile && isCollapsed"
        router
        class="aside-menu"
        background-color="#001529"
        text-color="#ffffffb3"
        active-text-color="#409EFF"
        @select="onMenuSelect"
      >
        <el-menu-item index="/anorectal/dashboard">
          <el-icon><DataBoard /></el-icon>
          <template #title>工作台</template>
        </el-menu-item>
        <el-menu-item index="/anorectal/patients">
          <el-icon><User /></el-icon>
          <template #title>患者管理</template>
        </el-menu-item>
        <el-menu-item index="/anorectal/consultations/new">
          <el-icon><EditPen /></el-icon>
          <template #title>新建就诊</template>
        </el-menu-item>
        <el-menu-item index="/anorectal/diagnosis">
          <el-icon><MagicStick /></el-icon>
          <template #title>智能辨证</template>
        </el-menu-item>
        <el-menu-item index="/anorectal/diagnosis/image">
          <el-icon><Camera /></el-icon>
          <template #title>影像诊断</template>
        </el-menu-item>
        <el-menu-item index="/anorectal/knowledge">
          <el-icon><Reading /></el-icon>
          <template #title>知识库</template>
        </el-menu-item>
        <el-menu-item index="/anorectal/billing">
          <el-icon><Money /></el-icon>
          <template #title>收费管理</template>
        </el-menu-item>
        <el-menu-item index="/anorectal/inventory">
          <el-icon><Box /></el-icon>
          <template #title>库存管理</template>
        </el-menu-item>
        <el-menu-item index="/anorectal/settings">
          <el-icon><Setting /></el-icon>
          <template #title>系统设置</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container class="main-container">
      <el-header class="layout-header">
        <div class="header-left">
          <!-- 移动端汉堡菜单 -->
          <el-icon v-if="isMobile" class="collapse-btn" @click="mobileDrawer = true">
            <Menu />
          </el-icon>
          <!-- 桌面端折叠按钮 -->
          <el-icon v-else class="collapse-btn" @click="toggleCollapse">
            <Fold v-if="!isCollapsed" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-button text size="small" @click="router.push('/dx')">
            <el-icon><MagicStick /></el-icon>
            <span style="margin-left:2px">辨证中心</span>
          </el-button>
          <el-button text size="small" @click="router.push('/')">
            <el-icon><HomeFilled /></el-icon>
            <span style="margin-left:4px">首页（门户）</span>
          </el-button>
          <el-button text size="small" @click="router.push('/stats')">
            <el-icon><Histogram /></el-icon>
            <span style="margin-left:4px">使用统计</span>
          </el-button>
          <el-button text size="small" @click="router.push('/kb')">
            <el-icon><Reading /></el-icon>
            <span style="margin-left:4px">知识总库</span>
          </el-button>
          <span class="open-access-tag">全开放 · 免登录</span>
        </div>
      </el-header>

      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useWindowSize } from '@vueuse/core'

const route = useRoute()
const router = useRouter()
const { width } = useWindowSize()

const isCollapsed = ref(false)
const mobileDrawer = ref(false)

const isMobile = computed(() => width.value < 768)

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/anorectal/patients')) return '/anorectal/patients'
  if (path.startsWith('/anorectal/consultations')) return '/anorectal/consultations/new'
  if (path.startsWith('/anorectal/diagnosis/image')) return '/anorectal/diagnosis/image'
  if (path.startsWith('/anorectal/diagnosis')) return '/anorectal/diagnosis'
  if (path.startsWith('/anorectal/knowledge')) return '/anorectal/knowledge'
  if (path.startsWith('/anorectal/billing')) return '/anorectal/billing'
  if (path.startsWith('/anorectal/inventory')) return '/anorectal/inventory'
  if (path.startsWith('/anorectal/settings')) return '/anorectal/settings'
  return '/anorectal/dashboard'
})

const currentTitle = computed(() => route.meta.title || '工作台')

// 切换页面后关闭移动端抽屉
function onMenuSelect() {
  if (isMobile.value) mobileDrawer.value = false
}

function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.layout-aside {
  background-color: #001529;
  transition: width 0.3s, transform 0.3s;
  overflow: hidden;
}

.logo-area {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-bottom: 1px solid #ffffff1a;
}

.logo-icon {
  width: 32px;
  height: 32px;
}

.logo-text {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}

.aside-menu {
  border-right: none;
}

.aside-menu:not(.el-menu--collapse) {
  width: 220px;
}

.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  padding: 0 16px;
  height: 56px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: #333;
}

.collapse-btn:hover {
  color: #409EFF;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.open-access-tag {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
}

.layout-main {
  background: #f5f7fa;
  padding: 16px;
  overflow-y: auto;
}

/* ============ 移动端 ============ */
@media (max-width: 768px) {
  .layout-aside {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 1001;
    transform: translateX(-100%);
  }
  .layout-aside.mobile-open {
    transform: translateX(0);
    box-shadow: 2px 0 12px rgba(0, 0, 0, 0.2);
  }

  .mobile-mask {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.45);
    z-index: 1000;
  }

  .open-access-tag {
    display: none;
  }

  .layout-header {
    padding: 0 12px;
    height: 52px;
  }

  .layout-main {
    padding: 12px;
  }

  .el-breadcrumb {
    font-size: 13px;
  }
}
</style>
