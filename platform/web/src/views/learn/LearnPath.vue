<template>
  <div class="lp-page">
    <div class="lp-body">
      <p class="lp-desc">{{ path.desc }}</p>

      <el-card v-for="(it, idx) in path.items" :key="it.key" shadow="never" class="item-card" :class="{ done: isDone(it.key) }">
        <div class="item-head">
          <span class="idx">{{ idx + 1 }}</span>
          <div class="item-info">
            <div class="item-line">
              <el-tag size="small" :type="it.resolved ? 'primary' : 'danger'">{{ TYPE_NAMES[it.type] || it.type }}</el-tag>
              <b style="margin-left:6px">{{ it.name }}</b>
              <span class="mod">{{ MODULES[it.module] || '跨科' }}</span>
            </div>
            <div class="item-note">{{ it.note }}</div>
          </div>
          <div class="item-ops">
            <el-button v-if="it.resolved" size="small" @click="openCard(it)">🃏 学习卡</el-button>
            <el-button v-if="it.resolved" size="small" type="primary" plain @click="router.push('/kb/' + it.type + '/' + it.id)">总库详情</el-button>
            <el-checkbox :model-value="isDone(it.key)" @change="toggle(it)" :disabled="!it.resolved">
              {{ isDone(it.key) ? '已学 ✓' : '标记已学' }}
            </el-checkbox>
          </div>
        </div>
      </el-card>

      <el-dialog v-model="cardVisible" :title="card?.front" width="min(520px, 94vw)">
        <div v-if="card" class="card-back">
          <div class="card-front-label">{{ TYPE_NAMES[card.type] }} · {{ MODULES[card.module] || '跨科' }}</div>
          <pre class="back-text">{{ card.back }}</pre>
          <div v-if="card.source" class="card-src">出处:{{ card.source }}</div>
          <el-button type="primary" plain style="margin-top:12px" @click="router.push('/kb/' + card.type + '/' + card.id)">打开总库详情</el-button>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { learnPaths, getProgress, saveProgress, getCard } from '@/api/learn'

const router = useRouter()
const route = useRoute()
const MODULES = { surgery: '外科疮疡', anorectal: '肛肠痔漏', pediatrics: '儿科', alchemy: '丹药研究' }
const TYPE_NAMES = { formulas: '方剂', herbs: '中药', diseases: '病种', syndromes: '证型', cases: '医案', tips: '要诀', terms: '术语', dulong: '引药' }

const path = ref({ items: [] })
const done = ref([])
const card = ref(null)
const cardVisible = ref(false)

const pct = computed(() => {
  const resolved = (path.value.items || []).filter(i => i.resolved).length
  return resolved ? Math.round((done.value.length / resolved) * 100) : 0
})

onMounted(async () => {
  const paths = (await learnPaths()).paths || []
  path.value = paths.find(p => p.id === route.params.id) || { items: [] }
  const g = await getProgress({ path_id: route.params.id })
  done.value = (g.items?.[0]?.done) || []
})

const isDone = (key) => done.value.includes(key)
async function toggle(it) {
  const res = await saveProgress({ path_id: route.params.id, item_key: it.key, done: !isDone(it.key) })
  done.value = res.done || []
}
async function openCard(it) {
  try {
    const c = await getCard({ type: it.type, name: it.name })
    card.value = c
    cardVisible.value = true
  } catch (e) { console.error(e) }
}
</script>

<style scoped>
.lp-page { min-height: 100vh; background: #f5f7fa; }
.lp-topbar { display: flex; align-items: center; gap: 18px; padding: 12px 24px; background: #fff; border-bottom: 1px solid #e8e8e8; }
.lp-title { font-weight: 700; font-size: 16px; }
.lp-body { max-width: 900px; margin: 0 auto; padding: 20px 16px; }
.lp-desc { color: #5c6b73; background: #f0f7f1; border-radius: 8px; padding: 10px 14px; }
.item-card { margin-bottom: 10px; }
.item-card.done { border-left: 4px solid #67c23a; }
.item-head { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.idx { width: 26px; height: 26px; border-radius: 50%; background: #eef2f6; color: #556; display: flex; align-items: center; justify-content: center; font-size: 13px; flex-shrink: 0; }
.item-info { flex: 1; }
.item-note { color: #8a94a0; font-size: 12.5px; margin-top: 3px; }
.item-ops { display: flex; gap: 8px; align-items: center; flex-shrink: 0; }
@media (max-width: 768px) { .item-ops { width: 100%; justify-content: flex-start; margin-top: 6px; } }
.mod { margin-left: 8px; color: #a0a8b0; font-size: 12px; }
.card-back { padding: 4px 8px; }
.card-front-label { color: #909399; font-size: 12px; margin-bottom: 6px; }
.back-text { white-space: pre-wrap; font-family: inherit; font-size: 14px; line-height: 1.9; background: #f8f9fa; border-radius: 8px; padding: 12px; margin: 0; }
.card-src { color: #a0a8b0; font-size: 12px; margin-top: 6px; }
</style>
