<template>
  <div class="consultation-new">
    <el-page-header @back="$router.back()" title="返回">
      <template #content>
        <span class="page-title">{{ isEdit ? '就诊详情' : '新建就诊' }}</span>
      </template>
    </el-page-header>

    <div class="consultation-body" v-loading="loading">
      <!-- 基本信息 -->
      <el-card class="form-section" shadow="never">
        <template #header><span>基本信息</span></template>
        <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item label="选择患者" prop="patient_id">
                <el-select
                  v-model="form.patient_id"
                  filterable
                  remote
                  :remote-method="searchPatients"
                  placeholder="输入姓名搜索患者"
                  style="width: 100%"
                >
                  <el-option
                    v-for="p in patientOptions"
                    :key="p.id"
                    :label="`${p.name} (${p.phone || '无手机'})`"
                    :value="p.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item label="主诉">
                <el-input v-model="form.chief_complaint" placeholder="患者主诉症状（可选）" clearable />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </el-card>

      <!-- 四诊采集（复用智能辨证的完整四诊合参） -->
      <el-card class="form-section" shadow="never">
        <template #header><span>四诊合参 · 辨证</span></template>
        <FourExaminations
          ref="fourExaminationsRef"
          @analyze-complete="handleAnalyzeComplete"
          @disease-type-change="onDiseaseChange"
          @symptoms-change="onSymptomsChange"
        />
      </el-card>

      <!-- 辨证结果 -->
      <el-card class="form-section" shadow="never" v-if="diagnosisResult">
        <template #header><span>辨证结果</span></template>
        <SyndromeResult
          :result="diagnosisResult"
          :patient="selectedPatientInfo"
          @selectFormula="handleSelectFormula"
          @selectTreatment="handleSelectTreatment"
        />
      </el-card>

      <!-- 影像资料 -->
      <el-card class="form-section" shadow="never">
        <template #header><span>影像资料（可选）</span></template>
        <ImageUploader v-model="form.images" multiple />
      </el-card>

      <div class="form-actions">
        <el-button @click="$router.back()">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          保存就诊记录
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { listPatients } from '@/api/patients'
import { createConsultation, getConsultation, updateConsultation } from '@/api/consultations'
import ImageUploader from '@/components/ImageUploader.vue'
import SyndromeResult from '@/components/SyndromeResult.vue'
import FourExaminations from '@/components/FourExaminations.vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const formRef = ref(null)
const fourExaminationsRef = ref(null)
const loading = ref(false)
const saving = ref(false)
const patientOptions = ref([])
const diagnosisResult = ref(null)
const activeConsultationId = ref(route.params.id || null)

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  patient_id: null,
  disease_type: '',   // 中文病种（由四诊组件回传）
  chief_complaint: '',
  symptoms: {},       // 结构化四诊症状
  images: [],
  syndrome: '',
  diagnosis: '',
  treatment_principle: '',
  prescription: '',
  external_treatment: '',
  acupuncture: ''
})

// 用于辨证结果顶部显示患者信息
const selectedPatientInfo = computed(() => {
  const p = patientOptions.value.find(x => x.id === form.patient_id)
  return p ? { name: p.name, gender: p.gender, age: p.age, phone: p.phone } : {}
})

const rules = {
  patient_id: [{ required: true, message: '请选择患者', trigger: 'change' }]
}

function onDiseaseChange(diseaseType) {
  form.disease_type = diseaseType  // 已是中文，直接存
}

function onSymptomsChange(symptoms) {
  form.symptoms = symptoms || {}
}

function handleAnalyzeComplete(result) {
  diagnosisResult.value = result
  if (result?.primary_syndrome) {
    form.syndrome = result.primary_syndrome.syndrome_name || ''
    form.treatment_principle = result.primary_syndrome.treatment_principle || ''
  }
}

async function searchPatients(query) {
  if (!query && patientOptions.value.length) return
  try {
    const res = await listPatients({ search: query || '', size: 20 })
    patientOptions.value = res.items || res || []
  } catch (e) {
    console.error(e)
  }
}

function handleSelectFormula(formula) {
  let prescriptionText = `${formula.name}\n`
  if (formula.composition && formula.composition.length > 0) {
    prescriptionText += '\n【组成】\n'
    formula.composition.forEach(herb => {
      const note = herb.note ? `（${herb.note}）` : ''
      prescriptionText += `  ${herb.name} ${herb.dosage}${herb.unit}${note}\n`
    })
  }
  if (formula.usage) prescriptionText += `\n【用法】${formula.usage}\n`
  if (formula.modifications) prescriptionText += `\n【加减】${formula.modifications}\n`
  form.prescription = prescriptionText
}

function handleSelectTreatment(treatment) {
  let externalText = `${treatment.name}\n`
  if (treatment.function) externalText += `【功效】${treatment.function}\n`
  if (treatment.usage) externalText += `【用法】${treatment.usage}\n`
  if (treatment.frequency) externalText += `【频次】${treatment.frequency}\n`
  if (treatment.precautions) externalText += `【注意】${treatment.precautions}\n`
  form.external_treatment = externalText
}

async function handleSave() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  if (!form.disease_type) {
    ElMessage.warning('请在四诊区选择病种')
    return
  }

  saving.value = true
  try {
    const data = {
      patient_id: form.patient_id,
      disease_type: form.disease_type,
      chief_complaint: form.chief_complaint,
      symptoms: form.symptoms,
      images: form.images,
      syndrome: form.syndrome,
      treatment_principle: form.treatment_principle,
      prescription_text: form.prescription,
      syndrome_result: diagnosisResult.value || null,
    }

    if (activeConsultationId.value) {
      await updateConsultation(activeConsultationId.value, data)
      ElMessage.success('更新成功')
    } else {
      const res = await createConsultation(data)
      ElMessage.success('保存成功')
      router.push(`/consultations/${res.id}`)
    }
  } catch (e) {
    // 拦截器已处理错误
  } finally {
    saving.value = false
  }
}

async function loadConsultation() {
  if (!activeConsultationId.value) return
  loading.value = true
  try {
    const data = await getConsultation(activeConsultationId.value)
    form.patient_id = data.patient_id
    form.disease_type = data.disease_type
    form.chief_complaint = data.chief_complaint
    form.symptoms = data.symptoms || {}
    form.images = data.images || []
    form.syndrome = data.syndrome
    form.treatment_principle = data.treatment_principle
    form.prescription = data.prescription_text || ''
    if (data.syndrome_result?.primary_syndrome) {
      diagnosisResult.value = data.syndrome_result
    }
    if (data.patient_id) {
      await searchPatients(data.patient_name || '')
      const p = patientOptions.value.find(x => x.id === data.patient_id)
      if (!p && data.patient_name) {
        patientOptions.value = [{ id: data.patient_id, name: data.patient_name, phone: data.patient_phone }]
      }
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  searchPatients('')
  if (activeConsultationId.value) {
    loadConsultation()
  }
  if (route.query.patient_id) {
    form.patient_id = route.query.patient_id
  }
})
</script>

<style scoped>
.consultation-new {
  max-width: 1000px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
}

.consultation-body {
  margin-top: 20px;
}

.form-section {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 0;
}
</style>
