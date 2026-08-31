<template>
  <el-dialog :model-value="modelValue" title="📷 拍照识舌" width="min(560px, 94vw)" @update:model-value="v => emit('update:modelValue', v)" @open="startCamera" @closed="cleanup">
    <div class="tc-body">
      <!-- 拍摄引导 -->
      <div class="tc-tips">
        <b>拍摄三要:</b>①自然光、面朝光源、关闭美颜滤镜;②自然伸舌、舌尖向下、不卷不使劲;③舌头占取景框约 2/3,拍清舌尖与舌根。
      </div>

      <!-- 摄像头 -->
      <div v-if="stage === 'camera'" class="tc-stage">
        <div class="tc-video-wrap">
          <video ref="videoRef" autoplay playsinline muted class="tc-video"></video>
          <svg class="tc-guide" viewBox="0 0 100 100" preserveAspectRatio="none">
            <ellipse cx="50" cy="55" rx="26" ry="32" fill="none" stroke="rgba(255,255,255,0.85)" stroke-width="1.2" />
            <ellipse cx="50" cy="55" rx="34" ry="40" fill="none" stroke="rgba(255,255,255,0.35)" stroke-width="0.8" stroke-dasharray="3 3" />
          </svg>
        </div>
        <div class="tc-actions">
          <el-button type="primary" @click="capture">📸 拍照</el-button>
          <el-button @click="close">取消</el-button>
        </div>
      </div>

      <!-- 预览/识别中/结果 -->
      <div v-else class="tc-stage">
        <div class="tc-preview">
          <img v-if="photoUrl" :src="photoUrl" class="tc-photo" alt="舌象照片" />
        </div>
        <div v-if="stage === 'recognizing'" class="tc-hint">🧠 AI 正在识别舌象(约 3-5 秒)…</div>
        <template v-else-if="stage === 'result'">
          <div class="tc-result">
            <div class="tc-labels">
              <el-tag v-for="l in labels" :key="l" type="success" size="large" style="margin:0 6px 6px 0">{{ l }}</el-tag>
              <span v-if="!labels.length" class="tc-none">未识别出明确舌象特征</span>
            </div>
            <div class="tc-meta">
              <el-tag v-if="lowConfidence" type="warning" size="small">⚠️ 置信度较低,建议人工核对</el-tag>
              <el-tag v-else-if="confidence !== null && confidence !== undefined" size="small" type="info">置信度 {{ Math.round(confidence * 100) }}%</el-tag>
              <span v-if="message" class="tc-msg">{{ message }}</span>
            </div>
          </div>
          <div class="tc-actions">
            <el-button type="primary" :disabled="!labels.length" @click="merge">✅ 并入舌象再辨证</el-button>
            <el-button @click="stage = 'camera'; photoUrl = ''">🔄 重拍</el-button>
            <el-button @click="close">手动点选</el-button>
          </div>
        </template>
        <div v-else class="tc-actions">
          <el-button type="primary" :loading="recognizing" @click="recognize">🧠 开始识别</el-button>
          <el-button @click="stage = 'camera'; photoUrl = ''">🔄 重拍</el-button>
        </div>
      </div>

      <div v-if="cameraError" class="tc-error">
        {{ cameraError }} 无法使用摄像头时,可直接在"望闻切"步骤手动点选舌象。
      </div>
      <div class="tc-note">舌象自动识别供辨证参考;受光照与拍摄影响,结论须经中医师面诊确认。</div>
    </div>
  </el-dialog>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { dxTongue } from '@/api/dx'

const props = defineProps({ modelValue: Boolean })
const emit = defineEmits(['update:modelValue', 'merged'])

const videoRef = ref(null)
const stage = ref('camera') // camera | preview | recognizing | result
const photoUrl = ref('')
const recognizing = ref(false)
const cameraError = ref('')
const labels = ref([])
const confidence = ref(null)
const lowConfidence = ref(false)
const message = ref('')
let mediaStream = null
let photoBlob = null

