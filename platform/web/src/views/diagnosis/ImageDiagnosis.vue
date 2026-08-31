<template>
  <div class="image-diagnosis">
    <el-row :gutter="20">
      <el-col :xs="24" :lg="10">
        <el-card class="upload-card">
          <template #header>
            <span>图像采集</span>
          </template>

          <div class="capture-area">
            <div v-if="!imagePreview && !showCamera" class="upload-placeholder" @click="showUploadOptions = true">
              <el-icon :size="48" color="#909399"><Camera /></el-icon>
              <p>点击上传或拍照</p>
            </div>

            <div v-if="showCamera" class="camera-container">
              <video ref="videoRef" autoplay playsinline class="camera-video"></video>
              <div class="camera-controls">
                <el-button type="danger" circle @click="stopCamera">
                  <el-icon><Close /></el-icon>
                </el-button>
                <el-button type="primary" circle size="large" @click="capturePhoto">
                  <el-icon><Camera /></el-icon>
                </el-button>
                <el-button circle @click="switchCamera">
                  <el-icon><Switch /></el-icon>
                </el-button>
              </div>
            </div>

            <div v-if="imagePreview && !showCamera" class="preview-container">
              <img :src="imagePreview" class="preview-image" alt="预览" />
              <el-button class="clear-btn" type="danger" circle size="small" @click="clearImage">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
          </div>

          <el-dialog v-model="showUploadOptions" title="选择图像来源" width="300px">
            <div class="upload-options">
              <el-button type="primary" size="large" class="option-btn" @click="startCamera">
                <el-icon><Camera /></el-icon>
                拍照
              </el-button>
              <el-button type="success" size="large" class="option-btn" @click="triggerFileInput">
                <el-icon><FolderOpened /></el-icon>
                从相册选择
              </el-button>
            </div>
          </el-dialog>

          <input
            ref="fileInputRef"
            type="file"
            accept="image/*"
            style="display: none"
            @change="handleFileSelect"
          />

          <canvas ref="canvasRef" style="display: none"></canvas>

          <el-divider />

          <el-form label-width="80px">
            <el-form-item label="图像类型">
              <el-select v-model="imageType" placeholder="请选择图像类型" style="width: 100%">
                <el-option
                  v-for="t in imageTypes"
                  :key="t.value"
                  :label="t.label"
                  :value="t.value"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="伴随症状">
              <el-input
                v-model="extraSymptoms"
                type="textarea"
                :rows="3"
                placeholder="可选：描述伴随症状，如便血、疼痛程度、持续时间等"
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="analyzing"
                :disabled="!imageBase64 || !imageType"
                style="width: 100%"
                @click="handleAnalyze"
              >
                <el-icon><MagicStick /></el-icon>
                开始AI分析
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="14">
        <el-card class="result-card" v-loading="analyzing">
          <template #header>
            <div class="card-header">
              <span>诊断结果</span>
              <el-button
                v-if="analysisResult"
                type="success"
                size="small"
                @click="showSaveDialog = true"
              >
                <el-icon><DocumentChecked /></el-icon>
                保存到就诊记录
              </el-button>
            </div>
          </template>

          <div v-if="analysisResult" class="result-content">
            <el-descriptions :column="1" border class="result-section">
              <el-descriptions-item label="疾病判断">
                <el-tag type="danger" size="large">{{ analysisResult.disease }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="置信度">
                <el-progress
                  :percentage="Math.round((analysisResult.confidence || 0) * 100)"
                  :color="getProgressColor"
                  :stroke-width="20"
                  text-inside
                />
              </el-descriptions-item>
            </el-descriptions>

            <el-card shadow="never" class="sub-section">
              <template #header><span>视觉分析</span></template>
              <div class="findings-list">
                <el-tag
                  v-for="finding in analysisResult.visual_findings || []"
                  :key="finding"
                  class="finding-tag"
                >
                  {{ finding }}
                </el-tag>
                <span v-if="!analysisResult.visual_findings || analysisResult.visual_findings.length === 0" class="empty-text">
                  暂无视觉分析数据
                </span>
              </div>
            </el-card>

            <el-card shadow="never" class="sub-section">
              <template #header><span>辨证分型</span></template>
              <p class="result-text">{{ analysisResult.syndrome || '未明确' }}</p>
            </el-card>

            <el-card shadow="never" class="sub-section">
              <template #header><span>治疗方案</span></template>
              <el-descriptions :column="1" border>
                <el-descriptions-item label="治法">
                  {{ analysisResult.treatment_principle || '未提供' }}
                </el-descriptions-item>
                <el-descriptions-item label="内服方药">
                  <pre class="formula-text">{{ analysisResult.formula || '未提供' }}</pre>
                </el-descriptions-item>
                <el-descriptions-item label="外治法">
                  {{ analysisResult.external_treatment || '未提供' }}
                </el-descriptions-item>
                <el-descriptions-item label="针灸方案">
                  {{ analysisResult.acupuncture || '未提供' }}
                </el-descriptions-item>
              </el-descriptions>
            </el-card>

            <el-alert
              v-if="analysisResult.red_flags && analysisResult.red_flags.length > 0"
              type="error"
              title="危险信号 - 请立即就医"
              :closable="false"
              show-icon
              class="sub-section"
            >
              <ul class="red-flags-list">
                <li v-for="flag in analysisResult.red_flags" :key="flag">{{ flag }}</li>
              </ul>
            </el-alert>

            <el-alert
              type="warning"
              title="免责声明"
              :closable="false"
              class="sub-section disclaimer"
            >
              AI分析结果仅供参考，不能替代专业医师的临床诊断。请结合四诊合参综合判断。
            </el-alert>
          </div>

          <el-empty v-else description="上传图像并点击分析按钮获取诊断结果" />
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="showSaveDialog" title="保存到就诊记录" width="400px">
      <el-form label-width="80px">
        <el-form-item label="选择患者">
          <el-select
            v-model="savePatientId"
            filterable
            remote
            :remote-method="searchPatientsForSave"
            placeholder="搜索患者"
            style="width: 100%"
          >
            <el-option
              v-for="p in savePatientOptions"
              :key="p.id"
              :label="`${p.name} (${p.phone || ''})`"
              :value="p.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSaveDialog = false">取消</el-button>
        <el-button type="primary" :loading="savingToRecord" :disabled="!savePatientId" @click="handleSaveToRecord">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount } from 'vue'
