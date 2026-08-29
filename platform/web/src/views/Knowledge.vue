<template>
  <div class="knowledge-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="title-side">
            <span>中医肛肠知识库</span>
            <el-button link type="primary" size="small" @click="router.push('/kb?module=anorectal')">
              在知识总库检索该专科内容
            </el-button>
          </div>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索知识库..."
            prefix-icon="Search"
            clearable
            style="width: 240px"
            @input="handleSearch"
          />
        </div>
      </template>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="中药" name="herbs">
          <div class="filter-bar">
            <el-select v-model="herbCategory" placeholder="药物分类" clearable @change="loadHerbs">
              <el-option label="清热药" value="清热药" />
              <el-option label="活血化瘀药" value="活血化瘀药" />
              <el-option label="补益药" value="补益药" />
              <el-option label="收涩药" value="收涩药" />
              <el-option label="泻下药" value="泻下药" />
              <el-option label="止血药" value="止血药" />
              <el-option label="祛湿药" value="祛湿药" />
              <el-option label="理气药" value="理气药" />
            </el-select>
          </div>

          <el-table :data="herbs" v-loading="loading" stripe>
            <el-table-column prop="name" label="药名" width="100" />
            <el-table-column prop="category" label="分类" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ row.category }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="properties" label="性味" width="140" show-overflow-tooltip />
            <el-table-column label="归经" width="140" show-overflow-tooltip>
              <template #default="{ row }">
                {{ formatMeridians(row.meridians) }}
              </template>
            </el-table-column>
            <el-table-column prop="effects" label="功效" show-overflow-tooltip />
            <el-table-column prop="indications" label="主治" width="200" show-overflow-tooltip />
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="方剂" name="formulas">
          <div class="filter-bar">
            <el-select v-model="formulaSyndrome" placeholder="证型分类" clearable @change="loadFormulas">
              <el-option label="湿热下注" value="湿热下注" />
              <el-option label="气滞血瘀" value="气滞血瘀" />
              <el-option label="脾虚气陷" value="脾虚气陷" />
              <el-option label="热毒蕴结" value="热毒蕴结" />
              <el-option label="血热肠燥" value="血热肠燥" />
              <el-option label="阴虚津亏" value="阴虚津亏" />
              <el-option label="风伤肠络" value="风伤肠络" />
            </el-select>
            <el-select v-model="formulaSource" placeholder="出处分类" clearable @change="loadFormulas">
              <el-option label="原文证治方" value="original_explicit" />
              <el-option label="医案/临床扩展" value="original_case" />
              <el-option label="传统经典/其他来源" value="traditional_classic" />
              <el-option label="历史专科疗法" value="historical_specialist" />
              <el-option label="系统整理" value="system_extension" />
            </el-select>
            <el-select v-model="formulaRisk" placeholder="风险等级" clearable @change="loadFormulas">
              <el-option label="资料参考" value="low" />
              <el-option label="需医师审核" value="medium" />
              <el-option label="高风险·仅专科" value="high" />
            </el-select>
          </div>

          <el-table :data="formulas" v-loading="loading" stripe>
            <el-table-column prop="name" label="方名" width="160">
              <template #default="{ row }">
                <el-button type="primary" link @click="viewFormula(row)">
                  {{ row.name }}
                </el-button>
              </template>
            </el-table-column>
            <el-table-column prop="syndrome_type" label="适用证型" width="140">
              <template #default="{ row }">
                <el-tag type="success" size="small">{{ row.syndrome_type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="出处/风险" width="190">
              <template #default="{ row }">
                <div class="formula-tags">
                  <el-tag size="small" :type="sourceTagType(row.source_status)">{{ row.source_label || row.source }}</el-tag>
                  <el-tag size="small" :type="riskTagType(row.risk_level)">{{ row.risk_label }}</el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="组成" show-overflow-tooltip>
              <template #default="{ row }">
                {{ formatComposition(row.composition) }}
              </template>
            </el-table-column>
            <el-table-column prop="function" label="功效" width="220" show-overflow-tooltip />
            <el-table-column prop="indications" label="主治" width="220" show-overflow-tooltip />
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="医案" name="cases">
          <el-table :data="cases" v-loading="loading" stripe>
            <el-table-column prop="title" label="案例标题" width="220" />
            <el-table-column prop="disease_type" label="病种" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ row.disease_type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="patient_info" label="患者信息" width="120" />
            <el-table-column prop="syndrome" label="证型" width="140" />
            <el-table-column prop="treatment_principle" label="治则" width="160" show-overflow-tooltip />
            <el-table-column prop="outcome" label="疗效" show-overflow-tooltip>
              <template #default="{ row }">
                {{ row.outcome || '疗效显著' }}
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="预防保健" name="prevention">
          <el-table :data="preventionGuides" v-loading="loading" stripe>
            <el-table-column prop="title" label="标题" width="220" />
            <el-table-column prop="disease_type" label="病种" width="120">
              <template #default="{ row }">
                <el-tag type="info" size="small">{{ row.disease_type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="预防要点" show-overflow-tooltip>
              <template #default="{ row }">
                {{ formatPreventionPoints(row.prevention_points) }}
              </template>
            </el-table-column>
            <el-table-column prop="postop_care" label="术后护理" width="240" show-overflow-tooltip />
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="经典医案" name="medical-cases">
          <el-table :data="medicalCases" v-loading="loading" stripe>
            <el-table-column prop="case_number" label="编号" width="110" />
            <el-table-column prop="case_title" label="案例标题" min-width="260" show-overflow-tooltip />
            <el-table-column prop="disease_type" label="病种" width="110">
              <template #default="{ row }"><el-tag size="small">{{ row.disease_type }}</el-tag></template>
            </el-table-column>
            <el-table-column prop="syndrome_type" label="证型" width="180" show-overflow-tooltip />
            <el-table-column prop="outcome" label="疗效" width="90" />
            <el-table-column label="操作" width="90" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="openMedicalCase(row)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="鉴别诊断" name="differentials">
          <div class="tab-toolbar">
            <el-select v-model="diffDisease" placeholder="选择病种" clearable style="width: 200px" @change="loadDifferentials">
              <el-option v-for="d in diseaseTypeOptions" :key="d" :label="d" :value="d" />
            </el-select>
          </div>
          <el-alert v-if="differentials" :title="differentials.summary" type="info" :closable="false" show-icon style="margin-bottom: 12px" />
          <div v-if="differentials?.items?.length" class="diff-list">
            <div v-for="dd in differentials.items" :key="dd.condition" class="diff-card" :class="{ critical: dd.urgency === 'critical' }">
              <div class="diff-card-head">
                <el-tag :type="dd.urgency === 'critical' ? 'danger' : dd.urgency === 'high' ? 'warning' : 'info'" effect="dark" size="small">{{ dd.condition }}</el-tag>
                <span v-if="dd.source" class="diff-source">{{ dd.source }}</span>
              </div>
              <ul><li v-for="pt in dd.points" :key="pt">{{ pt }}</li></ul>
            </div>
          </div>
          <el-empty v-else-if="diffDisease" description="该病种暂无鉴别诊断条目" />
        </el-tab-pane>

        <el-tab-pane label="针刺与手术" name="procedures">
          <div class="tab-toolbar">
            <el-select v-model="procDisease" placeholder="选择病种" clearable style="width: 200px" @change="loadProcedures">
              <el-option v-for="d in diseaseTypeOptions" :key="d" :label="d" :value="d" />
            </el-select>
          </div>
          <template v-if="acupuncture?.protocols?.length">
            <h4 class="proc-title">针刺法（专业操作）</h4>
            <div v-for="proto in acupuncture.protocols" :key="proto.name" class="diff-card">
              <div class="diff-card-head"><strong>{{ proto.name }}</strong><span v-if="proto.syndrome" class="diff-source">{{ proto.syndrome }}</span></div>
              <ul>
                <li v-for="pt in proto.points" :key="pt.name">{{ pt.name }}（{{ pt.role }}）：{{ pt.method }}</li>
                <li v-if="proto.course" class="course-note">疗程：{{ proto.course }}</li>
              </ul>
            </div>
          </template>
          <template v-if="surgical?.items?.length">
            <h4 class="proc-title">手术技法（院内专科·仅学习）</h4>
            <el-alert :title="surgical.governance" type="warning" :closable="false" show-icon style="margin-bottom: 12px" />
            <div v-for="tech in surgical.items" :key="tech.name" class="diff-card">
              <div class="diff-card-head">
                <el-tag type="warning" effect="dark" size="small">{{ tech.name }}</el-tag>
                <span class="diff-source">{{ tech.indication }}</span>
              </div>
              <ul><li v-for="kp in tech.key_points" :key="kp">{{ kp }}</li></ul>
            </div>
          </template>
          <el-empty v-else-if="procDisease" description="该病种暂无针刺/手术条目" />
        </el-tab-pane>

        <el-tab-pane label="原文覆盖" name="zhou-coverage">
          <el-alert
            v-if="coverageReport"
            :title="`原文共 ${coverageReport.source_total_lines} 行：结构化 ${coverageReport.summary.structured} 节，部分结构化 ${coverageReport.summary.partial} 节，资料参考 ${coverageReport.summary.reference_only} 节`"
            :description="coverageReport.honesty_notice"
            type="info"
            :closable="false"
            show-icon
            style="margin-bottom: 16px"
          />
          <el-table :data="coverageReport?.sections || []" stripe>
            <el-table-column prop="section" label="章节" width="190" />
            <el-table-column prop="lines" label="原文行号" width="110" />
            <el-table-column label="结构化状态" width="130">
              <template #default="{ row }"><el-tag :type="coverageTagType(row.status)">{{ coverageStatus(row.status) }}</el-tag></template>
            </el-table-column>
            <el-table-column label="已接入" min-width="280"><template #default="{ row }">{{ (row.included || []).join('；') }}</template></el-table-column>
            <el-table-column label="仍需补充" min-width="300"><template #default="{ row }">{{ (row.remaining || []).join('；') }}</template></el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>

      <div class="pagination-area">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadCurrentTab"
          @current-change="loadCurrentTab"
        />
      </div>
    </el-card>

    <el-dialog v-model="formulaDialogVisible" :title="selectedFormula?.name" width="700px">
      <div v-if="selectedFormula" class="formula-detail">
        <el-alert
          v-if="selectedFormula.learning_only"
          title="历史专科疗法学习资料"
          description="本条用于学习适应证背景、风险机制和现代处置边界，不作为患者自行配制、注射、封闭或腐蚀治疗的操作说明。"
          type="error"
          :closable="false"
          show-icon
          class="learning-alert"
        />
        <el-descriptions :column="1" border>
          <el-descriptions-item label="方名">{{ selectedFormula.name }}</el-descriptions-item>
          <el-descriptions-item label="出处" v-if="selectedFormula.source">{{ selectedFormula.source }}</el-descriptions-item>
          <el-descriptions-item label="资料属性" v-if="selectedFormula.source_label">
            <el-tag :type="sourceTagType(selectedFormula.source_status)">{{ selectedFormula.source_label }}</el-tag>
            <el-tag :type="riskTagType(selectedFormula.risk_level)" class="detail-risk">{{ selectedFormula.risk_label }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="组成">
            {{ selectedFormula.learning_only ? '历史组成仅用于来源识别；学习版不提供可执行配制参数' : formatComposition(selectedFormula.composition) }}
          </el-descriptions-item>
          <el-descriptions-item label="功效">{{ selectedFormula.function || selectedFormula.effects }}</el-descriptions-item>
          <el-descriptions-item label="主治">{{ selectedFormula.indications }}</el-descriptions-item>
          <el-descriptions-item label="用法">
            {{ selectedFormula.learning_only ? '仅限具备资质和相应条件的专科机构；不提供患者自行操作步骤' : selectedFormula.usage }}
          </el-descriptions-item>
          <el-descriptions-item label="证型" v-if="selectedFormula.syndrome_type">
            <el-tag type="success">{{ selectedFormula.syndrome_type }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="加减变化" v-if="selectedFormula.modifications">{{ selectedFormula.modifications }}</el-descriptions-item>
          <el-descriptions-item label="学习重点" v-if="selectedFormula.learning_topics?.length">
            <ul class="learning-topics">
              <li v-for="topic in selectedFormula.learning_topics" :key="topic">{{ topic }}</li>
            </ul>
          </el-descriptions-item>
          <el-descriptions-item label="现代边界" v-if="selectedFormula.modern_boundary">{{ selectedFormula.modern_boundary }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <el-dialog v-model="caseDialogVisible" :title="selectedCase?.case_title" width="760px" top="5vh">
      <div v-if="selectedCase" class="case-detail">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="编号">{{ selectedCase.case_number }}</el-descriptions-item>
          <el-descriptions-item label="病种">{{ selectedCase.disease_type }}</el-descriptions-item>
          <el-descriptions-item label="证型">{{ selectedCase.syndrome_type }}</el-descriptions-item>
          <el-descriptions-item label="治则">{{ selectedCase.treatment_principle }}</el-descriptions-item>
          <el-descriptions-item label="疗效">{{ selectedCase.outcome }}</el-descriptions-item>
          <el-descriptions-item label="出处" :span="2">{{ selectedCase.source }}</el-descriptions-item>
        </el-descriptions>
        <div class="case-block" v-if="selectedCase.patient_info && Object.keys(selectedCase.patient_info).length">
          <h4>患者信息</h4>
          <p>{{ formatCaseObject(selectedCase.patient_info) }}</p>
        </div>
        <div class="case-block" v-if="selectedCase.syndrome_analysis"><h4>辨证分析</h4><p>{{ selectedCase.syndrome_analysis }}</p></div>
        <div class="case-block" v-if="selectedCase.internal_formula && Object.keys(selectedCase.internal_formula).length">
          <h4>内服方</h4>
          <p><strong>{{ selectedCase.internal_formula.name }}</strong>：{{ selectedCase.internal_formula.composition }}</p>
          <p v-if="selectedCase.internal_formula.usage">用法：{{ selectedCase.internal_formula.usage }}</p>
        </div>
        <div class="case-block" v-if="selectedCase.external_treatment?.length">
          <h4>外治</h4>
          <p v-for="(ex, i) in selectedCase.external_treatment" :key="i"><strong>{{ ex.name }}</strong><span v-if="ex.composition">：{{ ex.composition }}</span><span v-if="ex.usage">；{{ ex.usage }}</span></p>
        </div>
        <div class="case-block" v-if="selectedCase.follow_ups?.length">
          <h4>复诊经过</h4>
          <div v-for="(fu, i) in selectedCase.follow_ups" :key="i" class="followup-item">
            <strong>{{ fu.诊次 }}</strong>：{{ fu.变化 }}<span v-if="fu.调整" class="followup-adjust"> → {{ fu.调整 }}</span>
          </div>
        </div>
        <div class="case-block" v-if="selectedCase.key_points"><h4>辨证要点</h4><p>{{ selectedCase.key_points }}</p></div>
        <div class="case-block teaching" v-if="selectedCase.teaching_notes"><h4>方意按语</h4><p>{{ selectedCase.teaching_notes }}</p></div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { listHerbs, listFormulas, getFormula, listCases, listPrevention, getZhouCoverage, listMedicalCases, getMedicalCase, getDifferentials, getAcupuncture, getSurgicalTechniques } from '@/api/knowledge'

const route = useRoute()
const router = useRouter()

const activeTab = ref('herbs')
const loading = ref(false)
const searchKeyword = ref('')
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const herbs = ref([])
const herbCategory = ref('')

const formulas = ref([])
const formulaSyndrome = ref('')
const formulaSource = ref('')
const formulaRisk = ref('')
const selectedFormula = ref(null)
const formulaDialogVisible = ref(false)

const cases = ref([])
const preventionGuides = ref([])
const coverageReport = ref(null)

const medicalCases = ref([])
const caseDialogVisible = ref(false)
const selectedCase = ref(null)
const diffDisease = ref('')
const differentials = ref(null)
const procDisease = ref('')
const acupuncture = ref(null)
const surgical = ref(null)
const diseaseTypeOptions = ['痔疮', '肛裂', '肛周脓肿', '直肠脱垂', '肛瘘', '肛门疣赘', '肛门疖肿', '便秘', '肛门湿疹']

let searchTimer = null

function handleSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    loadCurrentTab()
  }, 300)
}

function handleTabChange() {
  page.value = 1
  loadCurrentTab()
}

function loadCurrentTab() {
  switch (activeTab.value) {
    case 'herbs': loadHerbs(); break
    case 'formulas': loadFormulas(); break
    case 'cases': loadCases(); break
    case 'prevention': loadPrevention(); break
    case 'medical-cases': loadMedicalCases(); break
    case 'differentials': loadDifferentials(); break
    case 'procedures': loadProcedures(); break
    case 'zhou-coverage': loadCoverage(); break
  }
}

async function loadMedicalCases() {
  loading.value = true
  try {
    const res = await listMedicalCases({ page: page.value, page_size: pageSize.value })
    medicalCases.value = res.items || res || []
    total.value = res.total || medicalCases.value.length
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function loadDifferentials() {
  if (!diffDisease.value) { differentials.value = null; return }
  loading.value = true
  try { differentials.value = await getDifferentials(diffDisease.value) } catch (e) { console.error(e) } finally { loading.value = false }
}

async function loadProcedures() {
  if (!procDisease.value) { acupuncture.value = null; surgical.value = null; return }
  loading.value = true
  try {
    acupuncture.value = await getAcupuncture(procDisease.value)
    surgical.value = await getSurgicalTechniques(procDisease.value)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function openMedicalCase(c) {
  caseDialogVisible.value = true
  selectedCase.value = c
  try {
    selectedCase.value = await getMedicalCase(c.id)
  } catch (e) {
    console.error(e)
  }
}

function formatCaseObject(obj) {
  if (typeof obj === 'string') return obj
  return Object.entries(obj || {}).map(([k, v]) => `${k}：${typeof v === 'object' ? JSON.stringify(v) : v}`).join('；')
}

async function loadCoverage() {
  loading.value = true
  try { coverageReport.value = await getZhouCoverage() } catch (e) { console.error(e) } finally { loading.value = false }
}

async function loadHerbs() {
  loading.value = true
  try {
    const res = await listHerbs({
      page: page.value,
      size: pageSize.value,
      search: searchKeyword.value || undefined,
      category: herbCategory.value || undefined
    })
    herbs.value = res.items || res || []
    total.value = res.total || herbs.value.length
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function loadFormulas() {
  loading.value = true
  try {
    const res = await listFormulas({
      page: page.value,
      page_size: pageSize.value,
      search: searchKeyword.value || undefined,
      syndrome_type: formulaSyndrome.value || undefined,
      source_status: formulaSource.value || undefined,
      risk_level: formulaRisk.value || undefined
    })
    formulas.value = res.items || res || []
    total.value = res.total || formulas.value.length
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function loadCases() {
  loading.value = true
  try {
    const res = await listCases({
      page: page.value,
      size: pageSize.value,
      search: searchKeyword.value || undefined
    })
    cases.value = res.items || res || []
    total.value = res.total || cases.value.length
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function loadPrevention() {
  loading.value = true
  try {
    const res = await listPrevention({
      page: page.value,
      size: pageSize.value,
      search: searchKeyword.value || undefined
    })
    preventionGuides.value = res.items || res || []
    total.value = res.total || preventionGuides.value.length
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function viewFormula(formula) {
  selectedFormula.value = formula
  formulaDialogVisible.value = true
}

function formatMeridians(meridians) {
  if (typeof meridians === 'string') return meridians
  if (Array.isArray(meridians)) return meridians.join('、')
  return ''
}

function formatComposition(composition) {
  if (typeof composition === 'string') return composition
  if (Array.isArray(composition)) return composition.join('，')
  return ''
}

function formatPreventionPoints(points) {
  if (typeof points === 'string') return points
  if (Array.isArray(points)) return points.join('；')
  return ''
}

function sourceTagType(status) {
  return { original_explicit: 'success', original_case: 'warning', historical_specialist: 'danger', traditional_classic: 'info', system_extension: '' }[status] || 'info'
}

function riskTagType(level) {
  return { high: 'danger', medium: 'warning', low: 'info' }[level] || 'info'
}

function coverageStatus(status) {
  return { structured: '已结构化', partial: '部分结构化', reference_only: '资料参考' }[status] || status
}

function coverageTagType(status) {
  return { structured: 'success', partial: 'warning', reference_only: 'info' }[status] || 'info'
}

onMounted(() => {
  if (route.params.id) {
    activeTab.value = 'formulas'
    getFormula(route.params.id).then(res => {
      selectedFormula.value = res
      formulaDialogVisible.value = true
    })
  }
  loadCurrentTab()
})
</script>

<style scoped>
.knowledge-page {
  max-width: 1200px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-side {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-bar {
  margin-bottom: 16px;
}

.pagination-area {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.formula-detail {
  padding: 8px 0;
}

.formula-tags {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}

.detail-risk {
  margin-left: 8px;
}

.learning-alert {
  margin-bottom: 16px;
}

.learning-topics {
  margin: 0;
  padding-left: 18px;
}

.learning-topics li + li {
  margin-top: 6px;
}

.tab-toolbar {
  margin-bottom: 16px;
}

.diff-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.diff-card {
  padding: 12px 14px;
  border: 1px solid #E4E7EC;
  border-radius: 6px;
  background: #FAFBFC;
}
.diff-card.critical {
  border-color: #F56C6C;
  background: #FEF0F0;
}

.diff-card-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.diff-source {
  color: #909399;
  font-size: 12px;
}

.diff-card ul {
  margin: 0;
  padding-left: 18px;
}
.diff-card li {
  line-height: 1.7;
}
.diff-card li.course-note {
  color: #606266;
  list-style: none;
  margin-left: -18px;
}

.proc-title {
  margin: 16px 0 10px;
  color: #2E4760;
  font-size: 15px;
}

.case-detail {
  max-height: 72vh;
  overflow-y: auto;
}

.case-block {
  margin-top: 14px;
}
.case-block h4 {
  margin: 0 0 6px;
  color: #2E4760;
  font-size: 14px;
}
.case-block p {
  margin: 0;
  line-height: 1.7;
  color: #333;
}
.case-block.teaching {
  padding: 12px;
  background: #F5F7FA;
  border-radius: 6px;
}

.followup-item {
  padding: 6px 0;
  line-height: 1.7;
  border-bottom: 1px dashed #EBEEF5;
}
.followup-item:last-child { border-bottom: none; }
.followup-adjust { color: #B88230; }

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}
</style>