async function startCamera() {
  stage.value = 'camera'
  photoUrl.value = ''
  labels.value = []
  confidence.value = null
  lowConfidence.value = false
  message.value = ''
  cameraError.value = ''
  photoBlob = null
  if (!navigator.mediaDevices?.getUserMedia) {
    cameraError.value = '当前浏览器不支持摄像头。'
    return
  }
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } },
      audio: false
    })
    await nextTick()
    if (videoRef.value) videoRef.value.srcObject = mediaStream
  } catch (err) {
    console.error('camera error', err)
    cameraError.value = '无法访问摄像头(可能被浏览器拦截)。'
  }
}

function stopCamera() {
  if (mediaStream) {
    mediaStream.getTracks().forEach(t => t.stop())
    mediaStream = null
  }
}

function capture() {
  const video = videoRef.value
  if (!video || !video.videoWidth) {
    ElMessage.warning('摄像头尚未就绪,请稍候再拍')
    return
  }
  const canvas = document.createElement('canvas')
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  canvas.getContext('2d').drawImage(video, 0, 0)
  canvas.toBlob(blob => {
    if (!blob) {
      ElMessage.error('拍照失败,请重试')
      return
    }
    photoBlob = blob
    photoUrl.value = URL.createObjectURL(blob)
    stage.value = 'preview'
  }, 'image/jpeg', 0.9)
}

async function recognize() {
  if (!photoBlob) return
  recognizing.value = true
  stage.value = 'recognizing'
  try {
    const file = new File([photoBlob], `tongue_${Date.now()}.jpg`, { type: 'image/jpeg' })
    const res = await dxTongue(file)
    labels.value = res.labels || []
    confidence.value = res.confidence
    lowConfidence.value = !!res.low_confidence
    message.value = res.message || ''
    stage.value = 'result'
    if (!labels.value.length) {
      if (res.not_tongue) ElMessage.warning('未识别到清晰舌象,请重拍或手动点选')
      else ElMessage.info(res.message || 'AI 暂不可用,可手动点选舌象')
    }
  } catch (e) {
    stage.value = 'preview'
    ElMessage.error('识别失败:' + (e?.response?.data?.detail || e.message))
  } finally {
    recognizing.value = false
  }
}

function merge() {
  emit('merged', [...labels.value])
  ElMessage.success('已并入舌象:' + labels.value.join('、'))
  close()
}

function close() {
  emit('update:modelValue', false)
}

function cleanup() {
  stopCamera()
  if (photoUrl.value) URL.revokeObjectURL(photoUrl.value)
  photoUrl.value = ''
}

onBeforeUnmount(cleanup)
</script>

<style scoped>
.tc-body { padding: 0 4px; }
.tc-tips { background: #FBF7EC; border-left: 3px solid var(--xl-gold); color: #6B5C42; font-size: 12.5px; padding: 6px 10px; border-radius: 4px; margin-bottom: 10px; line-height: 1.6; }
.tc-stage { text-align: center; }
.tc-video-wrap { position: relative; display: inline-block; width: 100%; max-width: 420px; border-radius: 10px; overflow: hidden; background: #1a1a1a; }
.tc-video { width: 100%; display: block; transform: scaleX(-1); }
.tc-guide { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
.tc-preview { width: 100%; max-width: 420px; margin: 0 auto; border-radius: 10px; overflow: hidden; background: #f5f5f5; }
.tc-photo { width: 100%; display: block; }
.tc-actions { margin-top: 12px; display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; }
.tc-hint { margin-top: 10px; color: #2F6DA0; font-size: 13px; }
.tc-result { margin-top: 10px; }
.tc-labels { margin-bottom: 6px; }
.tc-none { color: #999; font-size: 13px; }
.tc-meta { font-size: 12.5px; color: #8a8370; display: flex; align-items: center; gap: 8px; justify-content: center; flex-wrap: wrap; }
.tc-msg { color: #A03D2C; }
.tc-error { margin-top: 10px; background: #FDEEEE; border: 1px solid #E8A0A0; color: #B42318; border-radius: 6px; padding: 8px 10px; font-size: 12.5px; }
.tc-note { margin-top: 12px; color: #999; font-size: 12px; text-align: center; }
</style>
