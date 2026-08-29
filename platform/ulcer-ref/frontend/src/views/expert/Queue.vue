<template>
  <div class="expert-queue">
    <el-card>
      <template #header>
        <div class="header">
          <span><el-icon><List /></el-icon> 会诊队列</span>
          <el-button type="primary" @click="loadQueue" :loading="loading" circle>
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="待接单" name="pending">
          <el-badge :value="pendingCount" class="item" />
        </el-tab-pane>
        <el-tab-pane label="已接单" name="accepted">
          <el-badge :value="acceptedCount" class="item" />
        </el-tab-pane>
        <el-tab-pane label="已完成" name="completed">
          <el-badge :value="completedCount" class="item" />
        </el-tab-pane>
      </el-tabs>

      <div v-if="queueItems.length === 0" class="empty">
        <el-empty description="暂无会诊请求" />
      </div>

      <el-row :gutter="20" v-else>
        <el-col :span="8" v-for="item in queueItems" :key="item.request_id">
          <el-card class="consultation-card" shadow="hover">
            <!-- 图片预览 -->
            <div class="card-image">
              <el-image
                v-if="item.first_image_url"
                :src="item.first_image_url"
                fit="cover"
                class="consultation-image"
              >
                <template #error>
                  <div class="image-placeholder">
                    <el-icon><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
              <div v-else class="image-placeholder">
                <el-icon><Picture /></el-icon>
              </div>

              <!-- 紧急程度标签 -->
              <el-tag
                class="urgency-tag"
                :type="getUrgencyType(item.urgency_level)"
                size="small"
              >
                {{ getUrgencyText(item.urgency_level) }}
              </el-tag>
            </div>

            <!-- 信息 -->
            <div class="card-content">
              <h4>{{ item.ulcer_type || '待识别' }}</h4>
              <p class="location">
                <el-icon><Location /></el-icon>
                {{ item.location }}
              </p>
              <p class="complaint">{{ item.chief_complaint?.substring(0, 50) }}...</p>

              <el-divider />

              <div class="meta">
                <span class="time">
                  <el-icon><Clock /></el-icon>
                  {{ formatTime(item.requested_at) }}
                </span>
                <el-tag size="small" v-if="item.priority >= 4" type="danger">
                  高优先级
                </el-tag>
              </div>

              <div class="ai-suggestion" v-if="item.ai_suggestion">
                <el-text type="info" size="small">
                  <el-icon><InfoFilled /></el-icon>
                  {{ item.ai_suggestion }}
                </el-text>
              </div>
            </div>

            <!-- 操作按钮 -->
            <template #footer>
              <div class="card-actions">
                <el-button
                  v-if="activeTab === 'pending'"
                  type="primary"
                  @click="handleAccept(item.request_id)"
                  :loading="accepting === item.request_id"
                  style="width: 100%"
                >
                  接单
                </el-button>
                <el-button
                  v-if="activeTab === 'accepted'"
                  type="success"
                  @click="handleRespond(item)"
                  style="width: 100%"
                >
                  提交诊断
                </el-button>
                <el-button
                  @click="viewDetail(item.consultation_id)"
                  style="width: 100%"
                  :type="activeTab === 'completed' ? 'primary' : 'default'"
                >
                  查看详情
                </el-button>
              </div>
            </template>
          </el-card>
        </el-col>
      </el-row>

      <el-pagination
        v-if="total > pageSize"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="loadQueue"
        style="margin-top: 20px; text-align: center"
      />
    </el-card>

    <!-- 提交诊断对话框 -->
    <el-dialog
      v-model="showRespondDialog"
      title="提交专家诊断"
      width="70%"
      :close-on-click-modal="false"
    >
      <el-form :model="responseForm" label-width="120px">
        <el-form-item label="专家诊断" required>
          <el-input
            v-model="responseForm.expert_diagnosis"
            type="textarea"
            :rows="3"
            placeholder="请输入您的诊断结论"
          />
        </el-form-item>

        <el-form-item label="辨证分析" required>
          <el-input
            v-model="responseForm.syndrome_differentiation"
            type="textarea"
            :rows="3"
            placeholder="请输入辨证分析"
          />
        </el-form-item>

        <el-form-item label="治则治法">
          <el-input
            v-model="responseForm.treatment_principle"
            placeholder="如：清热解毒，托毒排脓"
          />
        </el-form-item>

        <el-divider content-position="left">内治方案</el-divider>

        <el-form-item label="方剂名称">
          <el-input v-model="responseForm.formula_name" placeholder="如：五味消毒饮加减" />
        </el-form-item>

        <el-form-item label="药物组成">
          <el-button @click="addHerb" size="small">添加药物</el-button>
          <div v-for="(herb, index) in responseForm.herbs" :key="index" style="margin-top: 10px">
            <el-input
              v-model="herb.name"
              placeholder="药名"
              style="width: 150px; margin-right: 10px"
            />
            <el-input
              v-model="herb.dosage"
              placeholder="剂量"
              style="width: 100px; margin-right: 10px"
            />
            <el-button @click="removeHerb(index)" type="danger" size="small" circle>
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="服用方法">
          <el-input v-model="responseForm.usage" placeholder="如：水煎服，日一剂" />
        </el-form-item>

        <el-divider content-position="left">外治方案</el-divider>

        <el-form-item label="外敷药物">
          <el-input v-model="responseForm.topical" placeholder="如：油调膏外敷" />
        </el-form-item>

        <el-form-item label="使用频次">
          <el-input v-model="responseForm.frequency" placeholder="如：每日2-3次" />
        </el-form-item>

        <el-divider content-position="left">指导建议</el-divider>

        <el-form-item label="临床指导">
          <el-input
            v-model="responseForm.clinical_advice"
            type="textarea"
            :rows="2"
            placeholder="给基层医生的临床指导建议"
          />
        </el-form-item>

        <el-form-item label="随访计划">
          <el-input
            v-model="responseForm.follow_up_plan"
            type="textarea"
            :rows="2"
            placeholder="如：3-5日后复诊，观察疮口愈合情况"
          />
        </el-form-item>

        <el-form-item label="注意事项">
          <el-input
            v-model="responseForm.precautions"
            type="textarea"
            :rows="2"
            placeholder="需要注意的事项"
          />
        </el-form-item>

        <el-form-item label="饮食建议">
          <el-input
            v-model="responseForm.diet_advice"
            type="textarea"
            :rows="2"
            placeholder="饮食宜忌"
          />
        </el-form-item>

        <el-form-item label="建议转诊">
          <el-switch v-model="responseForm.need_referral" />
          <el-input
            v-if="responseForm.need_referral"
            v-model="responseForm.referral_reason"
            placeholder="转诊原因"
            style="margin-top: 10px"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showRespondDialog = false">取消</el-button>
        <el-button
          type="primary"
          @click="submitResponse"
          :loading="submitting"
          :disabled="!responseForm.expert_diagnosis || !responseForm.syndrome_differentiation"
        >
          提交诊断
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  List,
  Refresh,
  Picture,
  Location,
  Clock,
  InfoFilled,
  Close
} from '@element-plus/icons-vue'
import api from '../../api'
import dayjs from 'dayjs'

