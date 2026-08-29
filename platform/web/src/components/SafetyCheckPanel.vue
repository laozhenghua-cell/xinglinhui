<template>
  <div class="safety-check-panel">
    <div class="panel-header">
      <h4>
        <el-icon><WarnTriangleFilled /></el-icon>
        用药安全检查
      </h4>
    </div>

    <div v-if="!checked" class="unchecked-state">
      <el-alert
        title="提醒：方剂选定后，请进行用药安全检查"
        type="info"
        :closable="false"
        show-icon
      />
    </div>

    <div v-else class="check-results">
      <!-- 严重错误 -->
      <div v-if="result.errors && result.errors.length > 0" class="error-section">
        <el-alert
          title="严重错误（必须修改）"
          type="error"
          :closable="false"
        >
          <div v-for="(error, index) in result.errors" :key="index" class="alert-item">
            <strong>{{ error.type }}：</strong>{{ error.message }}
            <p class="suggestion">建议：{{ error.suggestion }}</p>
          </div>
        </el-alert>
      </div>

      <!-- 警告 -->
      <div v-if="result.warnings && result.warnings.length > 0" class="warning-section" style="margin-top: 12px">
        <el-alert
          title="警告提示（建议注意）"
          type="warning"
          :closable="false"
        >
          <div v-for="(warning, index) in result.warnings" :key="index" class="alert-item">
            <strong>{{ warning.type }}：</strong>{{ warning.message }}
            <p class="suggestion">建议：{{ warning.suggestion }}</p>
          </div>
        </el-alert>
      </div>

      <!-- 优化建议 -->
      <div v-if="result.suggestions && result.suggestions.length > 0" class="suggestion-section" style="margin-top: 12px">
        <el-alert
          title="优化建议"
          type="info"
          :closable="false"
        >
          <ul>
            <li v-for="(suggestion, index) in result.suggestions" :key="index">
              {{ suggestion }}
            </li>
          </ul>
        </el-alert>
      </div>

      <!-- 安全通过 -->
      <div v-if="isSafe" class="safe-section">
        <el-alert
          title="✓ 用药安全检查通过"
          type="success"
          :closable="false"
        />
      </div>
    </div>

    <!-- 患者信息表单 -->
    <el-collapse v-model="activeCollapse" style="margin-top: 16px">
      <el-collapse-item title="患者特殊信息（影响用药安全）" name="patient-info">
        <el-form :model="patientInfo" label-width="120px" size="small">
          <el-form-item label="是否妊娠">
            <el-switch v-model="patientInfo.is_pregnant" />
          </el-form-item>
          <el-form-item label="年龄">
            <el-input-number v-model="patientInfo.age" :min="0" :max="150" />
            <span style="margin-left: 8px; color: #6B7077">岁</span>
          </el-form-item>
          <el-form-item label="肝功能不全">
            <el-switch v-model="patientInfo.liver_dysfunction" />
          </el-form-item>
          <el-form-item label="肾功能不全">
            <el-switch v-model="patientInfo.kidney_dysfunction" />
          </el-form-item>
          <el-form-item label="过敏史">
            <el-input
              v-model="patientInfo.allergies"
              placeholder="例如：青霉素、磺胺类"
              type="textarea"
              :rows="2"
            />
          </el-form-item>
        </el-form>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { WarnTriangleFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const props = defineProps({
  herbs: {
    type: Array,
    default: () => []
    // Format: [{ name: '黄芪', dosage: 30 }, ...]
  },
  autoCheck: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['check-complete'])

const checked = ref(false)
const result = ref({
  errors: [],
  warnings: [],
  suggestions: []
})

const activeCollapse = ref([])

const patientInfo = ref({
  is_pregnant: false,
  age: null,
  liver_dysfunction: false,
  kidney_dysfunction: false,
  allergies: ''
})

const isSafe = computed(() => {
  return checked.value &&
    result.value.errors.length === 0 &&
    result.value.warnings.length === 0
})

// 执行安全检查
const performCheck = async () => {
  if (!props.herbs || props.herbs.length === 0) {
    ElMessage.warning('请先选择方剂')
    return
  }

  try {
    const response = await axios.post('/api/v1/diagnosis/safety-check', {
      herbs: props.herbs,
      patient_info: patientInfo.value.age ? patientInfo.value : null
    })

    result.value = response.data
    checked.value = true

    // 通知父组件
    emit('check-complete', {
      safe: isSafe.value,
      result: response.data
    })

    if (isSafe.value) {
      ElMessage.success('用药安全检查通过')
    } else if (result.value.errors.length > 0) {
      ElMessage.error('发现严重用药禁忌，请修改方剂！')
    } else {
      ElMessage.warning('请注意用药警告')
    }
  } catch (error) {
    console.error('安全检查失败:', error)
    ElMessage.error('安全检查失败')
  }
}

// 监听herbs变化，自动检查
watch(() => props.herbs, (newHerbs) => {
  if (newHerbs && newHerbs.length > 0 && props.autoCheck) {
    checked.value = false
    performCheck()
  }
}, { deep: true })

// 暴露方法给父组件
defineExpose({
  performCheck,
  isSafe
})
</script>

<style scoped>
.safety-check-panel {
  background: #FFFFFF;
  border: 1px solid #E7E3DA;
  border-radius: 8px;
  padding: 20px;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.panel-header h4 {
  margin: 0;
  font-size: 16px;
  color: #1E2227;
  display: flex;
  align-items: center;
  gap: 8px;
}

.unchecked-state {
  text-align: center;
  padding: 20px;
}

.alert-item {
  margin: 8px 0;
  line-height: 1.6;
}

.suggestion {
  margin: 4px 0 0 0;
  font-size: 13px;
  color: #6B7077;
  font-style: italic;
}

.check-results ul {
  margin: 8px 0;
  padding-left: 20px;
}

.check-results li {
  margin: 4px 0;
  line-height: 1.6;
}

.safe-section {
  text-align: center;
  padding: 12px;
}
</style>
