<template>
  <div>
    <h1 class="page-title">炼丹术语表</h1>
    <div class="page-sub">第六章「中国炼丹术的术语」及全书术语汇编 · 共 {{ terms.length }} 条</div>
    <el-input v-model="kw" placeholder="搜索术语…" clearable style="margin-bottom:14px" />
    <div v-for="t in filtered" :key="t.term" class="card" style="padding:10px 14px">
      <strong style="color:var(--dan-red)">{{ t.term }}</strong>
      <span v-if="t.page" style="float:right;font-size:0.72rem;color:#b9a87e">原书第 {{ t.page }} 页</span>
      <div style="font-size:0.9rem;margin-top:4px">{{ t.definition }}</div>
    </div>
    <div v-if="!filtered.length" class="card" style="text-align:center;color:#9a8a6c">暂无匹配术语</div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import glossary from '../data/glossary.json'

const kw = ref('')
const terms = glossary.terms
const filtered = computed(() =>
  terms.filter((t) => !kw.value || (t.term + t.definition).includes(kw.value.trim()))
)
</script>