const router = useRouter()

// 状态
const activeTab = ref('pending')
const loading = ref(false)
const queueItems = ref([])
const currentPage = ref(1)
const pageSize = ref(9)
const total = ref(0)
const accepting = ref(null)

// 统计
const pendingCount = ref(0)
const acceptedCount = ref(0)
const completedCount = ref(0)

// 回复对话框
const showRespondDialog = ref(false)
const submitting = ref(false)
const currentRequestId = ref('')

const responseForm = reactive({
  expert_diagnosis: '',
  syndrome_differentiation: '',
  treatment_principle: '',
  formula_name: '',
  herbs: [],
  usage: '',
  topical: '',
  frequency: '',
  clinical_advice: '',
  follow_up_plan: '',
  precautions: '',
  diet_advice: '',
  need_referral: false,
  referral_reason: ''
})

// 加载队列
const loadQueue = async () => {
  loading.value = true
  try {
    const response = await api.get('/expert/queue', {
      params: {
        status: activeTab.value,
        skip: (currentPage.value - 1) * pageSize.value,
        limit: pageSize.value
      }
    })
    queueItems.value = response.data
    total.value = response.data.length // 简化版，实际应该返回total

    // 加载统计
    await loadStats()
  } catch (error) {
    ElMessage.error('加载队列失败')
  } finally {
    loading.value = false
  }
}

