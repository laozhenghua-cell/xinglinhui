<template>
  <div class="page">
    <el-card>
      <template #header><span>辨证诊断</span></template>

      <el-tabs v-model="tab">
        <!-- ============ AI 文本辨病 ============ -->
        <el-tab-pane label="AI 文本辨病" name="analyze">
          <el-form label-position="top">
            <el-form-item label="疮形特点描述（症状 / 部位 / 皮色 / 舌脉等）">
              <el-input
                v-model="symptoms"
                type="textarea"
                :rows="5"
                placeholder="例如：初起红肿热痛，成脓后溃破，脓稠黄，伴口渴发热，舌红苔黄，脉数…"
              />
            </el-form-item>
            <el-button type="primary" :loading="analyzeLoading" :disabled="!symptoms.trim()" @click="runAnalyze">
              智能辨病
            </el-button>
          </el-form>

          <div v-if="analyzeResult" class="result-area">
          <div style="margin-bottom:10px">
            <el-link type="primary" :href="'/kb/search?q=' + encodeURIComponent((analyzeResult.ai && (analyzeResult.ai.disease_name || analyzeResult.ai.syndrome)) || '疮疡')" target="_blank">
              在杏林汇总库检索相关方剂/医案 →
            </el-link>
          </div>
            <el-alert
              v-if="analyzeResult.hint"
              :title="analyzeResult.hint"
              :type="analyzeResult.hint.startsWith('⚠️') ? 'warning' : 'info'"
              :closable="false"
              show-icon
            />

            <div v-if="analyzeResult.ai && Object.keys(analyzeResult.ai).length" class="ai-card">
              <h4 class="sub-title">AI 分析结果</h4>
              <el-descriptions :column="2" border size="small">
                <el-descriptions-item v-if="analyzeResult.ai.disease_name" label="辨病">
                  <el-tag type="danger">{{ analyzeResult.ai.disease_name }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item v-if="analyzeResult.ai.syndrome" label="证型">
                  {{ analyzeResult.ai.syndrome }}
                </el-descriptions-item>
                <el-descriptions-item v-if="analyzeResult.ai.analysis" label="分析" :span="2">
                  {{ analyzeResult.ai.analysis }}
                </el-descriptions-item>
                <el-descriptions-item v-if="analyzeResult.ai.treatment" label="治法建议" :span="2">
                  {{ analyzeResult.ai.treatment }}
                </el-descriptions-item>
                <el-descriptions-item v-if="analyzeResult.ai.error" label="提示" :span="2">
                  {{ analyzeResult.ai.error }}
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <h4 v-if="analyzeResult.matched_diseases?.length" class="sub-title">匹配图谱库病种</h4>
            <el-table v-if="analyzeResult.matched_diseases?.length" :data="analyzeResult.matched_diseases" stripe size="small">
              <el-table-column prop="name" label="病名" width="150" />
              <el-table-column prop="category" label="分类" width="100" />
              <el-table-column label="部位" width="150" show-overflow-tooltip>
                <template #default="{ row }">{{ row.location || '—' }}</template>
              </el-table-column>
              <el-table-column label="操作" width="90">
                <template #default="{ row }">
                  <el-button link type="primary" @click="router.push(`/surgery/diseases/${row.id}`)">详情</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- ============ 方证对应（按证选方） ============ -->
        <el-tab-pane label="方证对应" name="match">
          <div class="match-head">
            <el-select v-model="matchDomain" placeholder="选择病域（可选）" clearable style="width:200px" @change="onDomainChange">
              <el-option v-for="d in matchOptions" :key="d.domain" :label="d.label" :value="d.domain" />
            </el-select>
          </div>

          <h4 class="sub-title">按证候选方</h4>
          <div class="syndrome-chips">
            <span
              v-for="d in visibleDomains"
              :key="d.domain"
              style="display:contents"
            >
              <el-checkbox
                v-for="s in d.syndromes"
                :key="s.key"
                v-model="keyChecked[s.key]"
                :value="s.key"
                style="margin-right:12px;margin-bottom:6px"
              >{{ s.label }}</el-checkbox>
            </span>
          </div>
          <el-button type="primary" size="small" :loading="matchFormulaLoading" @click="runMatchFormula">按证选方</el-button>

          <div v-if="matchFormulaResult" class="result-area">
            <el-alert v-if="matchFormulaResult.summary" :title="matchFormulaResult.summary" type="info" :closable="false" show-icon />
            <el-table :data="matchFormulaResult.items" stripe size="small" style="margin-top:12px">
              <el-table-column label="方名" width="180">
                <template #default="{ row }">{{ row.formula.name }}</template>
              </el-table-column>
              <el-table-column label="领域" width="80">
                <template #default="{ row }">{{ row.formula.domain || '—' }}</template>
              </el-table-column>
              <el-table-column label="命中关键词" min-width="180">
                <template #default="{ row }">
                  <el-tag v-for="m in row.matched" :key="m" size="small" style="margin-right:4px">{{ m }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="score" label="得分" width="80" />
              <el-table-column label="功效" min-width="180" show-overflow-tooltip>
                <template #default="{ row }">{{ row.formula.function || '—' }}</template>
              </el-table-column>
            </el-table>
          </div>

          <el-divider />

          <h4 class="sub-title">四诊驱动辨证</h4>
          <div class="sym-chips">
            <el-checkbox
              v-for="s in matchSymptoms"
              :key="s"
              v-model="matchSymptomChecked[s]"
              :value="s"
              style="margin-right:12px;margin-bottom:6px"
            >{{ s }}</el-checkbox>
          </div>
          <el-button type="primary" size="small" :loading="matchSyndromeLoading" @click="runMatchSyndrome">辨证</el-button>

          <div v-if="matchSyndromeResult" class="result-area">
            <el-alert v-if="matchSyndromeResult.suggestion" :title="matchSyndromeResult.suggestion" type="info" :closable="false" show-icon />
            <div class="syn-grid">
              <div v-for="s in matchSyndromeResult.matched" :key="s.key" class="syn-card">
                <div class="syn-name">{{ s.label }} <el-tag size="small">得分 {{ s.score }}</el-tag></div>
                <div v-if="s.desc" class="syn-line">{{ s.desc }}</div>
                <div v-if="s.matched?.length" class="syn-line">依据：{{ s.matched.join('、') }}</div>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { analyzeSymptoms, matchOptions, matchSyndrome, matchFormula } from '../api'

const router = useRouter()
const tab = ref('analyze')

// --- AI 文本辨病 ---
const symptoms = ref('')
const analyzeResult = ref(null)
const analyzeLoading = ref(false)

async function runAnalyze() {
  analyzeLoading.value = true
  try {
    analyzeResult.value = await analyzeSymptoms(symptoms.value.trim())
  } catch (e) {
    console.error(e)
  } finally {
    analyzeLoading.value = false
  }
}

// --- 方证对应 ---
const matchOptionsList = ref([])
const matchDomain = ref('')
const keyChecked = reactive({})
const matchFormulaResult = ref(null)
const matchFormulaLoading = ref(false)
const matchSymptomChecked = reactive({})
const matchSyndromeResult = ref(null)
const matchSyndromeLoading = ref(false)

const visibleDomains = computed(() => {
  if (!matchDomain.value) return matchOptionsList.value
  return matchOptionsList.value.filter((d) => d.domain === matchDomain.value)
})

const matchSymptoms = computed(() => {
  const set = new Set()
  for (const d of visibleDomains.value) {
    for (const s of d.syndromes) {
      for (const sym of s.symptoms || []) set.add(sym)
    }
  }
  return [...set]
})

function onDomainChange() {
  Object.keys(keyChecked).forEach((k) => delete keyChecked[k])
  Object.keys(matchSymptomChecked).forEach((k) => delete matchSymptomChecked[k])
  matchFormulaResult.value = null
  matchSyndromeResult.value = null
}

async function runMatchFormula() {
  const keys = Object.keys(keyChecked).filter((k) => keyChecked[k])
  if (!keys.length) {
    matchFormulaResult.value = { items: [], summary: '请先勾选证候' }
    return
  }
  matchFormulaLoading.value = true
  try {
    matchFormulaResult.value = await matchFormula({ keys, domain: matchDomain.value || undefined })
  } catch (e) {
    console.error(e)
  } finally {
    matchFormulaLoading.value = false
  }
}

async function runMatchSyndrome() {
  const sels = Object.keys(matchSymptomChecked).filter((k) => matchSymptomChecked[k])
  if (!sels.length) {
    matchSyndromeResult.value = { matched: [], suggestion: '请先勾选四诊表现' }
    return
  }
  matchSyndromeLoading.value = true
  try {
    matchSyndromeResult.value = await matchSyndrome({ domain: matchDomain.value || undefined, symptoms: sels })
  } catch (e) {
    console.error(e)
  } finally {
    matchSyndromeLoading.value = false
  }
}

onMounted(async () => {
  try {
    matchOptionsList.value = (await matchOptions()) || []
  } catch (e) {
    console.error(e)
  }
})
</script>

<style scoped>
.result-area {
  margin-top: 16px;
}

.sub-title {
  margin: 16px 0 8px;
  color: #2e4760;
}

.ai-card {
  margin-top: 12px;
}

.match-head {
  margin-bottom: 8px;
}

.syndrome-chips,
.sym-chips {
  margin-bottom: 12px;
}

.syn-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.syn-card {
  border: 1px solid #e7e3da;
  border-radius: 8px;
  padding: 12px 14px;
  background: #faf8f3;
}

.syn-name {
  font-weight: 700;
  color: #1e2227;
  margin-bottom: 6px;
}

.syn-line {
  font-size: 12.5px;
  color: #606266;
  line-height: 1.7;
}
</style>
