<template>
  <div class="ln-page">
    <div class="ln-body">
      <section class="ln-hero">
        <h2>四科合参 · 学用一体</h2>
        <p>六条学习路径(四科入门 + 两条跨科融合专题),把 3,540 条知识变成可学的课程;学完自测,不会就问 AI 助教。</p>
      </section>

      <h3>📚 学习路径</h3>
      <el-row :gutter="14">
        <el-col v-for="p in paths" :key="p.id" :span="8" style="margin-bottom:14px">
          <el-card shadow="hover" class="path-card" @click="router.push('/learn/path/' + p.id)">
            <div class="path-badge" :class="p.module">{{ p.module === 'all' ? '跨科融合' : MODULES[p.module] }}</div>
            <b class="path-title">{{ p.title }}</b>
            <div class="path-desc">{{ p.desc }}</div>
            <el-progress :percentage="pct(p)" :stroke-width="8" style="margin:10px 0" />
            <div class="path-meta">{{ doneOf(p) }}/{{ p.resolved_count }} 已学 · 共 {{ p.total }} 节</div>
          </el-card>
        </el-col>
      </el-row>

      <h3 style="margin-top:22px">⭐ 我的收藏({{ favs.length }})</h3>
      <div v-if="!favs.length" class="empty">还没有收藏——在知识总库详情页点"收藏"即可加入</div>
      <div v-else class="card-grid">
        <div v-for="f in favs" :key="f.id" class="mini-card" @click="router.push('/kb/' + f.type + '/' + f.id)">
          <el-tag size="small">{{ TYPE_NAMES[f.type] || f.type }}</el-tag>
          <b>{{ f.front }}</b>
          <div class="mini-back">{{ f.back.split('\n')[0] }}</div>
        </div>
      </div>

      <h3 style="margin-top:22px">📝 我的笔记({{ notes.length }})</h3>
      <div v-if="!notes.length" class="empty">还没有笔记——在知识总库详情页记下心得</div>
      <el-timeline v-else>
        <el-timeline-item v-for="n in notes" :key="n.id" :timestamp="fmt(n.created_at)">
          <div class="note-line">
            <span>{{ n.content }}</span>
            <el-button link type="danger" size="small" @click="removeNote(n.id)">删除</el-button>
          </div>
        </el-timeline-item>
      </el-timeline>

      <h3 style="margin-top:22px">🎯 自测成绩</h3>
      <div v-if="!history.length" class="empty">还没有自测记录,去 <a @click="router.push('/learn/quiz')" style="color:#409EFF;cursor:pointer">自测</a> 一试身手</div>
      <div v-else class="score-row">
        <el-tag v-for="h in history" :key="h.id" :type="h.score >= 80 ? 'success' : h.score >= 60 ? 'warning' : 'danger'">
          {{ fmt(h.created_at) }} · {{ SCOPE_NAMES[h.scope] || h.scope }} · {{ h.correct }}/{{ h.total }} ({{ h.score }}分)
        </el-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { learnPaths, getProgress, listFavs, listNotes, delNote, quizHistory } from '@/api/learn'

const router = useRouter()
const MODULES = { surgery: '外科疮疡', anorectal: '肛肠痔漏', pediatrics: '儿科', alchemy: '丹药研究' }
const SCOPE_NAMES = { all: '全部', surgery: '疮疡', anorectal: '肛肠', pediatrics: '儿科', alchemy: '丹药' }
const TYPE_NAMES = { formulas: '方剂', herbs: '中药', diseases: '病种', syndromes: '证型', cases: '医案', tips: '要诀', terms: '术语', dulong: '引药' }

const paths = ref([])
const progress = ref({})
const favs = ref([])
const notes = ref([])
const history = ref([])

onMounted(async () => {
  try {
    const [p, g, f, n, h] = await Promise.all([learnPaths(), getProgress({}), listFavs(), listNotes(), quizHistory({ limit: 10 })])
    paths.value = p.paths || []
    for (const it of g.items || []) progress.value[it.path_id] = it.done || []
    favs.value = f.items || []
    notes.value = n.items || []
    history.value = h.items || []
  } catch (e) { console.error(e) }
})
const doneOf = (p) => (progress.value[p.id] || []).length
const pct = (p) => (p.resolved_count ? Math.round((doneOf(p) / p.resolved_count) * 100) : 0)
const fmt = (t) => (t ? String(t).replace('T', ' ').slice(0, 16) : '')
async function removeNote(id) {
  await delNote(id)
  notes.value = (await listNotes()).items || []
}
</script>

<style scoped>
.ln-page { min-height: 100vh; background: #f5f7fa; }
.ln-topbar { display: flex; align-items: center; justify-content: space-between; padding: 12px 24px; background: #fff; border-bottom: 1px solid #e8e8e8; }
.ln-title { font-weight: 700; font-size: 17px; }
.ln-body { max-width: 1200px; margin: 0 auto; padding: 20px 16px; }
.ln-hero { background: linear-gradient(120deg, #f0f7f1, #eef4f7); border-radius: 10px; padding: 22px 24px; margin-bottom: 18px; }
.ln-hero h2 { margin: 0 0 6px; }
.ln-hero p { margin: 0; color: #5c6b73; }
.path-card { cursor: pointer; height: 100%; }
.path-badge { display: inline-block; font-size: 12px; padding: 1px 8px; border-radius: 10px; background: #eef2f6; color: #556; margin-bottom: 6px; }
.path-badge.all { background: #f6eef9; color: #7a4fa0; }
.path-title { font-size: 15px; }
.path-desc { color: #8a94a0; font-size: 12.5px; margin: 6px 0; min-height: 48px; }
.path-meta { color: #909399; font-size: 12px; }
.empty { color: #999; padding: 10px 0; }
.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px; }
.mini-card { background: #fff; border: 1px solid #eee; border-radius: 8px; padding: 10px; cursor: pointer; }
.mini-card b { display: block; margin: 4px 0; }
.mini-back { font-size: 12px; color: #8a94a0; }
.note-line { display: flex; justify-content: space-between; align-items: center; }
.score-row { display: flex; flex-wrap: wrap; gap: 8px; }
</style>
