<template>
  <div>
    <h1 class="page-title">安全与法规</h1>
    <div class="page-sub">现代法规、毒理与中毒救治要点 · 依据官方来源整理</div>

    <div class="safety-banner">
      <strong>⚠️ 核心声明：</strong>丹药（轻粉、粉霜、白降丹、三仙丹、红升丹、灵砂、银朱等）多为汞、砷剧毒化合物制剂，
      现代已严格限制或淘汰使用。本系统保留原书临床用法原文，<strong>仅为中医外科专业学术研究参考</strong>。
      <strong>严禁自行配制、严禁内服、严禁用于任何非专业用途。</strong>
    </div>

    <div class="card md-body" v-html="html"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'

const mdFiles = import.meta.glob('../data/chapters/*.md', { query: '?raw', import: 'default', eager: true })
const html = computed(() => {
  const raw = mdFiles['../data/chapters/safety.md']
  if (!raw) return '<p style="color:#9a8a6c">安全与法规篇整理中（法规调研完成后载入）。核心要求：丹药为剧毒化合物，严禁自行配制、严禁内服，临床须遵循现行药事法规。</p>'
  return marked.parse(raw)
})
</script>
