<template>
  <div class="new-consultation">
    <el-page-header @back="$router.back()" title="返回">
      <template #content>
        <span class="page-title">新建疮疡会诊</span>
      </template>
    </el-page-header>

    <el-card style="margin-top: 20px">
      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step title="选择患者" />
        <el-step title="录入病情" />
        <el-step title="上传图片" />
        <el-step title="AI分析" />
      </el-steps>

      <!-- 步骤1: 选择患者 -->
      <div v-show="currentStep === 0" class="step-content">
        <h3>选择患者</h3>
        <el-form :model="form" label-width="100px">
          <el-form-item label="患者">
            <el-select
              v-model="form.patient_id"
              filterable
              remote
              placeholder="搜索患者姓名或电话"
              :remote-method="searchPatients"
              :loading="patientsLoading"
              style="width: 100%"
            >
              <el-option
                v-for="patient in patients"
                :key="patient.id"
                :label="`${patient.name} - ${patient.gender} - ${patient.age}岁`"
                :value="patient.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button @click="showAddPatientDialog = true">新建患者</el-button>
          </el-form-item>
        </el-form>
        <div class="step-actions">
          <el-button type="primary" @click="nextStep" :disabled="!form.patient_id">下一步</el-button>
        </div>
      </div>

      <!-- 步骤2: 录入病情 -->
      <div v-show="currentStep === 1" class="step-content">
        <h3>录入病情信息</h3>
        <el-form :model="form" label-width="120px">
          <el-divider content-position="left">基本信息</el-divider>

          <el-form-item label="主诉" required>
            <el-input v-model="form.chief_complaint" type="textarea" :rows="3" placeholder="患者主要症状描述" />
          </el-form-item>

          <el-form-item label="发病日期">
            <el-date-picker v-model="form.onset_date" type="date" placeholder="选择发病日期" />
          </el-form-item>

          <el-form-item label="发病部位">
            <el-select v-model="form.location" placeholder="选择部位">
              <el-option label="头面部" value="头面部" />
              <el-option label="上肢" value="上肢" />
              <el-option label="下肢" value="下肢" />
              <el-option label="躯干" value="躯干" />
            </el-select>
          </el-form-item>

          <el-form-item label="具体位置">
            <el-input v-model="form.location_detail" placeholder="如：右侧鼻翼、左手食指等" />
          </el-form-item>

          <el-divider content-position="left">症状评估</el-divider>

          <el-form-item label="疼痛程度">
            <el-slider v-model="form.symptoms.pain_level" :max="10" show-stops />
            <span class="slider-label">{{ form.symptoms.pain_level }}/10</span>
          </el-form-item>

          <el-form-item label="局部症状">
            <el-checkbox-group v-model="form.symptomsList">
              <el-checkbox label="红肿" />
              <el-checkbox label="灼热" />
              <el-checkbox label="肿胀" />
              <el-checkbox label="有脓" />
            </el-checkbox-group>
          </el-form-item>

          <el-form-item label="全身症状">
            <el-checkbox-group v-model="form.systemicList">
              <el-checkbox label="发热" />
              <el-checkbox label="乏力" />
              <el-checkbox label="纳差" />
            </el-checkbox-group>
            <el-input v-model="form.symptoms.systemic" placeholder="其他全身症状" style="margin-top: 10px" />
          </el-form-item>

          <el-divider content-position="left">望闻问切</el-divider>

          <el-form-item label="舌苔">
            <el-input v-model="form.tongue_coating" placeholder="如：薄白、黄厚、白腻等" />
          </el-form-item>

          <el-form-item label="舌质">
            <el-input v-model="form.tongue_body" placeholder="如：淡红、红、暗红等" />
          </el-form-item>

          <el-form-item label="脉象">
            <el-input v-model="form.pulse" placeholder="如：浮数、沉细、滑数等" />
          </el-form-item>
        </el-form>

        <div class="step-actions">
          <el-button @click="prevStep">上一步</el-button>
          <el-button type="primary" @click="nextStep" :disabled="!form.chief_complaint">下一步</el-button>
        </div>
      </div>

      <!-- 步骤3: 上传图片 -->
      <div v-show="currentStep === 2" class="step-content">
        <h3>上传疮疡图片</h3>
        <el-alert
          title="拍摄建议"
          type="info"
          description="请上传清晰的患处照片，建议拍摄多角度（正面、侧面、特写），光线充足，背景简洁。"
          :closable="false"
          style="margin-bottom: 20px"
        />

        <el-upload
          class="upload-demo"
          drag
          action="#"
          :http-request="handleUpload"
          :on-success="handleUploadSuccess"
          :file-list="uploadedImages"
          list-type="picture-card"
          accept="image/*"
          multiple
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            拖拽图片到此处或<em>点击上传</em>
          </div>
        </el-upload>

        <div class="step-actions">
          <el-button @click="prevStep">上一步</el-button>
          <el-button type="primary" @click="nextStep" :disabled="uploadedImages.length === 0">
            下一步，开始AI分析
          </el-button>
        </div>
      </div>

      <!-- 步骤4: AI分析 -->
      <div v-show="currentStep === 3" class="step-content">
        <h3>AI智能分析</h3>

        <div v-if="analyzing" class="analyzing">
          <el-icon class="is-loading" :size="50"><Loading /></el-icon>
          <p>千问AI正在分析图像，请稍候...</p>
        </div>

        <div v-else-if="aiResult" class="ai-result">
          <el-result icon="success" title="AI分析完成">
            <template #sub-title>
              <div class="result-content">
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="疮疡类型">
                    <el-tag type="primary" size="large">{{ aiResult.ulcer_type }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="置信度">
                    <el-progress :percentage="aiResult.confidence * 100" :color="getConfidenceColor(aiResult.confidence)" />
                  </el-descriptions-item>
                  <el-descriptions-item label="发病部位" :span="2">
                    {{ aiResult.location }} - {{ aiResult.location_detail }}
                  </el-descriptions-item>
                  <el-descriptions-item label="证型" :span="2">
                    <el-tag>{{ aiResult.syndrome }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="严重程度" :span="2">
                    <el-rate v-model="aiResult.severity" disabled :max="10" />
                    <span style="margin-left: 10px">{{ aiResult.severity_level }}</span>
                  </el-descriptions-item>
                </el-descriptions>

                <el-card style="margin-top: 20px" v-if="aiResult.treatment_suggestion">
                  <template #header>
                    <span>AI治疗建议</span>
                  </template>
                  <el-descriptions :column="1" border>
                    <el-descriptions-item label="治则">
                      {{ aiResult.treatment_suggestion.principle }}
                    </el-descriptions-item>
                    <el-descriptions-item label="内治方剂" v-if="aiResult.treatment_suggestion.internal">
                      <strong>{{ aiResult.treatment_suggestion.internal.formula }}</strong>
                      <div style="margin-top: 10px">
                        <el-tag v-for="herb in aiResult.treatment_suggestion.internal.herbs" :key="herb" style="margin: 5px">
                          {{ herb }}
                        </el-tag>
                      </div>
                    </el-descriptions-item>
                    <el-descriptions-item label="外治法" v-if="aiResult.treatment_suggestion.external">
                      {{ aiResult.treatment_suggestion.external.topical }}
                      （{{ aiResult.treatment_suggestion.external.frequency }}）
                    </el-descriptions-item>
                  </el-descriptions>
                </el-card>

                <el-alert
                  v-if="aiResult.needs_expert"
                  title="建议请求专家会诊"
                  type="warning"
                  :description="aiResult.expert_reason"
                  show-icon
                  style="margin-top: 20px"
                />

                <div v-if="recommendedExperts.length > 0" style="margin-top: 20px">
                  <h4>推荐专家</h4>
                  <el-table :data="recommendedExperts" style="margin-top: 10px">
                    <el-table-column prop="name" label="姓名" />
                    <el-table-column prop="title" label="职称" />
                    <el-table-column prop="hospital" label="医院" />
                    <el-table-column prop="match_reason" label="推荐理由" />
                    <el-table-column label="匹配度">
                      <template #default="{ row }">
                        <el-progress :percentage="row.match_score" :color="getMatchColor(row.match_score)" />
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </div>
            </template>
            <template #extra>
              <el-button type="primary" @click="handleComplete">完成会诊</el-button>
              <el-button v-if="aiResult.needs_expert" type="warning" @click="handleRequestExpert">
                请求专家会诊
              </el-button>
            </template>
          </el-result>
        </div>
      </div>
    </el-card>

    <!-- 新建患者对话框 -->
    <el-dialog v-model="showAddPatientDialog" title="新建患者" width="500px">
      <el-form :model="newPatient" label-width="80px">
        <el-form-item label="姓名" required>
          <el-input v-model="newPatient.name" />
        </el-form-item>
        <el-form-item label="性别" required>
          <el-radio-group v-model="newPatient.gender">
            <el-radio label="男" />
            <el-radio label="女" />
          </el-radio-group>
        </el-form-item>
        <el-form-item label="年龄">
          <el-input-number v-model="newPatient.age" :min="0" :max="150" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="newPatient.phone" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddPatientDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddPatient" :loading="addingPatient">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { UploadFilled, Loading } from '@element-plus/icons-vue'
import api from '../../api'

const router = useRouter()

// 步骤控制
const currentStep = ref(0)
const nextStep = () => currentStep.value++
const prevStep = () => currentStep.value--

// 患者相关
const patients = ref([])
const patientsLoading = ref(false)
const showAddPatientDialog = ref(false)
const addingPatient = ref(false)
const newPatient = reactive({
  name: '',
  gender: '男',
  age: null,
  phone: ''
})

// 表单数据
const form = reactive({
  patient_id: '',
  chief_complaint: '',
  onset_date: null,
  location: '',
  location_detail: '',
  symptoms: {
    pain_level: 5,
    redness: false,
    heat: false,
    swelling: false,
    pus: false,
    fever: false,
    systemic: ''
  },
  symptomsList: [],
  systemicList: [],
  tongue_coating: '',
  tongue_body: '',
  pulse: ''
})

// 图片上传
const uploadedImages = ref([])
const consultationId = ref('')

// AI分析
const analyzing = ref(false)
const aiResult = ref(null)
const recommendedExperts = ref([])

// 搜索患者
const searchPatients = async (query) => {
  if (!query) return
  patientsLoading.value = true
  try {
    const response = await api.get('/patients', { params: { search: query } })
    patients.value = response.data
  } catch (error) {
    console.error('Failed to search patients:', error)
  } finally {
    patientsLoading.value = false
  }
}

// 新建患者
const handleAddPatient = async () => {
  if (!newPatient.name || !newPatient.gender) {
    ElMessage.error('请填写必填项')
    return
  }

  addingPatient.value = true
  try {
    const formData = new FormData()
    formData.append('name', newPatient.name)
    formData.append('gender', newPatient.gender)
    if (newPatient.age) formData.append('age', newPatient.age)
    if (newPatient.phone) formData.append('phone', newPatient.phone)

    const response = await api.post('/patients', formData)
    form.patient_id = response.data.id
    ElMessage.success('患者创建成功')
    showAddPatientDialog.value = false
  } catch (error) {
    console.error('Failed to add patient:', error)
  } finally {
    addingPatient.value = false
  }
}

// 创建会诊记录（在步骤2完成后）
const createConsultation = async () => {
  // 合并症状
  form.symptoms.redness = form.symptomsList.includes('红肿')
  form.symptoms.heat = form.symptomsList.includes('灼热')
  form.symptoms.swelling = form.symptomsList.includes('肿胀')
  form.symptoms.pus = form.symptomsList.includes('有脓')
  form.symptoms.fever = form.systemicList.includes('发热')

  const formData = new FormData()
  formData.append('patient_id', form.patient_id)
  formData.append('chief_complaint', form.chief_complaint)
  if (form.onset_date) {
    formData.append('onset_date', form.onset_date.toISOString().split('T')[0])
  }
  if (form.location) formData.append('location', form.location)
  if (form.location_detail) formData.append('location_detail', form.location_detail)
  formData.append('symptoms', JSON.stringify(form.symptoms))
  if (form.tongue_coating) formData.append('tongue_coating', form.tongue_coating)
  if (form.tongue_body) formData.append('tongue_body', form.tongue_body)
  if (form.pulse) formData.append('pulse', form.pulse)

  try {
    const response = await api.post('/ulcers/consultations', formData)
    consultationId.value = response.data.id
    return response.data.id
  } catch (error) {
    ElMessage.error('创建会诊失败')
    throw error
  }
}

// 上传图片
const handleUpload = async (options) => {
  if (!consultationId.value) {
    // 先创建会诊记录
    try {
      await createConsultation()
    } catch (error) {
      options.onError(error)
      return
    }
  }

  const formData = new FormData()
  formData.append('image', options.file)
  formData.append('image_type', 'initial')

  try {
    const response = await api.post(
      `/ulcers/consultations/${consultationId.value}/images`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' }
      }
    )
    options.onSuccess(response.data)
  } catch (error) {
    options.onError(error)
  }
}

const handleUploadSuccess = (response, file) => {
  ElMessage.success('图片上传成功')
}

// 开始AI分析
const startAnalysis = async () => {
  analyzing.value = true
  try {
    const response = await api.post(`/ulcers/consultations/${consultationId.value}/analyze`)
    aiResult.value = response.data.ai_analysis
    recommendedExperts.value = response.data.recommended_experts || []
    ElMessage.success('AI分析完成')
  } catch (error) {
    ElMessage.error('AI分析失败')
  } finally {
    analyzing.value = false
  }
}

// 当进入步骤4时，自动开始AI分析
const originalNextStep = nextStep
nextStep = () => {
  originalNextStep()
  if (currentStep.value === 3 && !aiResult.value) {
    startAnalysis()
  }
}

// 完成会诊
const handleComplete = () => {
  ElMessage.success('会诊创建成功')
  router.push(`/ulcers/${consultationId.value}`)
}

// 请求专家会诊
const handleRequestExpert = async () => {
  try {
    await api.post(`/ulcers/consultations/${consultationId.value}/request-expert`)
    ElMessage.success('已发送专家会诊请求')
    router.push(`/ulcers/${consultationId.value}`)
  } catch (error) {
    ElMessage.error('请求失败')
  }
}

// 辅助函数
const getConfidenceColor = (confidence) => {
  if (confidence >= 0.8) return '#67c23a'
  if (confidence >= 0.6) return '#e6a23c'
  return '#f56c6c'
}

const getMatchColor = (score) => {
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
}
</script>

<style scoped>
.new-consultation {
  padding: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
}

.step-content {
  margin-top: 40px;
  padding: 20px;
}

.step-content h3 {
  margin-bottom: 20px;
  color: #303133;
}

.step-actions {
  margin-top: 30px;
  text-align: center;
}

.slider-label {
  margin-left: 10px;
  color: #606266;
}

.analyzing {
  text-align: center;
  padding: 60px 0;
}

.analyzing p {
  margin-top: 20px;
  font-size: 16px;
  color: #606266;
}

.ai-result {
  padding: 20px 0;
}

.result-content {
  text-align: left;
  max-width: 900px;
  margin: 0 auto;
}

.upload-demo {
  text-align: center;
}
</style>
