<template>
  <div>
    <h1 class="page-title">中国炼丹术时间线</h1>
    <div class="page-sub">从战国方士到现代——两千年炼丹术兴衰脉络（据上篇总论与附录记事年表整理）</div>

    <div class="pill-row">
      <el-input v-model="kw" placeholder="按朝代/关键词筛选…" clearable size="small" style="max-width:260px" />
    </div>

    <div style="margin-top:16px">
      <div v-for="(t, i) in filtered" :key="i" class="tl-item">
        <div class="tl-year">{{ t.year }}</div>
        <div class="tl-text">{{ t.event }}</div>
        <div class="tl-src">出处：{{ t.source }}</div>
      </div>
    </div>
    <div v-if="!filtered.length" class="card" style="text-align:center;color:#9a8a6c">暂无匹配条目</div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import timeline from '../data/timeline.json'

const kw = ref('')
const filtered = computed(() =>
  timeline.timeline.filter(
    (t) => !kw.value || (t.year + t.event + t.source).includes(kw.value.trim())
  )
)
</script>
