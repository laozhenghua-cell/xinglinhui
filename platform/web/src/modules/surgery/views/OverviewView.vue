<template>
  <div class="page">
    <div v-loading="loading">
      <!-- 基础计数 -->
      <el-row :gutter="20">
        <el-col :xs="12" :sm="8" :md="5" v-for="item in countCards" :key="item.label">
          <div class="count-card">
            <div class="count-num">{{ item.value ?? '-' }}</div>
            <div class="count-label">{{ item.label }}</div>
          </div>
        </el-col>
      </el-row>

      <!-- 病种分布 -->
      <el-card class="section-card" v-if="data.disease_distribution?.length">
        <template #header><span>病种分布（病例数 TOP10）</span></template>
        <el-table :data="data.disease_distribution" stripe size="small">
          <el-table-column prop="name" label="病种" />
          <el-table-column prop="count" label="病例数" width="120" />
        </el-table>
      </el-card>

      <!-- 证型分布 -->
      <el-card class="section-card" v-if="data.syndrome_distribution?.length">
        <template #header><span>证型分布</span></template>
        <el-table :data="data.syndrome_distribution" stripe size="small">
          <el-table-column prop="name" label="证型" />
          <el-table-column prop="count" label="病例数" width="120" />
        </el-table>
      </el-card>

      <!-- 常用方剂 -->
      <el-card class="section-card" v-if="data.formula_usage?.length">
        <template #header><span>常用方剂（TOP10）</span></template>
        <el-table :data="data.formula_usage" stripe size="small">
          <el-table-column prop="name" label="方剂" />
          <el-table-column prop="count" label="使用次数" width="120" />
        </el-table>
      </el-card>

      <!-- 疗效分布 -->
      <el-card class="section-card" v-if="data.effect_distribution?.length">
        <template #header><span>疗效分布</span></template>
        <el-table :data="data.effect_distribution" stripe size="small">
          <el-table-column prop="effect" label="疗效" />
          <el-table-column prop="count" label="例数" width="120" />
        </el-table>
      </el-card>

      <el-empty v-if="!loading && !Object.keys(data).length" description="暂无统计数据" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getStatsOverview } from '../api'

const data = ref({})
const loading = ref(false)

const countCards = computed(() => {
  const c = data.value.counts || {}
  return [
    { label: '患者数', value: c.patients },
    { label: '病例数', value: c.cases },
    { label: '病种数', value: c.diseases },
    { label: '方剂数', value: c.formulas },
    { label: '证型数', value: c.syndromes }
  ]
})

onMounted(async () => {
  loading.value = true
  try {
    data.value = (await getStatsOverview()) || {}
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.count-card {
  background: #fff;
  border: 1px solid #e7e3da;
  border-radius: 10px;
  padding: 22px 18px;
  text-align: center;
  margin-bottom: 16px;
}

.count-num {
  font-size: 28px;
  font-weight: 700;
  color: #2e4760;
}

.count-label {
  margin-top: 4px;
  font-size: 13px;
  color: #909399;
}

.section-card {
  margin-bottom: 16px;
}
</style>
