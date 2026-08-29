<template>
  <div>
    <h1 class="page-title">全文检索</h1>
    <div class="page-sub">检索章节正文、方剂、术语与时间线</div>
    <el-input v-model="kw" placeholder="输入关键词，如：三仙丹 / 升法 / 水银 / 葛洪…" clearable size="large" @input="search" />
    <div v-if="kw.trim().length >= 1" style="margin-top:10px;color:#8a7a60;font-size:0.85rem">
      命中 {{ results.length }} 条
    </div>
    <div style="margin-top:12px">
      <div v-for="(r, i) in results" :key="i" class="card" style="cursor:pointer" @click="open(r)">
        <span class="tag" :class="r.type === '方剂' ? 'red' : 'gold'">{{ r.type }}</span>
        <strong>{{ r.title }}</strong>
        <div style="font-size:0.85rem;color:#6b5c42;margin-top:4px" v-html="escapeHtml(r.snippet)"></div>
      </div>
      <div v-if="kw.trim().length >= 1 && !results.length" class="card" style="text-align:center;color:#9a8a6c">
        未找到相关内容
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import chapters from '../data/chapters.json'
import formulas from '../data/formulas.json'
import glossary from '../data/glossary.json'
import timeline from '../data/timeline.json'

const router = useRouter()
const kw = ref('')
const results = ref([])

const mdFiles = import.meta.glob('../data/chapters/*.md', { query: '?raw', import: 'default', eager: true })
const flat = chapters.parts.flatMap((p) => p.chapters.map((c) => ({ ...c, part: p.part })))

function snippet(text, kwr) {
  const i = text.indexOf(kwr)
  if (i < 0) return text.slice(0, 60)
  const s = Math.max(0, i - 30)
  const seg = text.slice(s, s + 90)
  const hl = seg.replaceAll(kwr, `<span style="background:#f6d27a">${kwr}</span>`)
  return (s > 0 ? '…' : '') + hl + '…'
}

function search() {
  const k = kw.value.trim()
  if (k.length < 1) { results.value = []; return }
  const out = []
  for (const ch of flat) {
    const raw = mdFiles['../data/chapters/' + ch.file] || ''
    const i = raw.indexOf(k)
    if (i >= 0) out.push({ type: '章节', title: ch.no + ' ' + ch.title, snippet: snippet(raw, k), path: '/alchemy/chapter/' + ch.id })
  }
  for (const f of formulas.formulas) {
    const hay = [f.name, ...(f.aliases || []), f.category, f.method, f.efficacy, f.indications, f.originalText].join(' ')
    const i = hay.indexOf(k)
    if (i >= 0) out.push({ type: '方剂', title: f.name, snippet: snippet(hay, k), path: '/alchemy/formula/' + f.id })
  }
  for (const t of glossary.terms) {
    const hay = t.term + t.definition
    if (hay.includes(k)) out.push({ type: '术语', title: t.term, snippet: snippet(hay, k), path: '/alchemy/glossary' })
  }
  for (const t of timeline.timeline) {
    const hay = t.year + t.event + t.source
    if (hay.includes(k)) out.push({ type: '年表', title: t.year, snippet: snippet(hay, k), path: '/alchemy/timeline' })
  }
  results.value = out.slice(0, 60)
}

function open(r) {
  router.push(r.path)
}
function escapeHtml(t) {
  if (!t) return ''
  return String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
}
</script>
