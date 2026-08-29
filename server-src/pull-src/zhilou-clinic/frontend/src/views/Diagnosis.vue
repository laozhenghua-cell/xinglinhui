<template>
  <div class="diagnosis-page">
    <div class="page-header">
      <h2>智能辨证</h2>
      <p>基于中医四诊合参的证型分析系统</p>
    </div>

    <!-- Phase 4: 患者选择器 -->
    <div class="patient-selector" v-if="!selectedPatient">
      <el-card>
        <el-form :inline="true">
          <el-form-item label="选择患者">
            <el-select
              v-model="tempPatientId"
              placeholder="请选择患者"
              filterable
              style="width: 300px"
            >
              <el-option
                v-for="patient in patients"
                :key="patient.id"
                :label="`${patient.name} - ${patient.id_number || '无身份证号'}`"
                :value="patient.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="selectPatient">开始辨证</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <div v-else>
      <!-- 患者信息栏 -->
      <el-card class="patient-info-bar" shadow="never">
        <div class="patient-info-content">
          <div class="left">
            <el-avatar :size="40" style="background-color: #3C5A78;">
              {{ selectedPatient.name.charAt(0) }}
            </el-avatar>
            <div class="info">
              <div class="name">{{ selectedPatient.name }}</div>
              <div class="meta">
                {{ selectedPatient.gender }} / {{ calculateAge(selectedPatient.birth_date) }}岁
              </div>
            </div>
          </div>
          <div class="right">
            <el-button text type="primary" @click="changePatient">切换患者</el-button>
          </div>
        </div>
      </el-card>

      <el-row :gutter="24" style="margin-top: 20px;">
        <!-- 左侧：四诊采集 + 病案历史 -->
        <el-col :xs="24" :lg="14">
          <FourExaminations
            ref="fourExaminationsRef"
            @analyze-complete="handleAnalyzeComplete"
            @disease-type-change="handleDiseaseTypeChange"
            @symptoms-change="handleSymptomsChange"
          />

          <!-- Phase 4.1: 病案历史 -->
          <div style="margin-top: 20px">
            <DiagnosisHistory
              ref="historyRef"
              :patient-id="selectedPatient.id"
            />
          </div>
        </el-col>

        <!-- 右侧：辨证结果 + 安全检查 -->
        <el-col :xs="24" :lg="10">
          <div class="result-sticky">
            <SyndromeResult
              v-if="syndromeResult"
              :result="syndromeResult"
              :patient="selectedPatient"
              @selectFormula="handleFormulaSelected"
            />
            <SimilarCases
              v-if="syndromeResult && !syndromeResult.primary_syndrome.insufficient_data"
              :disease-type="currentDiseaseType"
              :symptoms="currentSymptoms"
            />
            <el-card v-if="prescriptionDraft" class="prescription-status-card" shadow="never">
              <template #header><span>处方审核状态</span></template>
              <div class="prescription-status-row">
                <strong>{{ prescriptionDraft.formula_name }}</strong>
                <el-tag :type="prescriptionStatusType(prescriptionDraft.status)">{{ prescriptionStatusLabel(prescriptionDraft.status) }}</el-tag>
              </div>
              <div class="prescription-actions">
                <el-button v-if="prescriptionDraft.status === 'draft'" type="warning" size="small" @click="changePrescriptionStatus('reviewed')">送审核</el-button>
                <el-button v-if="prescriptionDraft.status === 'reviewed'" type="success" size="small" @click="changePrescriptionStatus('confirmed')">确认处方</el-button>
                <el-button v-if="prescriptionDraft.status !== 'cancelled'" type="danger" plain size="small" @click="changePrescriptionStatus('cancelled')">作废</el-button>
                <el-button type="primary" size="small" @click="printPrescription">打印 / 下载 PDF</el-button>
                <el-button size="small" @click="openPrintDialog">预览</el-button>
              </div>
            </el-card>
            <el-empty
              v-else
              description="请先完成四诊信息采集，然后点击【智能辨证】按钮"
              :image-size="120"
            />

            <!-- Phase 4.3: 用药安全检查 -->
            <div v-if="selectedFormula" style="margin-top: 20px">
              <SafetyCheckPanel
                ref="safetyCheckRef"
                :herbs="selectedFormulaHerbs"
                :auto-check="false"
                @check-complete="handleSafetyCheckComplete"
              />
              <el-button
                type="warning"
                style="width: 100%; margin-top: 12px"
                @click="checkSafety"
              >
                执行用药安全检查
              </el-button>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 方剂确认对话框 -->
    <el-dialog
      v-model="formulaDialogVisible"
      title="确认方剂并保存病案"
      width="700px"
      :close-on-click-modal="false"
    >
      <div v-if="selectedFormula">
        <p style="font-size: 16px; margin-bottom: 16px;">
          您选择了方剂：<strong style="color: #3C5A78;">{{ selectedFormula.name }}</strong>
        </p>

        <el-form :model="saveForm" label-width="100px">
          <el-form-item label="加减化裁">
            <el-input
              v-model="saveForm.modifications"
              type="textarea"
              :rows="3"
              placeholder="记录本次加减化裁内容（可选）"
            />
          </el-form-item>
          <el-form-item label="医生备注">
            <el-input
              v-model="saveForm.notes"
              type="textarea"
              :rows="3"
              placeholder="记录辨证思路、注意事项等（可选）"
            />
          </el-form-item>
        </el-form>

        <el-divider />
        <p style="color: #6B7077;">
          该方剂将自动创建处方、保存辨证记录，供后续复诊对比。
        </p>
      </div>
      <template #footer>
        <el-button @click="formulaDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          @click="confirmFormula"
          :loading="saving"
        >
          确认并保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 处方打印预览 -->
    <PrescriptionPrint
      v-model="printDialogVisible"
      :patient="selectedPatient"
      :syndrome="syndromeResult?.primary_syndrome || {}"
      :formula-name="prescriptionDraft?.formula_name || selectedFormula?.name"
      :composition="selectedFormula?.composition || prescriptionDraft?.medicines"
      :usage="prescriptionDraft?.dosage_instructions || selectedFormula?.usage"
      :duration-days="prescriptionDraft?.duration_days || 7"
      :notes="prescriptionDraft?.notes"
      :doctor-name="doctorName"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import FourExaminations from '../components/FourExaminations.vue'
