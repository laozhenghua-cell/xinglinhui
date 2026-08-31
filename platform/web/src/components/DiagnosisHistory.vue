<template>
  <div class="diagnosis-history">
    <div class="history-header">
      <h3>病案历史</h3>
      <el-button :icon="Refresh" @click="loadHistory" size="small">刷新</el-button>
    </div>

    <el-empty v-if="loading" description="加载中..." />

    <el-empty v-else-if="records.length === 0" description="暂无历史记录" />

    <div v-else class="history-timeline">
      <div
        v-for="(record, index) in records"
        :key="record.id"
        class="history-item"
        :class="{ 'is-latest': index === 0 }"
      >
        <div class="item-header">
          <div class="left">
            <span class="date">{{ formatDate(record.created_at) }}</span>
            <el-tag v-if="index === 0" type="success" size="small">最近</el-tag>
          </div>
          <div class="right">
            <el-button
              v-if="index > 0"
              text
              type="primary"
              size="small"
              @click="compareWith(records[0], record)"
            >
              与最近对比
            </el-button>
            <el-button text size="small" @click="viewDetail(record)">
              详情
            </el-button>
          </div>
        </div>

        <div class="item-body">
          <div class="syndrome-info">
            <span class="syndrome-name">{{ record.primary_syndrome_name }}</span>
            <el-progress
              :percentage="Math.round(record.confidence * 100)"
              :color="getConfidenceColor(record.confidence)"
              :stroke-width="6"
              style="width: 150px; margin-left: 12px"
            />
          </div>
          <div class="formula-info" v-if="record.selected_formula">
            <span class="label">方剂：</span>
            <span class="value">{{ record.selected_formula }}</span>
          </div>
          <div class="efficacy-info" v-if="record.efficacy_rating">
            <span class="label">疗效：</span>
            <el-rate
              :model-value="record.efficacy_rating"
              disabled
              size="small"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="辨证记录详情"
      width="min(800px, 94vw)"
    >
      <div v-if="currentRecord" class="record-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="日期">
            {{ formatDate(currentRecord.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="病种">
            {{ currentRecord.disease_type }}
          </el-descriptions-item>
          <el-descriptions-item label="主证型">
            {{ currentRecord.primary_syndrome_name }}
          </el-descriptions-item>
          <el-descriptions-item label="置信度">
            {{ Math.round(currentRecord.confidence * 100) }}%
          </el-descriptions-item>
          <el-descriptions-item label="方剂" :span="2">
            {{ currentRecord.selected_formula || '未选择' }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="symptoms-display" style="margin-top: 20px">
          <h4>症状详情</h4>
          <el-tag
            v-for="(value, key) in flattenSymptoms(currentRecord.selected_symptoms)"
            :key="key"
            style="margin: 4px"
          >
            {{ key }}: {{ value }}
          </el-tag>
        </div>

        <div v-if="currentRecord.doctor_notes" style="margin-top: 20px">
          <h4>医生备注</h4>
          <p>{{ currentRecord.doctor_notes }}</p>
        </div>

        <div style="margin-top: 20px">
          <h4>疗效评价</h4>
          <el-rate
            v-model="efficacyForm.rating"
            :texts="['很差', '较差', '一般', '较好', '很好']"
            show-text
          />
          <el-input
            v-model="efficacyForm.notes"
            type="textarea"
            :rows="3"
            placeholder="疗效备注（可选）"
            style="margin-top: 12px"
          />
          <el-button
            type="primary"
            @click="saveEfficacy"
            style="margin-top: 12px"
            :loading="savingEfficacy"
          >
            保存疗效评价
          </el-button>
        </div>

        <el-divider />
        <div class="followup-schedule">
          <h4>安排复诊</h4>
          <el-date-picker
            v-model="followupDate"
            type="datetime"
            placeholder="选择复诊日期和时间"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%"
          />
          <el-input
            v-model="followupNotes"
            placeholder="复诊重点（可选）"
            style="margin-top: 10px"
          />
          <el-button
            type="success"
            @click="scheduleFollowup"
            :loading="schedulingFollowup"
            style="margin-top: 10px"
          >
            安排复诊
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 对比结果对话框 -->
    <el-dialog
      v-model="compareDialogVisible"
      title="复诊对比分析"
      width="min(900px, 94vw)"
    >
      <div v-if="comparisonResult" class="comparison-result">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="compare-card">
              <div class="card-title">首诊（{{ formatDate(comparisonResult.record_1.date) }}）</div>
              <div class="card-content">
                <p><strong>证型：</strong>{{ comparisonResult.record_1.syndrome }}</p>
                <p><strong>置信度：</strong>{{ Math.round(comparisonResult.record_1.confidence * 100) }}%</p>
                <p><strong>方剂：</strong>{{ comparisonResult.record_1.formula }}</p>
              </div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="compare-card">
              <div class="card-title">复诊（{{ formatDate(comparisonResult.record_2.date) }}）</div>
              <div class="card-content">
                <p><strong>证型：</strong>{{ comparisonResult.record_2.syndrome }}</p>
                <p><strong>置信度：</strong>{{ Math.round(comparisonResult.record_2.confidence * 100) }}%</p>
                <p><strong>方剂：</strong>{{ comparisonResult.record_2.formula }}</p>
              </div>
            </div>
          </el-col>
        </el-row>

        <el-divider />

        <div class="changes-section">
          <h4>变化分析</h4>
          <el-alert
            :type="comparisonResult.changes.syndrome_changed ? 'warning' : 'success'"
            :title="comparisonResult.changes.syndrome_changed ? '证型已改变' : '证型未变'"
            :closable="false"
            style="margin-bottom: 16px"
          />

          <div v-if="comparisonResult.changes.symptoms_added.length > 0">
            <h5>新增症状</h5>
            <el-tag
              v-for="symptom in comparisonResult.changes.symptoms_added"
              :key="symptom.key"
              type="success"
              style="margin: 4px"
            >
              + {{ symptom.key }}
            </el-tag>
          </div>

          <div v-if="comparisonResult.changes.symptoms_removed.length > 0" style="margin-top: 12px">
            <h5>消失症状</h5>
            <el-tag
              v-for="symptom in comparisonResult.changes.symptoms_removed"
              :key="symptom.key"
              type="danger"
              style="margin: 4px"
            >
              - {{ symptom.key }}
            </el-tag>
          </div>

          <div v-if="comparisonResult.changes.symptoms_modified.length > 0" style="margin-top: 12px">
            <h5>变化症状</h5>
            <el-tag
              v-for="symptom in comparisonResult.changes.symptoms_modified"
              :key="symptom.key"
              type="warning"
              style="margin: 4px"
            >
              {{ symptom.key }}: {{ symptom.from }} → {{ symptom.to }}
            </el-tag>
          </div>
        </div>

        <el-divider />

        <div class="suggestion-section">
          <h4>复诊建议</h4>
          <el-alert
            :title="comparisonResult.suggestion"
            type="info"
            :closable="false"
          />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/api/index'

const props = defineProps({
  patientId: {
    type: String,
    required: true
  }
})

const records = ref([])
const loading = ref(false)
const detailDialogVisible = ref(false)
const compareDialogVisible = ref(false)
const currentRecord = ref(null)
const comparisonResult = ref(null)
const savingEfficacy = ref(false)
const schedulingFollowup = ref(false)
const followupDate = ref('')
const followupNotes = ref('')

const efficacyForm = ref({
  rating: 0,
  notes: ''
})

// 加载历史记录
const loadHistory = async () => {
  loading.value = true
  try {
    records.value = await request.get(`/diagnosis/records/patient/${props.patientId}`)
  } catch (error) {
    console.error('加载历史记录失败:', error)
    ElMessage.error('加载历史记录失败')
  } finally {
    loading.value = false
  }
}

// 查看详情
const viewDetail = (record) => {
  currentRecord.value = record
  efficacyForm.value = {
    rating: record.efficacy_rating || 0,
    notes: record.efficacy_notes || ''
  }
  detailDialogVisible.value = true
}

// 对比两次记录
const compareWith = async (record1, record2) => {
  try {
    comparisonResult.value = await request.get(
      `/diagnosis/records/compare/${record1.id}/${record2.id}`
    )
    compareDialogVisible.value = true
  } catch (error) {
    console.error('对比失败:', error)
    ElMessage.error('对比失败')
  }
}

// 保存疗效评价
const saveEfficacy = async () => {
  if (!efficacyForm.value.rating) {
    ElMessage.warning('请选择疗效评分')
    return
  }

  savingEfficacy.value = true
  try {
    await request.put(`/diagnosis/records/${currentRecord.value.id}/efficacy`, {
      efficacy_rating: efficacyForm.value.rating,
      efficacy_notes: efficacyForm.value.notes
    })
    ElMessage.success('疗效评价已保存')
    detailDialogVisible.value = false
    await loadHistory()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    savingEfficacy.value = false
  }
}

const scheduleFollowup = async () => {
  if (!currentRecord.value || !followupDate.value) {
    ElMessage.warning('请选择复诊日期和时间')
    return
  }
  schedulingFollowup.value = true
  try {
    const date = new Date(followupDate.value)
    await request.post(`/diagnosis/records/${currentRecord.value.id}/schedule-followup`, {
      scheduled_date: date.toISOString(),
      notes: followupNotes.value || undefined
    })
    ElMessage.success('复诊已安排')
    followupDate.value = ''
    followupNotes.value = ''
  } catch (error) {
    console.error('安排复诊失败:', error)
  } finally {
    schedulingFollowup.value = false
  }
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 置信度颜色
const getConfidenceColor = (confidence) => {
  if (confidence >= 0.8) return '#67C23A'
  if (confidence >= 0.6) return '#E6A23C'
  return '#F56C6C'
}

// 扁平化症状对象
const flattenSymptoms = (symptoms) => {
  const result = {}
  for (const [key, value] of Object.entries(symptoms)) {
    if (typeof value === 'object' && value !== null) {
      result[key] = JSON.stringify(value)
    } else {
      result[key] = value
    }
  }
  return result
}

onMounted(() => {
  loadHistory()
})

defineExpose({
  loadHistory
})
</script>

<style scoped>
.diagnosis-history {
  background: #FFFFFF;
  border-radius: 8px;
  padding: 20px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.history-header h3 {
  margin: 0;
  font-size: 18px;
  color: #1E2227;
}

.history-timeline {
  position: relative;
}

.history-item {
  border-left: 2px solid #E7E3DA;
  padding-left: 20px;
  padding-bottom: 20px;
  position: relative;
}

.history-item::before {
  content: '';
  position: absolute;
  left: -6px;
  top: 5px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #E7E3DA;
}

.history-item.is-latest {
  border-left-color: #3C5A78;
}

.history-item.is-latest::before {
  background: #3C5A78;
}

.item-header { flex-wrap: wrap; gap: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.item-header .left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date {
  font-size: 14px;
  color: #6B7077;
}

.item-body {
  background: #F7F5F1;
  border-radius: 6px;
  padding: 12px;
}

.syndrome-info { flex-wrap: wrap;
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.syndrome-name { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  font-weight: 500;
  color: #1E2227;
  font-size: 16px;
}

.formula-info,
.efficacy-info {
  font-size: 14px;
  color: #6B7077;
  margin-top: 8px;
}

.label {
  font-weight: 500;
}

.compare-card {
  border: 1px solid #E7E3DA;
  border-radius: 8px;
  overflow: hidden;
}

.card-title {
  background: #3C5A78;
  color: #FFFFFF;
  padding: 12px;
  font-weight: 500;
}

.card-content {
  padding: 16px;
}

.card-content p {
  margin: 8px 0;
}

.changes-section h4,
.suggestion-section h4 {
  margin: 16px 0 12px 0;
  color: #1E2227;
}

.changes-section h5 {
  margin: 12px 0 8px 0;
  color: #6B7077;
  font-size: 14px;
}
</style>
