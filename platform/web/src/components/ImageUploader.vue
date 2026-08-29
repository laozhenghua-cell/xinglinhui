<template>
  <div class="image-uploader">
    <div class="upload-list">
      <div
        v-for="(img, index) in modelValue"
        :key="index"
        class="image-item"
      >
        <img :src="img" alt="uploaded" class="image-preview" />
        <div class="image-actions">
          <el-button type="danger" circle size="small" @click="removeImage(index)">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
      </div>

      <div
        v-if="multiple || modelValue.length === 0"
        class="upload-trigger"
        @click="showOptions = true"
      >
        <el-icon :size="32"><Plus /></el-icon>
        <span>上传图片</span>
      </div>
    </div>

    <el-dialog v-model="showOptions" title="选择图片来源" width="300px">
      <div class="upload-option-buttons">
        <el-button type="primary" size="large" @click="startCamera">
          <el-icon><Camera /></el-icon>
          拍照
        </el-button>
        <el-button type="success" size="large" @click="selectFile">
          <el-icon><FolderOpened /></el-icon>
          选择图片
        </el-button>
      </div>
    </el-dialog>

    <el-dialog v-model="showCamera" title="拍照" width="90%" @close="stopCamera">
      <div class="camera-view">
        <video ref="videoRef" autoplay playsinline class="video-element"></video>
        <div class="camera-btn-group">
          <el-button type="primary" circle size="large" @click="capture">
            <el-icon><Camera /></el-icon>
          </el-button>
        </div>
      </div>
    </el-dialog>

    <input
      ref="fileInputRef"
      type="file"
      accept="image/*"
      :multiple="multiple"
      style="display: none"
      @change="handleFileChange"
    />

    <canvas ref="canvasRef" style="display: none"></canvas>
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  multiple: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const videoRef = ref(null)
const canvasRef = ref(null)
const fileInputRef = ref(null)
const showOptions = ref(false)
const showCamera = ref(false)

let mediaStream = null

async function startCamera() {
  showOptions.value = false
  showCamera.value = true

  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } },
      audio: false
    })
    if (videoRef.value) {
      videoRef.value.srcObject = mediaStream
    }
  } catch (err) {
    ElMessage.error('无法访问摄像头')
    showCamera.value = false
    console.error('Camera error:', err)
  }
}

function stopCamera() {
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
    mediaStream = null
  }
}

function capture() {
  if (!videoRef.value || !canvasRef.value) return

  const video = videoRef.value
  const canvas = canvasRef.value
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight

  const ctx = canvas.getContext('2d')
  ctx.drawImage(video, 0, 0)

  const dataUrl = canvas.toDataURL('image/jpeg', 0.85)
  addImage(dataUrl)
  showCamera.value = false
  stopCamera()
}

function selectFile() {
  showOptions.value = false
  fileInputRef.value.click()
}

function handleFileChange(event) {
  const files = Array.from(event.target.files)
  files.forEach(file => {
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
      addImage(e.target.result)
    }
    reader.readAsDataURL(file)
  })
  event.target.value = ''
}

function addImage(dataUrl) {
  if (props.multiple) {
    emit('update:modelValue', [...props.modelValue, dataUrl])
  } else {
    emit('update:modelValue', [dataUrl])
  }
}

function removeImage(index) {
  const newList = [...props.modelValue]
  newList.splice(index, 1)
  emit('update:modelValue', newList)
}

onBeforeUnmount(() => {
  stopCamera()
})
</script>

<style scoped>
.image-uploader {
  width: 100%;
}

.upload-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.image-item {
  width: 100px;
  height: 100px;
  position: relative;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  overflow: hidden;
}

.image-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-actions {
  position: absolute;
  top: 4px;
  right: 4px;
}

.upload-trigger {
  width: 100px;
  height: 100px;
  border: 2px dashed #dcdfe6;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #909399;
  font-size: 12px;
  transition: all 0.3s;
}

.upload-trigger:hover {
  border-color: #409EFF;
  color: #409EFF;
}

.upload-option-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.upload-option-buttons .el-button {
  width: 100%;
  height: 60px;
  font-size: 16px;
}

.camera-view {
  position: relative;
}

.video-element {
  width: 100%;
  max-height: 60vh;
  object-fit: cover;
  display: block;
  border-radius: 8px;
}

.camera-btn-group {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}
</style>