import SyndromeResult from '../components/SyndromeResult.vue'
import DiagnosisHistory from '../components/DiagnosisHistory.vue'
import SafetyCheckPanel from '../components/SafetyCheckPanel.vue'
import PrescriptionPrint from '../components/PrescriptionPrint.vue'
import SimilarCases from '../components/SimilarCases.vue'
import { listPatients } from '@/api/patients'
import { saveDiagnosisRecord, createPrescriptionDraft, updatePrescriptionStatus } from '@/api/diagnosis'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const doctorName = computed(() => authStore.user?.name || authStore.userName || '')

// Phase 4: 患者管理
const patients = ref([])
const tempPatientId = ref('')
const selectedPatient = ref(null)

// 原有状态
const fourExaminationsRef = ref(null)
const historyRef = ref(null)
const safetyCheckRef = ref(null)
const syndromeResult = ref(null)
const formulaDialogVisible = ref(false)
const selectedFormula = ref(null)
const saving = ref(false)
const prescriptionDraft = ref(null)
const printDialogVisible = ref(false)

// Phase 4: 新增状态
const currentDiseaseType = ref('')
const currentSymptoms = ref({})
const safetyCheckPassed = ref(false)

const saveForm = ref({
  modifications: '',
  notes: ''
})

// 计算选中方剂的药材列表
const selectedFormulaHerbs = computed(() => {
  if (!selectedFormula.value || !selectedFormula.value.composition) {
    return []
  }
  // 假设 composition 是数组: [{ name: '黄芪', dosage: 30 }, ...]
  return selectedFormula.value.composition
})

// 加载患者列表
const loadPatients = async () => {
  try {
    const response = await listPatients({ page_size: 100 })
    patients.value = response.items || response || []
  } catch (error) {
    console.error('加载患者列表失败:', error)
    ElMessage.error('加载患者列表失败')
  }
}

// 选择患者
const selectPatient = () => {
  if (!tempPatientId.value) {
    ElMessage.warning('请选择患者')
    return
  }
  const patient = patients.value.find(p => p.id === tempPatientId.value)
  selectedPatient.value = patient
}

// 切换患者
const changePatient = () => {
  selectedPatient.value = null
  syndromeResult.value = null
  selectedFormula.value = null
}

// 计算年龄
const calculateAge = (birthDate) => {
  if (!birthDate) return '未知'
  const today = new Date()
  const birth = new Date(birthDate)
  let age = today.getFullYear() - birth.getFullYear()
  const monthDiff = today.getMonth() - birth.getMonth()
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--
  }
  return age
}

// Phase 4: 病种变化处理
const handleDiseaseTypeChange = (diseaseType) => {
  currentDiseaseType.value = diseaseType
}

// Phase 4: 症状变化处理
const handleSymptomsChange = (symptoms) => {
  currentSymptoms.value = symptoms
}

// 辨证完成处理
const handleAnalyzeComplete = (result) => {
  syndromeResult.value = result

  // 移动端自动滚动到结果
  if (window.innerWidth < 992) {
    setTimeout(() => {
      document.querySelector('.result-sticky')?.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      })
    }, 300)
  }
}

// 方剂选择处理
const handleFormulaSelected = async (formula) => {
  if (syndromeResult.value?.primary_syndrome?.insufficient_data) {
    ElMessage.warning('当前四诊资料不足，请补充症状后重新辨证再选方')
    return
  }
  selectedFormula.value = formula
  formulaDialogVisible.value = true

  // 重置表单
  saveForm.value = {
    modifications: '',
    notes: ''
  }
  safetyCheckPassed.value = false
}

// Phase 4.3: 用药安全检查
const checkSafety = () => {
  if (safetyCheckRef.value) {
    safetyCheckRef.value.performCheck()
  }
}

