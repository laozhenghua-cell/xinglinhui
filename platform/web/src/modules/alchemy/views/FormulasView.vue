<template>
  <div>
    <h1 class="page-title">丹药方剂库</h1>
    <div class="page-sub">下篇各论所载秘验方剂 · 共 {{ formulas.formulas.length }} 方</div>
    <div class="safety-banner">
      <strong>⚠️</strong> 全部方剂均为汞、砷剧毒化合物制剂。此处保留原书主治用法原文仅供专业研究，<strong>严禁自行配制、严禁内服</strong>。
    </div>

    <div class="pill-row">
      <span class="filter-pill" :class="{ active: cat === '' }" @click="cat = ''">全部类型</span>
      <span v-for="c in cats" :key="c" class="filter-pill" :class="{ active: cat === c }" @click="cat = c">{{ c }}</span>
    </div>
    <div class="pill-row">
      <span class="filter-pill" :class="{ active: method === '' }" @click="method = ''">全部炼法</span>
      <span v-for="m in methods" :key="m" class="filter-pill" :class="{ active: method === m }" @click="method = m">{{ m }}</span>
    </div>

    <div v-for="f in filtered" :key="f.id" class="card" style="cursor:pointer" @click="$router.push('/alchemy/formula/' + f.id)">
      <div style="display:flex;align-items:baseline;gap:8px;flex-wrap:wrap">
        <strong style="font-size:1.1rem">{{ f.name }}</strong>
        <span class="tag red">{{ f.category }}</span>
        <span class="tag gold">{{ f.method }}</span>
      </div>
      <div style="font-size:0.8rem;color:#9a8a6c;margin:4px 0" v-if="f.aliases && f.aliases.length">
        别名：{{ f.aliases.join('、') }}
      </div>
      <div style="font-size:0.9rem;color:#5c5240" class="clamp-2">{{ f.efficacy }}</div>
      <div style="font-size:0.75rem;color:#b35309;margin-top:6px">⚠️ {{ f.safetyNote.slice(0, 60) }}…</div>
    </div>
    <div v-if="!filtered.length" class="card" style="text-align:center;color:#9a8a6c">
      该筛选下暂无方剂（方剂数据随全书校对转录逐步载入）
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import formulas from '../data/formulas.json'

const cat = ref('')
const method = ref('')
const cats = computed(() => [...new Set(formulas.formulas.map((f) => f.category))])
const methods = computed(() => [...new Set(formulas.formulas.map((f) => f.method))])
const filtered = computed(() =>
  formulas.formulas.filter(
    (f) => (!cat.value || f.category === cat.value) && (!method.value || f.method === method.value)
  )
)
</script>

<style scoped>
.clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
