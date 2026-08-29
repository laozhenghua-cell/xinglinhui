<template>
  <div v-if="f">
    <h1 class="page-title">{{ f.name }}</h1>
    <div class="page-sub">
      <span class="tag red">{{ f.category }}</span>
      <span class="tag gold">{{ f.method }}</span>
      <span v-if="f.page">原书第 {{ f.page }} 页</span>
      <span v-if="f.aliases && f.aliases.length">别名：{{ f.aliases.join('、') }}</span>
    </div>

    <div class="safety-banner">
      <strong>⚠️ 现代安全警示：</strong>{{ f.safetyNote }}
    </div>

    <el-descriptions :column="isMobile ? 1 : 2" border size="small" style="margin-bottom:14px">
      <el-descriptions-item label="组成">
        <div v-for="(c, i) in f.composition" :key="i">{{ c.drug }}　{{ c.amount }}</div>
      </el-descriptions-item>
      <el-descriptions-item label="炼制法" :span="isMobile ? 1 : 1">{{ f.process }}</el-descriptions-item>
      <el-descriptions-item label="理化性状">{{ f.appearance }}</el-descriptions-item>
      <el-descriptions-item label="功效">{{ f.efficacy }}</el-descriptions-item>
      <el-descriptions-item label="主治" :span="isMobile ? 1 : 2">{{ f.indications }}</el-descriptions-item>
      <el-descriptions-item label="用法用量" :span="isMobile ? 1 : 2">{{ f.usage }}</el-descriptions-item>
      <el-descriptions-item label="禁忌" :span="isMobile ? 1 : 2">{{ f.contraindications }}</el-descriptions-item>
    </el-descriptions>

    <div class="card">
      <h3 style="margin-top:0">📜 原书原文</h3>
      <div style="white-space:pre-wrap;font-family:var(--font-serif);font-size:0.95rem">{{ f.originalText }}</div>
    </div>

    <div style="text-align:center;margin-top:16px">
      <el-button @click="$router.back()">← 返回方剂库</el-button>
    </div>
  </div>
  <div v-else class="card">方剂未找到</div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import formulas from '../data/formulas.json'

const route = useRoute()
const f = computed(() => formulas.formulas.find((x) => x.id === route.params.id))

const isMobile = ref(window.innerWidth < 860)
function onResize() { isMobile.value = window.innerWidth < 860 }
onMounted(() => window.addEventListener('resize', onResize))
onUnmounted(() => window.removeEventListener('resize', onResize))
</script>
