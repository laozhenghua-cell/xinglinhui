<template>
  <div>
    <div v-if="chapter">
      <h1 class="page-title">{{ chapter.no }} {{ chapter.title }}</h1>
      <div class="page-sub">{{ partName }} · 原书第 {{ pagesText }} 页</div>
      <div class="safety-banner" v-if="chapter.id === 'ch07' || chapter.id === 'ch08' || chapter.id === 'ch09' || chapter.id === 'ch10'">
        <strong>⚠️</strong> 本章所载为剧毒汞化合物制剂的炼制与用法原文。仅供专业研究，严禁自行配制、严禁内服。
      </div>
      <div class="card md-body" v-html="html"></div>
      <div style="text-align:center;margin:18px 0">
        <el-button-group>
          <el-button :disabled="!prev" @click="go(prev)">← 上一章</el-button>
          <el-button :disabled="!next" @click="go(next)">下一章 →</el-button>
        </el-button-group>
      </div>
    </div>
    <div v-else class="card">章节未找到</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import chapters from '../data/chapters.json'

const route = useRoute()
const router = useRouter()

const mdFiles = import.meta.glob('../data/chapters/*.md', { query: '?raw', import: 'default', eager: true })

const flat = chapters.parts.flatMap((p) => p.chapters.map((c) => ({ ...c, part: p.part })))
const chapter = computed(() => flat.find((c) => c.id === route.params.id))
const idx = computed(() => flat.findIndex((c) => c.id === route.params.id))
const prev = computed(() => (idx.value > 0 ? flat[idx.value - 1] : null))
const next = computed(() => (idx.value >= 0 && idx.value < flat.length - 1 ? flat[idx.value + 1] : null))
const partName = computed(() => chapter.value?.part || '')
const pagesText = computed(() => (chapter.value?.bookPages?.length ? chapter.value.bookPages.join('、') : '待校'))

const html = computed(() => {
  if (!chapter.value) return ''
  const key = '../data/chapters/' + chapter.value.file
  const raw = mdFiles[key]
  if (!raw) return '<p style="color:#9a8a6c">本章内容整理中（全书逐页校对转录完成后载入）。</p>'
  return marked.parse(raw)
})

function go(c) {
  if (c) router.push('/alchemy/chapter/' + c.id)
}
</script>
