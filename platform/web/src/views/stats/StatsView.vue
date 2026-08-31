<template>
  <div class="stats-page">
    <el-page-header @back="router.push('/')" title="返回门户">
      <template #content>
        <span class="page-title">使用统计</span>
      </template>
    </el-page-header>

    <div v-loading="loading" class="stats-body">
      <!-- 总览卡片 -->
      <el-row :gutter="20" class="overview-row">
        <el-col :xs="12" :sm="6">
          <div class="stat-card primary">
            <div class="stat-num">{{ data.total_pv ?? '-' }}</div>
            <div class="stat-label">总访问量（PV）</div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-card success">
            <div class="stat-num">{{ data.total_uv ?? '-' }}</div>
            <div class="stat-label">总访客（UV）</div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-card warning">
            <div class="stat-num">{{ data.today_pv ?? '-' }}</div>
            <div class="stat-label">今日 PV</div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-card info">
            <div class="stat-num">{{ data.today_uv ?? '-' }}</div>
            <div class="stat-label">今日 UV</div>
          </div>
        </el-col>
      </el-row>

      <!-- 近30天 PV 趋势 -->
      <el-card class="chart-card">
        <template #header><span>近 30 天 PV 趋势</span></template>
        <div ref="chartRef" class="chart-container"></div>
        <el-empty v-if="!trend.length" description="暂无趋势数据" :image-size="80" />
      </el-card>

      <!-- 按模块 PV/UV -->
      <el-card class="module-card">
        <template #header><span>按模块访问统计</span></template>
        <el-table :data="byModule" stripe>
          <el-table-column prop="module" label="模块" min-width="140">
            <template #default="{ row }">
              <el-tag>{{ moduleLabel(row.module) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="pv" label="PV（访问量）" width="160" />
          <el-table-column prop="uv" label="UV（访客数）" width="160" />
        </el-table>
        <el-empty v-if="!byModule.length" description="暂无模块数据" :image-size="80" />
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { getPublicStats } from '@/api/stats'

const router = useRouter()
const loading = ref(false)
const data = ref({})
const byModule = ref([])
const trend = ref([])
const chartRef = ref(null)
let chart = null

const MODULE_LABELS = {
  portal: '门户',
  stats: '统计页',
  anorectal: '肛肠痔漏',
  pediatrics: '儿科',
  alchemy: '丹药研究',
  surgery: '外科疮疡'
}

function moduleLabel(m) {
  return MODULE_LABELS[m] || m || '其他'
}

// 防御式解析：兼容后端字段命名差异
function normalize(res) {
  if (!res || typeof res !== 'object') return
  data.value = {
    total_pv: res.total_pv ?? res.totalPV ?? res.pv ?? null,
    total_uv: res.total_uv ?? res.totalUV ?? res.uv ?? null,
    today_pv: res.today_pv ?? res.todayPV ?? null,
    today_uv: res.today_uv ?? res.todayUV ?? null
  }

  const mods = res.by_module ?? res.modules ?? res.module_stats ?? []
  byModule.value = Array.isArray(mods)
    ? mods.map((m) => ({
        module: m.module ?? m.name ?? m.key ?? '',
        pv: m.pv ?? m.pageviews ?? 0,
        uv: m.uv ?? m.visitors ?? 0
      }))
    : []

  const days = res.last30 ?? res.daily ?? res.trend ?? res.last_30_days ?? []
  trend.value = Array.isArray(days)
    ? days.map((d) => ({
        date: d.date ?? d.day ?? d.d ?? '',
        pv: d.pv ?? d.pageviews ?? d.count ?? 0
      }))
    : []
}

function renderChart() {
  if (!chartRef.value || !trend.value.length) return
  if (!chart) chart = echarts.init(chartRef.value)
  chart.setOption({
    grid: { left: 48, right: 20, top: 24, bottom: 40 },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: trend.value.map((d) => d.date),
      axisLabel: { rotate: 45, fontSize: 12, interval: 'auto', hideOverlap: true }
    },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        name: 'PV',
        type: 'line',
        smooth: true,
        areaStyle: { opacity: 0.12 },
        data: trend.value.map((d) => d.pv),
        itemStyle: { color: '#3C5A78' }
      }
    ]
  })
}

function handleResize() {
  chart && chart.resize()
}

async function load() {
  loading.value = true
  try {
    const res = await getPublicStats()
    normalize(res)
    await nextTick()
    renderChart()
  } catch (e) {
    console.warn('公开统计接口暂不可用', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  load()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (chart) {
    chart.dispose()
    chart = null
  }
})
</script>

<style scoped>
.stats-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px 16px 48px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
}

.stats-body {
  margin-top: 20px;
}

.overview-row {
  margin-bottom: 20px;
}

.stat-card {
  background: #fff;
  border: 1px solid #e7e3da;
  border-radius: 12px;
  padding: 24px 20px;
  text-align: center;
  margin-bottom: 12px;
}

.stat-card .stat-num {
  font-size: 32px;
  font-weight: 700;
  line-height: 1.2;
}

.stat-card .stat-label {
  margin-top: 6px;
  font-size: 13px;
  color: #6b7077;
}

.stat-card.primary .stat-num { color: #3c5a78; }
.stat-card.success .stat-num { color: #67c23a; }
.stat-card.warning .stat-num { color: #e6a23c; }
.stat-card.info .stat-num { color: #909399; }

.chart-card {
  margin-bottom: 20px;
}

.chart-container {
  width: 100%;
  height: 320px;
}
@media (max-width: 768px) {
  .chart-container { height: 240px; }
}

.module-card {
  margin-bottom: 20px;
}
</style>