import { analyzeImage } from '@/api/vision'
import { createConsultation } from '@/api/consultations'
import { listPatients } from '@/api/patients'
import { imageTypes } from '@/data/anorectal-syndromes'
import { ElMessage } from 'element-plus'

const videoRef = ref(null)
const canvasRef = ref(null)
const fileInputRef = ref(null)

const showCamera = ref(false)
const showUploadOptions = ref(false)
const showSaveDialog = ref(false)
const imagePreview = ref('')
const imageBase64 = ref('')
const imageType = ref('')
const extraSymptoms = ref('')
const analyzing = ref(false)
const analysisResult = ref(null)
const savingToRecord = ref(false)
const savePatientId = ref(null)
const savePatientOptions = ref([])

let mediaStream = null
let facingMode = 'environment'

function getProgressColor(percentage) {
  if (percentage >= 80) return '#67C23A'
  if (percentage >= 60) return '#E6A23C'
  return '#F56C6C'
}

async function startCamera() {
  showUploadOptions.value = false
  showCamera.value = true

  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: facingMode, width: { ideal: 1280 }, height: { ideal: 720 } },
      audio: false
    })
    if (videoRef.value) {
      videoRef.value.srcObject = mediaStream
    }
  } catch (err) {
    ElMessage.error('无法访问摄像头，请检查权限设置')
    showCamera.value = false
    console.error('Camera error:', err)
  }
}

function stopCamera() {
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
    mediaStream = null
  }
  showCamera.value = false
}

async function switchCamera() {
  facingMode = facingMode === 'environment' ? 'user' : 'environment'
  stopCamera()
  await startCamera()
}

function capturePhoto() {
  if (!videoRef.value || !canvasRef.value) return

  const video = videoRef.value
  const canvas = canvasRef.value
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight

  const ctx = canvas.getContext('2d')
  ctx.drawImage(video, 0, 0)

  const dataUrl = canvas.toDataURL('image/jpeg', 0.85)
  imagePreview.value = dataUrl
  imageBase64.value = dataUrl.split(',')[1]

  stopCamera()
}

