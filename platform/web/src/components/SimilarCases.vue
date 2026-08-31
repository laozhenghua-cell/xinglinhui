<template>
  <div class="similar-cases" v-if="diseaseType">
    <div class="section-heading">
      <div>
        <span class="section-kicker">经典医案</span>
        <h4>相似经典医案</h4>
      </div>
      <el-button v-if="cases.length" text type="primary" size="small" @click="load">刷新</el-button>
    </div>

    <el-skeleton v-if="loading" :rows="3" animated />

    <el-empty v-else-if="!cases.length" description="暂无同病种经典医案" :image-size="60" />

    <div v-else class="case-list">
      <div v-for="c in cases" :key="c.id" class="case-card" @click="viewCase(c)">
        <div class="case-head">
          <span class="case-title">{{ c.case_title }}</span>
          <el-tag type="success" size="small" effect="plain">相似 {{ Math.round(c.similarity_score * 100) }}%</el-tag>
        </div>
        <div class="case-meta">
          <el-tag size="small" type="info">{{ c.disease_type }}</el-tag>
          <span class="case-syndrome">{{ c.syndrome_type }}</span>
        </div>
      </div>
    </div>

    <el-dialog v-model="detailVisible" :title="selectedCase?.case_title" width="min(720px, 94vw)" top="5vh">
      <div v-if="selectedCase" class="case-detail">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="病种">{{ selectedCase.disease_type }}</el-descriptions-item>
          <el-descriptions-item label="证型">{{ selectedCase.syndrome_type }}</el-descriptions-item>
          <el-descriptions-item label="治则">{{ selectedCase.treatment_principle }}</el-descriptions-item>
          <el-descriptions-item label="疗效">{{ selectedCase.outcome }}</el-descriptions-item>
          <el-descriptions-item label="出处" :span="2">{{ selectedCase.source }}</el-descriptions-item>
        </el-descriptions>
        <div v-if="selectedCase.syndrome_analysis" class="case-block">
          <h5>辨证分析</h5><p>{{ selectedCase.syndrome_analysis }}</p>
        </div>
        <div v-if="selectedCase.internal_formula && Object.keys(selectedCase.internal_formula).length" class="case-block">
          <h5>内服方</h5>
          <p><strong>{{ selectedCase.internal_formula.name }}</strong>：{{ selectedCase.internal_formula.composition }}</p>
          <p v-if="selectedCase.internal_formula.usage" class="meta">用法：{{ selectedCase.internal_formula.usage }}</p>
        </div>
        <div v-if="selectedCase.follow_ups?.length" class="case-block">
          <h5>复诊经过</h5>
          <div v-for="(fu, i) in selectedCase.follow_ups" :key="i" class="followup-line">
            <strong>{{ fu.诊次 }}</strong>：{{ fu.变化 }}<span v-if="fu.调整" class="adjust"> → {{ fu.调整 }}</span>
          </div>
        </div>
        <div v-if="selectedCase.key_points" class="case-block">
          <h5>辨证要点</h5><p>{{ selectedCase.key_points }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { findSimilarCases, getMedicalCase } from '@/api/knowledge'

const props = defineProps({
  diseaseType: { type: String, default: '' },
  symptoms: { type: Object, default: () => ({}) },
})

const cases = ref([])
const loading = ref(false)
const detailVisible = ref(false)
const selectedCase = ref(null)

async function load() {
  if (!props.diseaseType) { cases.value = []; return }
  loading.value = true
  try {
    const res = await findSimilarCases({
      disease_type: props.diseaseType,
      symptoms: props.symptoms,
    })
    cases.value = (res.items || []).filter(c => c.similarity_score > 0)
  } catch (e) {
    console.error('加载相似医案失败:', e)
    cases.value = []
  } finally {
    loading.value = false
  }
}

async function viewCase(c) {
  detailVisible.value = true
  selectedCase.value = c
  try {
    selectedCase.value = await getMedicalCase(c.id)
  } catch (e) {
    console.error('加载医案详情失败:', e)
  }
}

watch(() => [props.diseaseType, props.symptoms], load, { deep: true })
onMounted(load)
</script>

<style scoped>
.similar-cases {
  margin-top: 16px;
}
.section-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.section-heading h4 {
  margin: 0;
  font-size: 15px;
  color: #1E2227;
}
.section-kicker {
  font-size: 12px;
  color: #909399;
}

.case-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.case-card {
  border: 1px solid #E7E3DA;
  border-radius: 8px;
  padding: 10px 14px;
  cursor: pointer;
  transition: all 0.2s;
  background: #fff;
}
.case-card:hover {
  border-color: #3C5A78;
  box-shadow: 0 2px 8px rgba(60, 90, 120, 0.08);
}
.case-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.case-title {
  font-size: 14px;
  font-weight: 500;
  color: #1E2227;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.case-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}
.case-syndrome {
  font-size: 13px;
  color: #6B7077;
}

.case-block {
  margin-top: 14px;
}
.case-block h5 {
  margin: 0 0 6px;
  color: #2E4760;
  font-size: 14px;
}
.case-block p {
  margin: 0;
  line-height: 1.7;
  color: #333;
}
.case-block .meta {
  color: #6B7077;
  font-size: 13px;
}
.followup-line {
  padding: 4px 0;
  line-height: 1.6;
  border-bottom: 1px dashed #EBEEF5;
}
.followup-line:last-child { border-bottom: none; }
.adjust { color: #B88230; }
</style>
