<template>
  <el-container class="surgery-shell">
    <el-aside width="220px" class="aside">
      <div class="brand">
        <span class="brand-title">外科疮疡</span>
        <span class="brand-sub">辅助诊疗模块</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        class="menu"
        background-color="#2E1B1B"
        text-color="#f0e6d2b3"
        active-text-color="#e6b54a"
      >
        <el-menu-item index="/surgery/diseases">
          <el-icon><Collection /></el-icon>
          <template #title>疾病库</template>
        </el-menu-item>
        <el-menu-item index="/surgery/formulas">
          <el-icon><Box /></el-icon>
          <template #title>方剂库</template>
        </el-menu-item>
        <el-menu-item index="/surgery/cases">
          <el-icon><Document /></el-icon>
          <template #title>医案库</template>
        </el-menu-item>
        <el-menu-item index="/surgery/expert">
          <el-icon><UserFilled /></el-icon>
          <template #title>名医经验</template>
        </el-menu-item>
        <el-menu-item index="/surgery/diagnosis">
          <el-icon><MagicStick /></el-icon>
          <template #title>辨证诊断</template>
        </el-menu-item>
        <el-menu-item index="/surgery/treatment">
          <el-icon><FirstAidKit /></el-icon>
          <template #title>治法规则</template>
        </el-menu-item>
        <el-menu-item index="/surgery/tips">
          <el-icon><Reading /></el-icon>
          <template #title>临床要诀</template>
        </el-menu-item>
        <el-menu-item index="/surgery/overview">
          <el-icon><Histogram /></el-icon>
          <template #title>统计概览</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>外科疮疡</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-button text size="small" @click="router.push('/')">
            <el-icon><HomeFilled /></el-icon>
            <span style="margin-left:4px">返回平台门户</span>
          </el-button>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Collection, Box, Document, UserFilled, MagicStick,
  FirstAidKit, Reading, Histogram, HomeFilled,
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const activeMenu = computed(() => {
  const p = route.path
  if (p.startsWith('/surgery/diseases')) return '/surgery/diseases'
  if (p.startsWith('/surgery/formulas')) return '/surgery/formulas'
  if (p.startsWith('/surgery/cases')) return '/surgery/cases'
  if (p.startsWith('/surgery/expert')) return '/surgery/expert'
  if (p.startsWith('/surgery/diagnosis')) return '/surgery/diagnosis'
  if (p.startsWith('/surgery/treatment')) return '/surgery/treatment'
  if (p.startsWith('/surgery/tips')) return '/surgery/tips'
  if (p.startsWith('/surgery/overview')) return '/surgery/overview'
  return '/surgery/diseases'
})

const currentTitle = computed(() => route.meta.title || '疾病库')
</script>

<style scoped>
.surgery-shell {
  height: 100vh;
}

.aside {
  background-color: #2e1b1b;
  overflow: hidden;
}

.brand {
  height: 64px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #ffffff1a;
}

.brand-title {
  color: #f0e6d2;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 2px;
}

.brand-sub {
  color: #c9b795;
  font-size: 11px;
  margin-top: 2px;
}

.menu {
  border-right: none;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  padding: 0 16px;
  height: 56px;
}

.main {
  background: #f7f5f1;
  padding: 16px;
  overflow-y: auto;
}
</style>
