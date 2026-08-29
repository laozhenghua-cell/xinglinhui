<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { doSearch, searchCategories, type SearchRecord } from '../data/searchIndex'

const router = useRouter()
const q = ref('')
const cat = ref('全部')
const results = computed(() => {
  const rs = doSearch(q.value, 80)
  return cat.value === '全部' ? rs : rs.filter((r) => r.cat === cat.value)
})

/** 高亮命中词（转义后包裹 <mark>） */
function esc(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}
function highlight(rec: SearchRecord): string {
  const terms = q.value.trim().split(/\s+/).filter(Boolean)
  // 取标题 + 正文前段，截取包含关键词的片段
  let text = `${rec.title}。${rec.text.replace(/\n/g, ' ')}`
  const idx = terms.length ? Math.max(...terms.map((t) => text.indexOf(t)).filter((i) => i >= 0)) : -1
  let start = idx > 40 ? idx - 40 : 0
  if (idx < 0) start = 0
  let snippet = text.slice(start, start + 160)
  if (start > 0) snippet = '…' + snippet
  if (start + 160 < text.length) snippet += '…'
  snippet = esc(snippet)
  for (const t of terms) {
    if (!t) continue
    const et = esc(t)
    snippet = snippet.split(et).join(`<mark>${et}</mark>`)
  }
  return snippet
}

function go(rec: SearchRecord) {
  router.push('/pediatrics' + rec.route)
  q.value = ''
}
</script>

<template>
  <div class="page">
    <div class="h-title" style="font-size: 26px">全文检索</div>
    <p class="vern" style="margin-top: 6px">
      检索全书内容：八症、方剂、纹形、诊法、用药、死候、训诫、推拿、医案、三症、题库。
      多个词以空格分隔（如"风热 泻青黄"）。
    </p>

    <div class="card no-print">
      <el-input v-model="q" size="large" placeholder="如：浮萍 / 透关射甲 / 贴脐 / 天保采薇汤 / 死候…" clearable class="search-input" />
      <div class="cats">
        <el-radio-group v-model="cat" size="small">
          <el-radio-button value="全部">全部</el-radio-button>
          <el-radio-button v-for="c in searchCategories" :key="c" :value="c">{{ c }}</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <div v-if="q" class="result-count">共 {{ results.length }} 条</div>
    <div v-for="r in results" :key="r.id" class="card result" @click="go(r)">
      <div class="r-head">
        <span class="tag-syndrome">{{ r.cat }}</span>
        <b class="r-title">{{ r.title }}</b>
      </div>
      <div class="r-snippet" v-html="highlight(r)" />
    </div>
    <p v-if="q && !results.length" class="vern" style="text-align: center; padding: 30px 0">
      无匹配结果，试试更换关键词（如"泻""惊""灯火"）。
    </p>
    <p v-if="!q" class="vern" style="text-align: center; padding: 30px 0; color: #a0845a">
      输入关键词开始检索全书
    </p>
  </div>
</template>

<style scoped>
.search-input {
  max-width: 560px;
}
.cats {
  margin-top: 12px;
}
.result-count {
  margin: 12px 2px;
  color: var(--jade);
  font-size: 13px;
}
.result {
  cursor: pointer;
  transition: box-shadow 0.15s;
}
.result:hover {
  box-shadow: 0 6px 18px rgba(43, 35, 24, 0.16);
}
.r-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.r-title {
  font-family: var(--font-kai);
  font-size: 15.5px;
  color: var(--ink);
}
.r-snippet {
  font-size: 13px;
  color: var(--ink-soft);
  line-height: 1.9;
}
.r-snippet :deep(mark) {
  background: #f8e3b7;
  color: var(--vermilion);
  border-radius: 2px;
  padding: 0 2px;
}
</style>
