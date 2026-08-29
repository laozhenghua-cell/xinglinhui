<template>
  <div class="page">
    <!-- ============ 一、辨证导航 ============ -->
    <el-card class="section-card">
      <template #header><span>一、辨证导航（结构化问答）</span></template>
      <el-form label-width="80px" :inline="true">
        <el-form-item label="病种">
          <el-select v-model="diff.disease_id" placeholder="选择病种" filterable clearable style="width:220px">
            <el-option v-for="d in diseases" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="阴阳">
          <el-radio-group v-model="diff.yin_yang">
            <el-radio-button value="阳">阳</el-radio-button>
            <el-radio-button value="阴">阴</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="阶段">
          <el-radio-group v-model="diff.stage">
            <el-radio-button value="初起">初起</el-radio-button>
            <el-radio-button value="成脓">成脓</el-radio-button>
            <el-radio-button value="溃后">溃后</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <div class="sym-section">
        <div class="sym-title">四诊症状（可多选，用于证型排序）</div>
        <el-checkbox-group v-model="diff.symptoms">
          <el-checkbox v-for="s in symptomOptions" :key="s" :value="s" class="sym-chk">{{ s }}</el-checkbox>
        </el-checkbox-group>
      </div>

      <el-button type="primary" :loading="diffLoading" @click="runDifferentiate">辨证</el-button>

      <div v-if="diffResult" class="result-area">
        <el-alert v-if="diffResult.suggestion" :title="diffResult.suggestion" type="info" :closable="false" show-icon />
        <div class="syn-grid">
          <div v-for="s in diffResult.matched_syndromes" :key="s.id" class="syn-card">
            <div class="syn-name">{{ s.name }} <el-tag size="small" type="info">{{ s.yin_yang }}证</el-tag></div>
            <div v-if="s.local_signs" class="syn-line">局部：{{ s.local_signs }}</div>
            <div v-if="s.systemic_signs" class="syn-line">全身：{{ s.systemic_signs }}</div>
            <div v-if="s.tongue_pulse" class="syn-line">舌脉：{{ s.tongue_pulse }}</div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- ============ 二、论治出方 ============ -->
    <el-card class="section-card">
      <template #header><span>二、论治出方（病种 × 阶段 × 证型）</span></template>
      <el-form label-width="80px" :inline="true">
        <el-form-item label="病种">
          <el-select v-model="rec.disease_id" placeholder="选择病种" filterable style="width:220px" @change="onDiseaseChange">
            <el-option v-for="d in diseases" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="阶段">
          <el-radio-group v-model="rec.stage">
            <el-radio-button value="初起">初起</el-radio-button>
            <el-radio-button value="成脓">成脓</el-radio-button>
            <el-radio-button value="溃后">溃后</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="证型">
          <el-select v-model="rec.syndrome_id" placeholder="选择证型" filterable clearable style="width:200px">
            <el-option v-for="s in syndromes" :key="s.id" :label="`${s.name}（${s.yin_yang}）`" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="recLoading" @click="runRecommend">出方</el-button>
        </el-form-item>
      </el-form>

      <div v-if="recResult" class="result-area">
        <el-alert v-if="recResult.summary" :title="recResult.summary" type="success" :closable="false" show-icon />

        <h4 class="sub-title">论治规则</h4>
        <el-table :data="recResult.rules" stripe size="small">
          <el-table-column prop="stage" label="阶段" width="80" />
          <el-table-column label="证型" width="140">
            <template #default="{ row }">{{ row.syndrome?.name || '通用' }}</template>
          </el-table-column>
          <el-table-column label="内治方" width="160">
            <template #default="{ row }">
              <span v-if="row.formula">{{ row.formula.name }}</span>
              <span v-else>—</span>
            </template>
          </el-table-column>
          <el-table-column label="外治" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">{{ row.external_treatment || '—' }}</template>
          </el-table-column>
          <el-table-column label="调护" min-width="180" show-overflow-tooltip>
            <template #default="{ row }">{{ row.nursing || '—' }}</template>
          </el-table-column>
        </el-table>

        <h4 v-if="recResult.experience_formulas?.length" class="sub-title">文琢之经验方（内服）</h4>
        <el-table v-if="recResult.experience_formulas?.length" :data="recResult.experience_formulas" stripe size="small">
          <el-table-column prop="name" label="方名" width="180" />
          <el-table-column prop="function" label="功效" min-width="160" show-overflow-tooltip />
          <el-table-column prop="indication" label="适应证" min-width="220" show-overflow-tooltip />
        </el-table>

        <h4 v-if="recResult.external_formulas?.length" class="sub-title">马培之外治方参考</h4>
        <el-table v-if="recResult.external_formulas?.length" :data="recResult.external_formulas" stripe size="small">
          <el-table-column prop="name" label="方名" width="180" />
          <el-table-column prop="method" label="治法" width="70" />
          <el-table-column prop="indication" label="适应证" min-width="220" show-overflow-tooltip />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { listDiseases, listSyndromes, treatmentDifferentiate, treatmentRecommend } from '../api'

const diseases = ref([])
const syndromes = ref([])

const symptomOptions = [
  '舌红', '苔黄', '脉数', '红肿热痛', '口渴', '发热', '便结', '溲赤',
  '苔黄燥', '脉洪数', '腐肉不脱', '舌淡', '脉细弱', '脓水清稀', '新肉不生',
  '神疲乏力', '面色无华', '苔薄白', '疮口不敛', '苔黄腻', '脉滑数', '纳呆',
  '脉沉细', '发凉麻木', '畏寒', '舌紫暗', '舌有瘀斑', '脉涩', '刺痛固定',
  '漫肿', '脓成不溃', '脉弦数', '潮热盗汗', '苔少', '脉细数', '脉浮数'
]

const diff = reactive({ disease_id: null, yin_yang: '阳', stage: '初起', symptoms: [] })
const diffResult = ref(null)
const diffLoading = ref(false)

const rec = reactive({ disease_id: null, stage: '初起', syndrome_id: null })
const recResult = ref(null)
const recLoading = ref(false)

async function runDifferentiate() {
  diffLoading.value = true
  try {
    diffResult.value = await treatmentDifferentiate({
      disease_id: diff.disease_id || undefined,
      yin_yang: diff.yin_yang || undefined,
      stage: diff.stage || undefined,
      symptoms: diff.symptoms
    })
  } catch (e) {
    console.error(e)
  } finally {
    diffLoading.value = false
  }
}

async function runRecommend() {
  if (!rec.disease_id) return
  recLoading.value = true
  try {
    recResult.value = await treatmentRecommend({
      disease_id: rec.disease_id,
      stage: rec.stage,
      syndrome_id: rec.syndrome_id || undefined
    })
  } catch (e) {
    console.error(e)
  } finally {
    recLoading.value = false
  }
}

function onDiseaseChange() {
  rec.syndrome_id = null
}

onMounted(async () => {
  try {
    diseases.value = (await listDiseases({})) || []
    syndromes.value = (await listSyndromes({})) || []
  } catch (e) {
    console.error(e)
  }
})
</script>

<style scoped>
.section-card {
  margin-bottom: 20px;
}

.sym-section {
  margin: 12px 0;
}

.sym-title {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.sym-chk {
  margin-right: 12px;
  margin-bottom: 4px;
}

.result-area {
  margin-top: 16px;
}

.sub-title {
  margin: 16px 0 8px;
  color: #2e4760;
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