// Phase 4.3: 安全检查完成处理
const handleSafetyCheckComplete = ({ safe, result }) => {
  safetyCheckPassed.value = safe
  if (!safe && result.errors && result.errors.length > 0) {
    ElMessage.warning('存在用药禁忌，请修改方剂后再保存')
  }
}

function prescriptionStatusLabel(status) {
  return { draft: '待审核', reviewed: '已审核待确认', confirmed: '已确认', cancelled: '已作废' }[status] || status
}

function prescriptionStatusType(status) {
  return { draft: 'warning', reviewed: 'primary', confirmed: 'success', cancelled: 'info' }[status] || 'info'
}

async function changePrescriptionStatus(status) {
  try {
    const result = await updatePrescriptionStatus(prescriptionDraft.value.id, status)
    prescriptionDraft.value = { ...prescriptionDraft.value, ...result }
    ElMessage.success(result.message || '处方状态已更新')
  } catch (error) {
    console.error('更新处方状态失败:', error)
  }
}

function openPrintDialog() {
  if (!selectedFormula.value) {
    ElMessage.warning('请先选用方剂并生成处方')
    return
  }
  printDialogVisible.value = true
}

// 生成并下载/打印 PDF 处方（服务端 reportlab 生成，可另存为 PDF 或直接打印）
async function printPrescription() {
  if (!prescriptionDraft.value?.id) {
    ElMessage.warning('请先生成处方')
    return
  }
  try {
    const token = localStorage.getItem('token') || ''
    const res = await fetch(`/api/v1/diagnosis/prescriptions/${prescriptionDraft.value.id}/pdf`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || '生成 PDF 失败')
    }
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    window.open(url, '_blank')
  } catch (e) {
    console.error(e)
    ElMessage.error(e.message || '生成 PDF 失败')
  }
}

// 确认方剂并保存病案
const confirmFormula = async () => {
  if (!selectedPatient.value) {
    ElMessage.error('请先选择患者')
    return
  }

  // 检查是否已进行安全检查
  if (selectedFormulaHerbs.value.length > 0 && !safetyCheckPassed.value) {
    const confirmed = await ElMessageBox.confirm(
      '您还未进行用药安全检查，是否继续保存？',
      '提示',
      {
        confirmButtonText: '继续保存',
        cancelButtonText: '先检查',
        type: 'warning'
      }
    ).catch(() => false)

    if (!confirmed) return
  }

  saving.value = true
  try {
    // Phase 4.1: 保存辨证记录
    const recordData = {
      patient_id: selectedPatient.value.id,
      disease_type: currentDiseaseType.value,
      selected_symptoms: currentSymptoms.value,
      syndrome_result: syndromeResult.value,
      selected_formula: selectedFormula.value.name,
      formula_modifications: saveForm.value.modifications,
      doctor_notes: saveForm.value.notes
    }

    const savedRecord = await saveDiagnosisRecord(recordData)
    if (savedRecord?.id && selectedFormula.value) {
      prescriptionDraft.value = await createPrescriptionDraft(savedRecord.id, {
        formula_name: selectedFormula.value.name,
        medicines: selectedFormula.value.composition || [],
        dosage_instructions: selectedFormula.value.usage,
        duration_days: 7,
        notes: saveForm.value.modifications || saveForm.value.notes || undefined
      })
    }

    ElMessage.success(prescriptionDraft.value ? '病案已保存，处方草稿待审核' : '病案记录已保存')
    formulaDialogVisible.value = false

    // 刷新病案历史
    if (historyRef.value) {
      historyRef.value.loadHistory()
    }

    if (prescriptionDraft.value) {
      ElMessage.info(`处方状态：${prescriptionDraft.value.status}`)
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存病案失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadPatients()
})
</script>

<style scoped>
.diagnosis-page {
  padding: 24px;
  background: #F7F5F1;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  font-family: 'Playfair Display', serif;
  font-size: 32px;
  font-weight: 600;
  color: #1E2227;
}

.page-header p {
  margin: 0;
  color: #6B7077;
  font-size: 16px;
}

.patient-selector {
  max-width: 600px;
  margin: 40px auto;
}

.patient-info-bar {
  margin-bottom: 20px;
  border: 1px solid #E7E3DA;
}

.patient-info-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.patient-info-content .left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.patient-info-content .info .name {
  font-size: 18px;
  font-weight: 500;
  color: #1E2227;
}

.patient-info-content .info .meta {
  font-size: 14px;
  color: #6B7077;
  margin-top: 4px;
}

.result-sticky {
  position: sticky;
  top: 24px;
}

.prescription-status-card {
  margin-top: 16px;
  border: 1px solid #dbe4ee;
}

.prescription-status-row,
.prescription-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.prescription-actions {
  justify-content: flex-start;
  margin-top: 14px;
}

@media (max-width: 992px) {
  .diagnosis-page {
    padding: 16px;
  }

  .page-header h2 {
    font-size: 24px;
  }

  .result-sticky {
    position: static;
    margin-top: 24px;
  }
}
</style>
