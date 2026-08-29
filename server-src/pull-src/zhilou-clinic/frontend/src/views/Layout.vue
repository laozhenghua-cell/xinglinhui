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
        <span v-show="isMobile || !isCollapsed" class="logo-text">华夏痔瘘诊疗系统</span>
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
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <template #title>工作台</template>
        </el-menu-item>
        <el-menu-item index="/patients">
          <el-icon><User /></el-icon>
          <template #title>患者管理</template>
        </el-menu-item>
        <el-menu-item index="/consultations/new">
          <el-icon><EditPen /></el-icon>
          <template #title>新建就诊</template>
        </el-menu-item>
        <el-menu-item index="/diagnosis">
          <el-icon><MagicStick /></el-icon>
          <template #title>智能辨证</template>
        </el-menu-item>
        <el-menu-item index="/diagnosis/image">
          <el-icon><Camera /></el-icon>
          <template #title>影像诊断</template>
        </el-menu-item>
        <el-menu-item index="/knowledge">
          <el-icon><Reading /></el-icon>
          <template #title>知识库</template>
        </el-menu-item>
        <el-menu-item index="/billing">
          <el-icon><Money /></el-icon>
          <template #title>收费管理</template>
        </el-menu-item>
        <el-menu-item index="/inventory">
          <el-icon><Box /></el-icon>
          <template #title>库存管理</template>
        </el-menu-item>
        <el-menu-item index="/settings">
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
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" icon="UserFilled" />
              <span class="user-name">{{ authStore.userName }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="settings">个人设置</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useWindowSize } from '@vueuse/core'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { width } = useWindowSize()

const isCollapsed = ref(false)
const mobileDrawer = ref(false)

const isMobile = computed(() => width.value < 768)

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/patients')) return '/patients'
  if (path.startsWith('/consultations')) return '/consultations/new'
  if (path.startsWith('/diagnosis/image')) return '/diagnosis/image'
  if (path.startsWith('/diagnosis')) return '/diagnosis'
  if (path.startsWith('/knowledge')) return '/knowledge'
  if (path.startsWith('/billing')) return '/billing'
  if (path.startsWith('/inventory')) return '/inventory'
  if (path.startsWith('/settings')) return '/settings'
  return '/dashboard'
})

const currentTitle = computed(() => route.meta.title || '工作台')

// 切换页面后关闭移动端抽屉
function onMenuSelect() {
  if (isMobile.value) mobileDrawer.value = false
}

function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
}

function handleCommand(command) {
  if (command === 'logout') {
    authStore.logout()
  } else if (command === 'settings') {
    router.push('/settings')
  }
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
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #333;
}

.user-name {
  font-size: 14px;
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

  .user-name {
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
