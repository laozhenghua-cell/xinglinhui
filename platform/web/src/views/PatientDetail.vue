<template>
  <div class="patient-detail" v-loading="loading">
    <el-page-header @back="$router.push('/anorectal/patients')" title="返回患者列表">
      <template #content>
        <span class="page-title">{{ patient.name }} - 患者详情</span>
      </template>
    </el-page-header>

    <el-row :gutter="20" class="detail-content">
      <el-col :xs="24" :lg="8">
        <el-card class="info-card">
          <template #header>
            <span>基本信息</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="姓名">{{ patient.name }}</el-descriptions-item>
            <el-descriptions-item label="性别">
              {{ patient.gender === 'male' ? '男' : patient.gender === 'female' ? '女' : '未知' }}
            </el-descriptions-item>
            <el-descriptions-item label="年龄">{{ patient.age }}岁</el-descriptions-item>
            <el-descriptions-item label="手机号">{{ patient.phone }}</el-descriptions-item>
            <el-descriptions-item label="主治医生">{{ patient.doctor }}</el-descriptions-item>
            <el-descriptions-item label="过敏史">{{ patient.allergies || '无' }}</el-descriptions-item>
            <el-descriptions-item label="既往史">{{ patient.medical_history || '无' }}</el-descriptions-item>
            <el-descriptions-item label="建档日期">
              {{ patient.created_at ? patient.created_at.split('T')[0] : '' }}
            </el-descriptions-item>
          </el-descriptions>
          <div class="action-buttons">
            <el-button type="success" @click="$router.push(`/anorectal/consultations/new?patient_id=${patient.id}`)">
              <el-icon><EditPen /></el-icon>
              新建就诊
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="16">
        <el-card>
          <template #header>
            <span>就诊记录</span>
          </template>
          <el-timeline v-if="consultations.length > 0">
            <el-timeline-item
              v-for="item in consultations"
              :key="item.id"
              :timestamp="formatDate(item.created_at)"
              placement="top"
            >
              <el-card shadow="hover" class="consultation-card" @click="$router.push(`/anorectal/consultations/${item.id}`)">
                <div class="consultation-info">
                  <el-tag type="primary">{{ item.disease_type || '未分类' }}</el-tag>
                  <el-tag v-if="item.syndrome" type="success">{{ item.syndrome }}</el-tag>
                </div>
                <p v-if="item.chief_complaint" class="complaint-text">主诉: {{ item.chief_complaint }}</p>
                <p v-if="item.diagnosis" class="diagnosis-text">诊断: {{ item.diagnosis }}</p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无就诊记录" />
        </el-card>

        <el-card class="followup-card">
          <template #header>
            <span>随访记录</span>
          </template>
          <el-table v-if="followups.length > 0" :data="followups" stripe>
            <el-table-column prop="date" label="随访日期" width="120" />
            <el-table-column prop="status" label="恢复状况" width="100" />
            <el-table-column prop="notes" label="随访记录" show-overflow-tooltip />
          </el-table>
          <el-empty v-else description="暂无随访记录" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getPatient, getPatientConsultations, getPatientFollowups } from '@/api/patients'

const route = useRoute()
const loading = ref(false)
const patient = ref({})
const consultations = ref([])
const followups = ref([])

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

async function loadPatient() {
  loading.value = true
  try {
    const id = route.params.id
    patient.value = await getPatient(id)

    try {
      const res = await getPatientConsultations(id)
      consultations.value = res.items || res || []
    } catch (e) {
      console.error('Failed to load consultations:', e)
    }

    try {
      const res = await getPatientFollowups(id)
      followups.value = res.items || res || []
    } catch (e) {
      console.error('Failed to load followups:', e)
    }
  } catch (e) {
    console.error('Failed to load patient:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPatient()
})
</script>

<style scoped>
.patient-detail {
  max-width: 1200px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
}

.detail-content {
  margin-top: 20px;
}

.info-card {
  margin-bottom: 20px;
}

.action-buttons {
  margin-top: 16px;
  text-align: center;
}

.consultation-card {
  cursor: pointer;
}

.consultation-info {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.complaint-text,
.diagnosis-text {
  margin: 4px 0;
  font-size: 14px;
  color: #606266;
}

.followup-card {
  margin-top: 20px;
}

@media (max-width: 768px) {
  .detail-content .el-col {
    margin-bottom: 16px;
  }
}
</style>
