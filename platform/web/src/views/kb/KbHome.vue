<template>
  <div class="kb-home">
    <section class="big-search">
      <h2>检索全平台中医知识</h2>
      <p>方剂、中药、病种、证型、医案、要诀、术语、引药，跨四专科一站式检索</p>
      <el-input
        v-model="q"
        size="large"
        placeholder="输入关键词，如：黄连、乳蛾、托法…"
        clearable
        @keyup.enter="doSearch"
      >
        <template #append>
          <el-button type="primary" @click="doSearch">检索</el-button>
        </template>
      </el-input>
    </section>

    <el-alert
      v-if="moduleFilter"
      class="module-tip"
      type="info"
      :closable="true"
      @close="clearModule"
      show-icon
    >
      <template #title>
        当前聚焦专科：{{ MODULE_MAP[moduleFilter] || moduleFilter }}
        <el-button link type="primary" @click="clearModule">清除筛选</el-button>
      </template>
    </el-alert>

    <section class="count-grid" v-loading="loading">
      <div
        v-for="t in KB_TYPES"
        :key="t.key"
        class="count-card"
        :style="{ '--accent': t.color }"
        @click="goType(t.key)"
      >
        <div class="count-icon">{{ t.icon }}</div>
        <div class="count-num">{{ counts[t.key] ?? 0 }}</div>
        <div class="count-label">{{ t.label }}</div>
      </div>
    </section>

    <section class="module-section">
      <h3 class="section-title">各专科收录</h3>
      <el-row :gutter="16">
        <el-col v-for="m in MODULES" :key="m.key" :xs="12" :sm="12" :md="6">
          <div class="module-card" @click="goModule(m.key)">
            <div class="module-name">{{ m.label }}</div>
            <div class="module-total">{{ moduleTotal(m.key) }}</div>
            <div class="module-sub">条内容</div>
          </div>
        </el-col>
      </el-row>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getKbStats } from '@/api/kb'
import { KB_TYPES, MODULES, MODULE_MAP } from './config'

const route = useRoute()
const router = useRouter()
const q = ref('')
const loading = ref(false)
const stats = ref(null)

const counts = computed(() => stats.value?.counts || {})
const byModule = computed(() => stats.value?.by_module || {})

const moduleFilter = computed(() => route.query.module || '')

function doSearch() {
  const kw = q.value.trim()
  router.push({ path: '/kb/search', query: kw ? { q: kw } : {} })
}

function goType(type) {
  const m = moduleFilter.value
  router.push({ path: `/kb/${type}`, query: m ? { module: m } : {} })
}

function goModule(m) {
  router.push({ path: '/kb', query: { module: m } })
}

function clearModule() {
  const query = { ...route.query }
  delete query.module
  router.replace({ path: '/kb', query })
}

function moduleTotal(key) {
  const m = byModule.value[key] || {}
  return Object.values(m).reduce((a, b) => a + (Number(b) || 0), 0)
}

onMounted(async () => {
  loading.value = true
  try {
    stats.value = await getKbStats()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.big-search {
  text-align: center;
  padding: 28px 0 24px;
}

.big-search h2 {
  margin: 0 0 8px;
  font-size: 26px;
  color: #1c2b26;
  letter-spacing: 1px;
}

.big-search p {
  margin: 0 0 20px;
  color: #909399;
  font-size: 14px;
}

.big-search .el-input {
  max-width: 640px;
  margin: 0 auto;
}

.module-tip {
  margin-bottom: 16px;
}

.count-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 16px;
  margin: 12px 0 32px;
}

.count-card {
  background: #fff;
  border: 1px solid #e7e3da;
  border-radius: 12px;
  padding: 22px 12px;
  text-align: center;
  cursor: pointer;
  transition: transform 0.16s, box-shadow 0.16s, border-color 0.16s;
}

.count-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 24px rgba(30, 34, 39, 0.1);
  border-color: var(--accent);
}

.count-icon {
  font-size: 28px;
  margin-bottom: 8px;
}

.count-num {
  font-size: 28px;
  font-weight: 700;
  color: var(--accent);
  line-height: 1.2;
}

.count-label {
  font-size: 14px;
  color: #6b7077;
  margin-top: 4px;
}

.section-title {
  margin: 0 0 14px;
  font-size: 17px;
  color: #1c2b26;
}

.module-card {
  background: #fff;
  border: 1px solid #e7e3da;
  border-radius: 12px;
  padding: 18px 12px;
  text-align: center;
  cursor: pointer;
  margin-bottom: 12px;
  transition: box-shadow 0.16s, border-color 0.16s;
}

.module-card:hover {
  box-shadow: 0 8px 20px rgba(30, 34, 39, 0.1);
  border-color: #409eff;
}

.module-name {
  font-size: 14px;
  font-weight: 600;
  color: #1c2b26;
}

.module-total {
  font-size: 26px;
  font-weight: 700;
  color: #409eff;
  margin-top: 6px;
}

.module-sub {
  font-size: 12px;
  color: #b0b3b8;
}
</style>
