<template>
  <div class="consultation-detail" v-if="consultation">
    <el-page-header @back="$router.back()" title="返回">
      <template #content>
        <span class="page-title">会诊详情</span>
      </template>
      <template #extra>
        <el-tag :type="getStatusType(consultation.status)">
          {{ getStatusText(consultation.status) }}
        </el-tag>
      </template>
    </el-page-header>

    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 左侧：患者信息和病情 -->
      <el-col :span="16">
        <!-- 患者信息 -->
        <el-card>
          <template #header>
            <span><el-icon><User /></el-icon> 患者信息</span>
          </template>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="姓名">{{ consultation.patient.name }}</el-descriptions-item>
            <el-descriptions-item label="性别">{{ consultation.patient.gender }}</el-descriptions-item>
            <el-descriptions-item label="年龄">{{ consultation.patient.age }}岁</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 病情信息 -->
        <el-card style="margin-top: 20px">
          <template #header>
            <span><el-icon><Document /></el-icon> 病情信息</span>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="主诉" :span="2">
              {{ consultation.chief_complaint }}
            </el-descriptions-item>
            <el-descriptions-item label="发病部位">
              {{ consultation.location }}
            </el-descriptions-item>
            <el-descriptions-item label="具体位置">
              {{ consultation.location_detail }}
            </el-descriptions-item>
            <el-descriptions-item label="疮疡类型" v-if="consultation.ulcer_type">
              <el-tag type="primary">{{ consultation.ulcer_type }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="病程">
              {{ consultation.duration_days }}天
            </el-descriptions-item>
            <el-descriptions-item label="疼痛程度" v-if="consultation.symptoms">
              <el-rate v-model="consultation.symptoms.pain_level" disabled :max="10" />
            </el-descriptions-item>
            <el-descriptions-item label="紧急程度">
              <el-tag :type="getUrgencyType(consultation.urgency_level)">
                {{ getUrgencyText(consultation.urgency_level) }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>

          <el-divider />

          <el-descriptions :column="2" border>
            <el-descriptions-item label="舌苔">{{ consultation.tongue_coating }}</el-descriptions-item>
            <el-descriptions-item label="舌质">{{ consultation.tongue_body }}</el-descriptions-item>
            <el-descriptions-item label="脉象" :span="2">{{ consultation.pulse }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 疮疡图片 -->
        <el-card style="margin-top: 20px">
          <template #header>
            <span><el-icon><Picture /></el-icon> 疮疡图片</span>
          </template>
          <div class="image-gallery">
            <el-image
              v-for="image in consultation.images"
              :key="image.id"
              :src="image.image_url"
              :preview-src-list="imageUrls"
              :initial-index="consultation.images.indexOf(image)"
              fit="cover"
              class="gallery-image"
            >
              <template #error>
                <div class="image-error">
                  <el-icon><Picture /></el-icon>
                  <span>加载失败</span>
                </div>
              </template>
            </el-image>
          </div>
        </el-card>

        <!-- AI分析结果 -->
        <el-card style="margin-top: 20px" v-if="consultation.ai_analysis">
          <template #header>
            <span><el-icon><Cpu /></el-icon> AI智能分析</span>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="识别类型">
              <el-tag type="primary">{{ consultation.ai_analysis.ulcer_type }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="置信度">
              <el-progress
                :percentage="consultation.ai_analysis.confidence * 100"
                :color="getConfidenceColor(consultation.ai_analysis.confidence)"
              />
            </el-descriptions-item>
            <el-descriptions-item label="证型" :span="2">
              <el-tag>{{ consultation.ai_analysis.syndrome }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="严重程度" :span="2">
              {{ consultation.ai_analysis.severity_level }} ({{ consultation.ai_analysis.severity }}/10)
            </el-descriptions-item>
          </el-descriptions>

          <el-alert
            v-if="consultation.ai_analysis.needs_expert"
            title="AI建议请求专家会诊"
            type="warning"
            :description="consultation.ai_analysis.expert_reason"
            show-icon
            style="margin-top: 15px"
          />

          <div v-if="consultation.ai_analysis.treatment_suggestion" style="margin-top: 15px">
            <h4>AI治疗建议</h4>
            <el-descriptions :column="1" border style="margin-top: 10px">
              <el-descriptions-item label="治则">
                {{ consultation.ai_analysis.treatment_suggestion.principle }}
              </el-descriptions-item>
              <el-descriptions-item label="内治方剂" v-if="consultation.ai_analysis.treatment_suggestion.internal">
                <strong>{{ consultation.ai_analysis.treatment_suggestion.internal.formula }}</strong>
              </el-descriptions-item>
              <el-descriptions-item label="外治法" v-if="consultation.ai_analysis.treatment_suggestion.external">
                {{ consultation.ai_analysis.treatment_suggestion.external.topical }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>

        <!-- 专家诊断 -->
        <el-card style="margin-top: 20px" v-if="consultation.doctor_diagnosis">
          <template #header>
            <span><el-icon><Checked /></el-icon> 专家诊断</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="专家诊断">
              {{ consultation.doctor_diagnosis }}
            </el-descriptions-item>
            <el-descriptions-item label="辨证分析">
              {{ consultation.syndrome_differentiation }}
            </el-descriptions-item>
          </el-descriptions>

          <div v-if="consultation.internal_treatment" style="margin-top: 15px">
            <h4>内治方案</h4>
            <el-descriptions :column="1" border style="margin-top: 10px">
              <el-descriptions-item label="方剂">
                {{ consultation.internal_treatment.formula_name }}
              </el-descriptions-item>
              <el-descriptions-item label="药物组成">
                <el-tag
                  v-for="herb in consultation.internal_treatment.herbs"
                  :key="herb.name"
                  style="margin: 3px"
                >
                  {{ herb.name }} {{ herb.dosage }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <div v-if="consultation.external_treatment" style="margin-top: 15px">
            <h4>外治方案</h4>
            <el-descriptions :column="1" border style="margin-top: 10px">
              <el-descriptions-item label="外敷">
                {{ consultation.external_treatment.topical }}
              </el-descriptions-item>
              <el-descriptions-item label="频次">
                {{ consultation.external_treatment.frequency }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：操作和状态 -->
      <el-col :span="8">
        <!-- 快捷操作 -->
        <el-card>
          <template #header>
            <span>操作</span>
          </template>
          <div class="actions">
            <el-button
              type="warning"
              @click="handleRequestExpert"
              :disabled="consultation.status !== 'ai_done' && consultation.status !== 'draft'"
              style="width: 100%"
            >
              请求专家会诊
            </el-button>
            <el-button
              type="primary"
              style="width: 100%; margin-top: 10px"
              @click="$router.push(`/ulcers/${$route.params.id}/followup`)"
            >
              添加随访记录
            </el-button>
          </div>
        </el-card>

        <!-- 会诊请求状态 -->
        <el-card style="margin-top: 20px" v-if="consultation.consultation_request">
          <template #header>
            <span><el-icon><MessageBox /></el-icon> 会诊请求</span>
          </template>
          <el-timeline>
            <el-timeline-item
              :timestamp="formatTime(consultation.consultation_request.requested_at)"
              placement="top"
            >
              <el-tag>发起会诊请求</el-tag>
            </el-timeline-item>
            <el-timeline-item
              v-if="consultation.consultation_request.status === 'accepted'"
              :timestamp="formatTime(consultation.consultation_request.accepted_at)"
              placement="top"
            >
              <el-tag type="success">专家已接单</el-tag>
            </el-timeline-item>
            <el-timeline-item
              v-if="consultation.consultation_request.status === 'completed'"
              :timestamp="formatTime(consultation.consultation_request.completed_at)"
              placement="top"
            >
              <el-tag type="success">专家已回复</el-tag>
            </el-timeline-item>
          </el-timeline>
        </el-card>

        <!-- 时间轴 -->
        <el-card style="margin-top: 20px">
          <template #header>
            <span><el-icon><Clock /></el-icon> 时间轴</span>
          </template>
          <el-timeline>
            <el-timeline-item :timestamp="formatTime(consultation.created_at)" placement="top">
              创建会诊
            </el-timeline-item>
            <el-timeline-item :timestamp="formatTime(consultation.updated_at)" placement="top">
              最后更新
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Document, Picture, Cpu, Checked, MessageBox, Clock } from '@element-plus/icons-vue'
import api from '../../api'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const consultation = ref(null)

const imageUrls = computed(() => {
  return consultation.value?.images.map(img => img.image_url) || []
})

// 加载会诊详情
const loadConsultation = async () => {
  try {
    const response = await api.get(`/ulcers/consultations/${route.params.id}`)
    consultation.value = response.data
  } catch (error) {
    ElMessage.error('加载会诊详情失败')
  }
}

// 请求专家会诊
const handleRequestExpert = async () => {
  try {
    await ElMessageBox.confirm('确定要请求专家会诊吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await api.post(`/ulcers/consultations/${route.params.id}/request-expert`)
    ElMessage.success('已发送专家会诊请求')
    await loadConsultation()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('请求失败')
    }
  }
}

// 辅助函数
const getStatusType = (status) => {
  const types = {
    'draft': 'info',
    'ai_analyzing': 'warning',
    'ai_done': 'success',
    'pending_expert': 'warning',
    'expert_reviewing': 'primary',
    'completed': 'success'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    'draft': '草稿',
    'ai_analyzing': 'AI分析中',
    'ai_done': 'AI分析完成',
    'pending_expert': '等待专家',
    'expert_reviewing': '专家审核中',
    'completed': '已完成'
  }
  return texts[status] || status
}

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

const getConfidenceColor = (confidence) => {
  if (confidence >= 0.8) return '#67c23a'
  if (confidence >= 0.6) return '#e6a23c'
  return '#f56c6c'
}

const formatTime = (time) => {
  return time ? dayjs(time).format('YYYY-MM-DD HH:mm') : ''
}

onMounted(() => {
  loadConsultation()
})
</script>

<style scoped>
.consultation-detail {
  padding: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
}

.image-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.gallery-image {
  width: 100%;
  height: 200px;
  border-radius: 8px;
  cursor: pointer;
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
}

.actions {
  display: flex;
  flex-direction: column;
}
</style>
