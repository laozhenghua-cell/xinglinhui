<script setup lang="ts">
import { ref, computed } from 'vue'
import { quizBank, loadWrongIds, saveWrongIds, loadStats, saveStats } from '../data/quiz'

const categories = ['全部', ...new Set(quizBank.map((q) => q.category))]
const cat = ref('全部')
const mode = ref<'all' | 'wrong'>('all')
const wrongIds = ref<Set<string>>(new Set(loadWrongIds()))
const stats = ref(loadStats())

const pool = computed(() => {
  const base = cat.value === '全部' ? quizBank : quizBank.filter((q) => q.category === cat.value)
  if (mode.value === 'wrong') return base.filter((q) => wrongIds.value.has(q.id))
  return base
})

// 抽题模式：随机 10 题
const started = ref(false)
const questions = ref<typeof quizBank>([])
const answers = ref<Record<string, number[]>>({})
const submitted = ref(false)
const score = ref(0)

function start() {
  const p = [...pool.value]
  const shuffled = p.sort(() => Math.random() - 0.5).slice(0, 10)
  questions.value = shuffled
  answers.value = {}
  submitted.value = false
  score.value = 0
  started.value = true
  window.scrollTo({ top: 0 })
}

function toggle(qid: string, idx: number) {
  if (submitted.value) return
  const q = questions.value.find((x) => x.id === qid)!
  const cur = answers.value[qid] ?? []
  if (q.type === 'single') {
    answers.value[qid] = [idx]
  } else {
    answers.value[qid] = cur.includes(idx) ? cur.filter((i) => i !== idx) : [...cur, idx]
  }
}

function submit() {
  submitted.value = true
  let right = 0
  for (const q of questions.value) {
    const a = answers.value[q.id] ?? []
    const ok = a.length === q.answer.length && q.answer.every((i) => a.includes(i))
    if (ok) right++
    else wrongIds.value.add(q.id)
    elseWrong(q.id, ok)
    const st = stats.value[q.category] ?? { done: 0, right: 0 }
    st.done++
    if (ok) st.right++
    stats.value[q.category] = st
  }
  score.value = right
  saveWrongIds([...wrongIds.value])
  saveStats(stats.value)
}

function elseWrong(qid: string, ok: boolean) {
  if (ok) wrongIds.value.delete(qid)
}

function isRight(qid: string, idx: number): boolean | null {
  if (!submitted.value) return null
  const q = questions.value.find((x) => x.id === qid)!
  const chosen = (answers.value[qid] ?? []).includes(idx)
  const correct = q.answer.includes(idx)
  if (correct) return true
  if (chosen) return false
  return null
}
</script>

<template>
  <div class="page">
    <div class="h-title" style="font-size: 26px">自测练习</div>
    <p class="vern" style="margin-top: 6px">
      题库共 {{ quizBank.length }} 题，全部出自原著。每次随机抽取 10 题，错题自动收入错题本。
    </p>

    <div class="card no-print">
      <div class="filters">
        <el-select v-model="cat" style="width: 200px">
          <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
        </el-select>
        <el-radio-group v-model="mode">
          <el-radio-button value="all">全部题目</el-radio-button>
          <el-radio-button value="wrong">错题本（{{ wrongIds.size }} 题）</el-radio-button>
        </el-radio-group>
        <el-button type="primary" @click="start" :disabled="pool.length === 0">
          {{ started ? '重新抽题' : '开始自测（随机 10 题）' }}
        </el-button>
        <span class="vern" v-if="pool.length === 0 && mode === 'wrong'">错题本为空，先去答题吧</span>
      </div>
      <div v-if="started" class="progress">
        本次答题：{{ questions.length }} 题
        <template v-if="submitted"> · 得分 {{ score }} / {{ questions.length }}</template>
      </div>
    </div>

    <div v-if="started" class="quiz-list">
      <div v-for="(q, qi) in questions" :key="q.id" class="card">
        <div class="q-head">
          <span class="q-no">{{ qi + 1 }}</span>
          <span class="tag-syndrome">{{ q.category }}</span>
          <span class="q-text">{{ q.question }}</span>
          <span class="q-type">{{ q.type === 'single' ? '单选' : '多选' }}</span>
        </div>
        <div class="opts">
          <div v-for="(o, oi) in q.options" :key="oi" class="opt" :class="{ right: isRight(q.id, oi) === true, wrong: isRight(q.id, oi) === false }" @click="toggle(q.id, oi)">
            <span class="opt-mark">{{ String.fromCharCode(65 + oi) }}</span>
            <span>{{ o }}</span>
            <span v-if="isRight(q.id, oi) === true" class="opt-flag">✓</span>
            <span v-if="isRight(q.id, oi) === false" class="opt-flag">✗</span>
          </div>
        </div>
        <div v-if="submitted" class="explain">
          <b>解：</b>{{ q.explain }}
          <span v-if="q.source" class="src">（出处：{{ q.source }}）</span>
        </div>
      </div>
    </div>

    <div v-if="started && !submitted" class="no-print" style="margin: 16px 0 40px">
      <el-button type="primary" size="large" @click="submit">交卷评分</el-button>
    </div>
    <div v-if="submitted" class="no-print" style="margin: 16px 0 40px">
      <el-button type="primary" size="large" @click="start">再练一组</el-button>
    </div>

    <div v-if="started" class="h-sec">分类成绩</div>
    <el-row v-if="started" :gutter="12">
      <el-col v-for="c in categories.filter((x) => x !== '全部' && stats[x])" :key="c" :xs="12" :md="6">
        <div class="card stat">
          <b>{{ c }}</b>
          <span>已答 {{ stats[c].done }} · 正确 {{ stats[c].right }}</span>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.filters {
  display: flex;
  gap: 14px;
  align-items: center;
  flex-wrap: wrap;
}
.progress {
  margin-top: 12px;
  color: var(--jade);
  font-size: 13.5px;
}
.q-head {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}
.q-no {
  display: inline-flex;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--vermilion);
  color: #fdf6e8;
  align-items: center;
  justify-content: center;
  font-size: 13px;
}
.q-text {
  font-weight: 600;
  font-size: 15px;
  color: var(--ink);
}
.q-type {
  margin-left: auto;
  font-size: 11.5px;
  color: #a0845a;
}
.opts {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.opt {
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 8px 12px;
  cursor: pointer;
  transition: background 0.12s;
  font-size: 14px;
}
.opt:hover {
  background: #f3ecdd;
}
.opt.right {
  background: #eef6f0;
  border-color: #4a7a5f;
}
.opt.wrong {
  background: var(--danger-bg);
  border-color: var(--danger-line);
}
.opt-mark {
  font-weight: 700;
  color: var(--vermilion);
}
.opt-flag {
  margin-left: auto;
  font-weight: 700;
}
.opt.right .opt-flag {
  color: #4a7a5f;
}
.opt.wrong .opt-flag {
  color: #c0392b;
}
.explain {
  margin-top: 10px;
  background: var(--paper-light);
  border: 1px dashed var(--line);
  border-radius: 6px;
  padding: 10px 12px;
  font-size: 13px;
  line-height: 1.8;
  color: var(--ink-soft);
}
.src {
  color: #a0845a;
  font-size: 12px;
}
.stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
  color: var(--ink-soft);
}
</style>
