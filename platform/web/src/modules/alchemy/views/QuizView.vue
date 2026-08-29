<template>
  <div>
    <h1 class="page-title">知识测验</h1>
    <div class="page-sub">共 {{ quiz.length }} 题 · 测试你对炼丹术历史、理论与安全知识的掌握</div>

    <div v-if="!started" class="card" style="text-align:center;padding:28px 16px">
      <div style="font-size:2rem;margin-bottom:10px">✍️</div>
      <p style="color:#6b5c42">题目涵盖历史源流、炼丹理论、方剂类别与安全知识。</p>
      <el-button type="danger" size="large" @click="start">开始测验</el-button>
    </div>

    <template v-else-if="cur < quiz.length">
      <div class="card">
        <div style="display:flex;justify-content:space-between;color:#8a7a60;font-size:0.8rem">
          <span>第 {{ cur + 1 }} / {{ quiz.length }} 题</span>
          <span>得分 {{ score }}</span>
        </div>
        <el-progress :percentage="Math.round((cur / quiz.length) * 100)" :show-text="false" style="margin:8px 0" />
        <h3 style="color:var(--dan-ink)">{{ quiz[cur].q }}</h3>
        <button v-for="(o, i) in quiz[cur].options" :key="i" class="quiz-option"
                :class="optClass(i)" :disabled="answered !== null"
                @click="choose(i)">
          {{ ['A', 'B', 'C', 'D'][i] }}. {{ o }}
        </button>
        <div v-if="answered !== null" style="margin-top:10px">
          <div :style="answered === quiz[cur].answer ? 'color:#2f5d26' : 'color:#8a2f2f'">
            {{ answered === quiz[cur].answer ? '✅ 回答正确' : '❌ 回答错误' }}
          </div>
          <div style="font-size:0.85rem;color:#6b5c42;margin-top:6px">💡 {{ quiz[cur].explain }}</div>
          <el-button type="danger" plain style="margin-top:12px" @click="nextQ">
            {{ cur + 1 < quiz.length ? '下一题' : '查看结果' }}
          </el-button>
        </div>
      </div>
    </template>

    <div v-else class="card" style="text-align:center;padding:28px 16px">
      <div style="font-size:2rem">🏆</div>
      <h2>得分：{{ score }} / {{ quiz.length }}</h2>
      <p style="color:#6b5c42">{{ verdict }}</p>
      <el-button type="danger" @click="start">再测一次</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import data from '../data/quiz.json'

const quiz = data.quiz
const started = ref(false)
const cur = ref(0)
const score = ref(0)
const answered = ref(null)

const verdict = computed(() => {
  const r = score.value / quiz.length
  if (r >= 0.9) return '精通！你对炼丹术的认知已经相当全面。'
  if (r >= 0.7) return '良好，建议再浏览总论章节与方剂库巩固。'
  if (r >= 0.5) return '及格，历史与安全知识还需加强。'
  return '建议从「总论 · 源流」开始系统阅读。'
})

function start() {
  started.value = true
  cur.value = 0
  score.value = 0
  answered.value = null
}
function choose(i) {
  if (answered.value !== null) return
  answered.value = i
  if (i === quiz[cur.value].answer) score.value++
}
function nextQ() {
  cur.value++
  answered.value = null
}
function optClass(i) {
  if (answered.value === null) return ''
  if (i === quiz[cur.value].answer) return 'correct'
  if (i === answered.value) return 'wrong'
  return ''
}
</script>