// 加载统计
const loadStats = async () => {
  try {
    const response = await api.get('/expert/statistics')
    // 简化版统计
    pendingCount.value = response.data.pending_consultations || 0
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

// 切换标签
const handleTabChange = () => {
  currentPage.value = 1
  loadQueue()
}

// 接单
const handleAccept = async (requestId) => {
  try {
    await ElMessageBox.confirm('确定接受此会诊请求吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })

    accepting.value = requestId
    await api.post(`/expert/queue/${requestId}/accept`)
    ElMessage.success('接单成功')
    await loadQueue()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('接单失败')
    }
  } finally {
    accepting.value = null
  }
}

// 提交诊断
const handleRespond = (item) => {
  currentRequestId.value = item.request_id
  // 重置表单
  Object.assign(responseForm, {
    expert_diagnosis: '',
    syndrome_differentiation: '',
    treatment_principle: '',
    formula_name: '',
    herbs: [],
    usage: '',
    topical: '',
    frequency: '',
    clinical_advice: '',
    follow_up_plan: '',
    precautions: '',
    diet_advice: '',
    need_referral: false,
    referral_reason: ''
  })
  showRespondDialog.value = true
}

// 添加药物
const addHerb = () => {
  responseForm.herbs.push({ name: '', dosage: '' })
}

// 移除药物
const removeHerb = (index) => {
  responseForm.herbs.splice(index, 1)
}

// 提交回复
const submitResponse = async () => {
  submitting.value = true
  try {
    const data = {
      expert_diagnosis: responseForm.expert_diagnosis,
      syndrome_differentiation: responseForm.syndrome_differentiation,
      treatment_principle: responseForm.treatment_principle,
      internal_prescription: responseForm.formula_name ? {
        formula_name: responseForm.formula_name,
        herbs: responseForm.herbs.filter(h => h.name),
        usage: responseForm.usage
      } : null,
      external_treatment: responseForm.topical ? {
        topical: responseForm.topical,
        frequency: responseForm.frequency
      } : null,
      clinical_advice: responseForm.clinical_advice,
      follow_up_plan: responseForm.follow_up_plan,
      precautions: responseForm.precautions,
      diet_advice: responseForm.diet_advice,
      need_referral: responseForm.need_referral,
      referral_reason: responseForm.referral_reason
    }

    await api.post(`/expert/consultations/${currentRequestId.value}/respond`, data)
    ElMessage.success('诊断提交成功')
    showRespondDialog.value = false
    await loadQueue()
  } catch (error) {
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}

// 查看详情
const viewDetail = (consultationId) => {
  router.push(`/ulcers/${consultationId}`)
}

// 辅助函数
const getUrgencyType = (level) => {
  const types = {
    'low': 'success',
    'medium': 'warning',
    'high': 'danger',
    'critical': 'danger'
  }
  return types[level] || 'info'
}

const getUrgencyText = (level) => {
  const texts = {
    'low': '轻度',
    'medium': '中度',
    'high': '重度',
    'critical': '危重'
  }
  return texts[level] || level
}

const formatTime = (time) => {
  return dayjs(time).format('MM-DD HH:mm')
}

onMounted(() => {
  loadQueue()
})
</script>

<style scoped>
.expert-queue {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty {
  padding: 60px 0;
}

.consultation-card {
  margin-bottom: 20px;
  transition: transform 0.3s;
}

.consultation-card:hover {
  transform: translateY(-5px);
}

.card-image {
  position: relative;
  width: 100%;
  height: 200px;
  border-radius: 8px 8px 0 0;
  overflow: hidden;
}

.consultation-image {
  width: 100%;
  height: 100%;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  font-size: 48px;
  color: #dcdfe6;
}

.urgency-tag {
  position: absolute;
  top: 10px;
  right: 10px;
}

.card-content {
  padding: 15px 0;
}

.card-content h4 {
  margin: 0 0 10px;
  color: #303133;
  font-size: 18px;
}

.location {
  color: #909399;
  font-size: 14px;
  margin: 5px 0;
}

.complaint {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  margin: 10px 0;
}

.meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #909399;
  font-size: 13px;
}

.time {
  display: flex;
  align-items: center;
  gap: 5px;
}

.ai-suggestion {
  margin-top: 10px;
  padding: 10px;
  background-color: #f4f4f5;
  border-radius: 4px;
}

.card-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
</style>
