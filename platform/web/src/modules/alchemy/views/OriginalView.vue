<template>
  <div>
    <h1 class="page-title">原书对照</h1>
    <div class="page-sub">扫描原页图像 · 逐页忠实转录 · 共 {{ pages.length }} 页</div>
    <div class="safety-banner"><strong>⚠️</strong> 原书图像仅作史料对照用。</div>

    <div class="pill-row">
      <el-input v-model="kw" placeholder="输入页码或书页号，如 5 / 72" clearable size="small" style="max-width:220px" @input="onKw" />
      <span style="font-size:0.8rem;color:#8a7a60;align-self:center">
        共 {{ filtered.length }} 页 · 已转录 {{ transcribed }} 页
      </span>
    </div>

    <!-- 分页控件 -->
    <div v-if="filtered.length > PAGE_SIZE" class="card" style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:10px 14px">
      <el-button size="small" :disabled="pageNum <= 1" @click="pageNum--">← 上一页</el-button>
      <span style="font-size:0.85rem">
        第 {{ pageNum }} / {{ totalPages }} 组（第 {{ rangeStart }}–{{ rangeEnd }} 页）
      </span>
      <el-button size="small" :disabled="pageNum >= totalPages" @click="pageNum++">下一页 →</el-button>
      <el-input-number v-model="pageNum" :min="1" :max="totalPages" size="small" style="width:90px" @change="pageNum = Math.min(Math.max(pageNum,1), totalPages)" />
    </div>

    <div v-for="p in paged" :key="p.pdf" class="card" style="padding:10px">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
        <span style="font-size:0.9rem">
          PDF 第 {{ p.pdf }} 页
          <span v-if="p.book" style="color:#b9a87e">· 书页：{{ p.book }}</span>
          <span v-if="!p.chars" class="tag" style="margin-left:6px">纯图像</span>
        </span>
      </div>
      <img :src="imgPath(p)" loading="lazy" class="original-page-img" alt="原书第{{ p.pdf }}页" />
    </div>

    <div v-if="filtered.length > PAGE_SIZE" style="text-align:center;margin-top:14px">
      <el-button-group>
        <el-button :disabled="pageNum <= 1" @click="pageNum--">← 上一组</el-button>
        <el-button :disabled="pageNum >= totalPages" @click="pageNum++">下一组 →</el-button>
      </el-button-group>
    </div>
    <div v-if="!filtered.length" class="card" style="text-align:center;color:#9a8a6c">暂无匹配页</div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import pagesData from '../data/pages.json'

const PAGE_SIZE = 20
const kw = ref('')
const pageNum = ref(1)
const pages = pagesData.pages
const transcribed = computed(() => pages.filter((p) => p.chars > 0).length)

const filtered = computed(() => {
  const k = kw.value.trim()
  if (!k) return pages
  return pages.filter((p) => String(p.pdf) === k || String(p.book).includes(k))
})
const totalPages = computed(() => Math.max(1, Math.ceil(filtered.value.length / PAGE_SIZE)))
const rangeStart = computed(() => (pageNum.value - 1) * PAGE_SIZE + 1)
const rangeEnd = computed(() => Math.min(pageNum.value * PAGE_SIZE, filtered.value.length))
const paged = computed(() => filtered.value.slice((pageNum.value - 1) * PAGE_SIZE, pageNum.value * PAGE_SIZE))

function onKw() {
  pageNum.value = 1
}
function imgPath(p) {
  return import.meta.env.BASE_URL + 'pages/' + p.img
}
</script>