function triggerFileInput() {
  showUploadOptions.value = false
  fileInputRef.value.click()
}

function handleFileSelect(event) {
  const file = event.target.files[0]
  if (!file) return

  if (!file.type.startsWith('image/')) {
    ElMessage.error('请选择图片文件')
    return
  }

  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过10MB')
    return
  }

  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target.result
    imageBase64.value = e.target.result.split(',')[1]
  }
  reader.readAsDataURL(file)
  event.target.value = ''
}

function clearImage() {
  imagePreview.value = ''
  imageBase64.value = ''
  analysisResult.value = null
}

async function handleAnalyze() {
  if (!imageBase64.value) {
    ElMessage.warning('请先上传或拍摄图像')
    return
  }
  if (!imageType.value) {
    ElMessage.warning('请选择图像类型')
    return
  }

  analyzing.value = true
  try {
    const result = await analyzeImage(imageBase64.value, imageType.value, extraSymptoms.value)
    analysisResult.value = result
    ElMessage.success('分析完成')
  } catch (e) {
    console.error('Analysis failed:', e)
  } finally {
    analyzing.value = false
  }
}

async function searchPatientsForSave(query) {
  if (!query) return
  try {
    const res = await listPatients({ search: query, size: 20 })
    savePatientOptions.value = res.items || res || []
  } catch (e) {
    console.error(e)
  }
}

async function handleSaveToRecord() {
  if (!savePatientId.value || !analysisResult.value) return

  savingToRecord.value = true
  try {
    await createConsultation({
      patient_id: savePatientId.value,
      disease_type: imageType.value,
      chief_complaint: extraSymptoms.value,
      syndrome: analysisResult.value.syndrome,
      diagnosis: analysisResult.value.disease,
      treatment_principle: analysisResult.value.treatment_principle,
      prescription: analysisResult.value.formula,
      external_treatment: analysisResult.value.external_treatment,
      acupuncture: analysisResult.value.acupuncture,
      images: [imagePreview.value]
    })
    ElMessage.success('已保存到就诊记录')
    showSaveDialog.value = false
  } catch (e) {
    console.error(e)
  } finally {
    savingToRecord.value = false
  }
}

onBeforeUnmount(() => {
  stopCamera()
})
</script>

<style scoped>
.image-diagnosis {
  max-width: 1400px;
}

.upload-card {
  margin-bottom: 20px;
}

.capture-area {
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  background: #fafafa;
}

.upload-placeholder {
  text-align: center;
  cursor: pointer;
  padding: 40px;
  width: 100%;
}

.upload-placeholder p {
  margin-top: 12px;
  color: #909399;
  font-size: 14px;
}

.upload-placeholder:hover {
  border-color: #409EFF;
}

.camera-container {
  width: 100%;
  position: relative;
}

.camera-video {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
  display: block;
}

.camera-controls {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 16px;
  align-items: center;
}

.preview-container {
  width: 100%;
  position: relative;
}

.preview-image {
  width: 100%;
  max-height: 400px;
  object-fit: contain;
  display: block;
}

.clear-btn {
  position: absolute;
  top: 8px;
  right: 8px;
}

.upload-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-btn {
  width: 100%;
  height: 60px;
  font-size: 16px;
}

.result-card {
  min-height: 500px;
}

.card-header { flex-wrap: wrap; gap: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-content {
  padding: 0;
}

.result-section {
  margin-bottom: 16px;
}

.sub-section {
  margin-bottom: 16px;
}

.findings-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.finding-tag {
  margin: 0;
}

.empty-text {
  color: #909399;
  font-size: 14px;
}

.result-text {
  margin: 0;
  font-size: 15px;
  line-height: 1.6;
}

.formula-text {
  margin: 0;
  white-space: pre-wrap;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.6;
}

.red-flags-list {
  margin: 8px 0 0;
  padding-left: 20px;
}

.red-flags-list li {
  margin-bottom: 4px;
}

.disclaimer {
  font-size: 12px;
}

@media (max-width: 768px) {
  .image-diagnosis .el-col {
    margin-bottom: 16px;
  }
}
</style>
