<template>
  <div class="kb-search">
    <div class="search-head">
      <h2>检索结果</h2>
      <div class="search-meta">
        <span v-if="q">关键词：<b>{{ q }}</b></span>
        <el-switch v-model="semantic" active-text="语义排序" @change="load" style="margin-right:14px" />
        <el-select
          v-model="typeFilter"
          placeholder="全部类型"
          clearable
          style="width: 140px"
          @change="load"
        >
          <el-option v-for="t in KB_TYPES" :key="t.key" :label="t.label" :value="t.key" />
        </el-select>
      </div>
    </div>

    <div v-loading="loading">
      <template v-if="grouped.length">
        <section v-for="g in grouped" :key="g.type" class="result-group">
          <h3 class="group-title">
            {{ g.icon }} {{ g.label }}
            <el-tag size="small" type="info" round>{{ g.items.length }}</el-tag>
          </h3>
          <div
            v-for="r in g.items"
            :key="`${r.type}-${r.id}`"
            class="result-item"
            @click="open(r)"
          >
            <div class="result-name">{{ displayName(g.type, r) }}</div>
            <div class="result-module">{{ MODULE_MAP[r.module] || r.module || '—' }}</div>
            <div class="result-snippet" v-html="highlight(r.snippet || '')"></div>
          </div>
        </section>
      </template>
      <el-empty v-else-if="!loading" :description="q ? '未检索到相关内容' : '请输入关键词开始检索'" />
    </div>
  </div>
</template>

<script setup>
const semantic = ref(false)
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { searchKb } from '@/api/kb'
import { KB_TYPES, TYPE_MAP, MODULE_MAP, displayName } from './config'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const results = ref([])
const typeFilter = ref('')

const q = computed(() => route.query.q || '')

const grouped = computed(() => {
  const order = KB_TYPES.map((t) => t.key)
  const groups = []
  for (const t of order) {
    const items = results.value.filter((r) => r.type === t)
    if (items.length) groups.push({ type: t, icon: TYPE_MAP[t].icon, label: TYPE_MAP[t].label, items })
  }
  return groups
})

function highlight(text) {
  if (!text) return ''
  const s = String(text)
  const kw = q.value.trim()
  if (!kw) return escapeHtml(s)
  try {
    const escaped = escapeHtml(s)
    const pattern = new RegExp(`(${escapeRegExp(escapeHtml(kw))})`, 'gi')
    return escaped.replace(pattern, '<mark>$1</mark>')
  } catch (e) {
    return escapeHtml(s)
  }
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
}

function escapeRegExp(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function open(r) {
  router.push(`/kb/${r.type}/${r.id}`)
}

async function load() {
  const kw = q.value.trim()
  if (!kw) {
    results.value = []
    return
  }
  loading.value = true
  try {
    const res = await searchKb({ q: kw, type: typeFilter.value || undefined, semantic: semantic.value ? 1 : 0 })
    results.value = res?.results || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

watch(
  () => route.query.q,
  () => { typeFilter.value = ''; load() },
  { immediate: true }
)
</script>

<style scoped>
.search-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
}

.search-head h2 {
  margin: 0;
  font-size: 20px;
  color: #1c2b26;
}

.search-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #909399;
  font-size: 13px;
}

.result-group {
  margin-bottom: 24px;
}

.group-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 10px;
  font-size: 16px;
  color: #1c2b26;
}

.result-item {
  background: #fff;
  border: 1px solid #e7e3da;
  border-radius: 10px;
  padding: 12px 16px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: box-shadow 0.15s, border-color 0.15s;
}

.result-item:hover {
  box-shadow: 0 6px 18px rgba(30, 34, 39, 0.08);
  border-color: #409eff;
}

.result-name {
  font-size: 15px;
  font-weight: 600;
  color: #1c2b26;
}

.result-module {
  display: inline-block;
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

.result-snippet {
  margin-top: 6px;
  font-size: 13px;
  color: #6b7077;
  line-height: 1.7;
}

.result-snippet :deep(mark) {
  background: #fde68a;
  color: #92400e;
  padding: 0 2px;
  border-radius: 2px;
}
</style>
