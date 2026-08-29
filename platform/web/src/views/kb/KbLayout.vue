<template>
  <div class="kb-shell">
    <header class="kb-header">
      <div class="kb-header-left">
        <el-button text @click="router.push('/')">
          <el-icon><HomeFilled /></el-icon>
          <span style="margin-left:4px">返回门户</span>
        </el-button>
        <span class="kb-title">杏林汇 · 知识总库</span>
      </div>
      <div class="kb-header-search">
        <el-input
          v-model="q"
          placeholder="跨专科检索方剂 / 中药 / 病种 / 医案 / 术语…"
          clearable
          style="width: 380px"
          @keyup.enter="doSearch"
          @clear="q = ''"
        >
          <template #append>
            <el-button @click="doSearch">检索</el-button>
          </template>
        </el-input>
      </div>
    </header>

    <div class="kb-tabs">
      <el-tabs :model-value="activeTab" @tab-change="onTabChange">
        <el-tab-pane label="总览" name="home" />
        <el-tab-pane v-for="t in KB_TYPES" :key="t.key" :label="t.label" :name="t.key" />
      </el-tabs>
    </div>

    <main class="kb-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { HomeFilled } from '@element-plus/icons-vue'
import { KB_TYPES } from './config'

const route = useRoute()
const router = useRouter()
const q = ref('')

const activeTab = computed(() => {
  if (route.name === 'KbSearch' || route.name === 'KbHome') return 'home'
  const t = route.params.type
  return KB_TYPES.some((x) => x.key === t) ? t : 'home'
})

watch(
  () => route.query.q,
  (v) => { q.value = v || '' },
  { immediate: true }
)

function onTabChange(name) {
  if (name === 'home') router.push('/kb')
  else router.push(`/kb/${name}`)
}

function doSearch() {
  const kw = q.value.trim()
  router.push({ path: '/kb/search', query: kw ? { q: kw } : {} })
}
</script>

<style scoped>
.kb-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.kb-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 24px;
  background: #fff;
  border-bottom: 1px solid #e7e3da;
  position: sticky;
  top: 0;
  z-index: 10;
}

.kb-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.kb-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 1px;
  color: #1c2b26;
}

.kb-header-search {
  display: flex;
  align-items: center;
}

.kb-tabs {
  background: #fff;
  padding: 0 24px;
  border-bottom: 1px solid #ebeef5;
}

.kb-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
}

.kb-main {
  flex: 1;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 24px 48px;
  box-sizing: border-box;
}

@media (max-width: 768px) {
  .kb-header {
    flex-direction: column;
    align-items: stretch;
  }
  .kb-header-search .el-input {
    width: 100% !important;
  }
  .kb-title {
    font-size: 17px;
  }
}
</style>
