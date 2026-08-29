<template>
  <div class="dashboard-premium">
    <!-- Hero Section with Greeting -->
    <div class="hero-section">
      <div class="greeting-card">
        <div class="greeting-content">
          <h1 class="greeting-title">{{ greetingText }}，{{ userName }}</h1>
          <p class="greeting-subtitle">{{ currentDate }} · 今日就诊 {{ stats.todayConsultations }} 人次</p>
        </div>
        <div class="quick-stats">
          <div class="stat-pill">
            <span class="stat-label">待随访</span>
            <span class="stat-value">{{ stats.pendingFollowups || 0 }}</span>
          </div>
          <div class="stat-pill">
            <span class="stat-label">库存预警</span>
            <span class="stat-value alert">{{ stats.inventoryAlerts }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="stats-grid">
      <div class="stat-card primary">
        <div class="stat-icon">
          <el-icon><UserFilled /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-number">{{ stats.patientCount }}</div>
          <div class="stat-label">患者总数</div>
          <div class="stat-trend positive" v-if="stats.patientGrowth">
            <el-icon><TrendCharts /></el-icon>
            +{{ stats.patientGrowth }}% 本月
          </div>
        </div>
      </div>

      <div class="stat-card success">
        <div class="stat-icon">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-number">{{ stats.monthlyConsultations || 0 }}</div>
          <div class="stat-label">本月就诊</div>
          <div class="stat-trend">{{ stats.todayConsultations }} 今日</div>
        </div>
      </div>

      <div class="stat-card warning">
        <div class="stat-icon">
          <el-icon><Coin /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-number">¥{{ formatMoney(stats.monthlyRevenue) }}</div>
          <div class="stat-label">本月收入</div>
          <div class="stat-trend">¥{{ formatMoney(stats.todayRevenue || 0) }} 今日</div>
        </div>
      </div>

      <div class="stat-card info">
        <div class="stat-icon">
          <el-icon><MagicStick /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-number">{{ stats.aiDiagnosisCount || 0 }}</div>
          <div class="stat-label">AI 辅助诊断</div>
          <div class="stat-trend">智能辨证论治</div>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <el-row :gutter="24" class="content-grid">
      <!-- Recent Consultations -->
      <el-col :xs="24" :lg="16">
        <div class="premium-card">
          <div class="card-header">
            <div class="header-left">
              <h2 class="card-title">最近就诊</h2>
              <span class="card-subtitle">Recent Consultations</span>
            </div>
            <el-button type="primary" plain @click="$router.push('/consultations/new')">
              <el-icon><Plus /></el-icon>
              新建就诊
            </el-button>
          </div>
          <div class="card-body">
            <div v-if="recentConsultations.length === 0" class="empty-state">
              <el-icon class="empty-icon"><DocumentCopy /></el-icon>
              <p>暂无就诊记录</p>
            </div>
            <div v-else class="consultation-list">
              <div
                v-for="item in recentConsultations"
                :key="item.id"
                class="consultation-item"
                @click="$router.push(`/consultations/${item.id}`)"
              >
                <div class="consultation-avatar">
                  <el-icon><User /></el-icon>
                </div>
                <div class="consultation-info">
                  <div class="consultation-name">{{ item.patient_name }}</div>
                  <div class="consultation-meta">
                    <el-tag size="small" type="info">{{ item.disease_type }}</el-tag>
                    <span class="consultation-syndrome">{{ item.syndrome }}</span>
                  </div>
                </div>
                <div class="consultation-time">
                  {{ formatTime(item.created_at) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-col>

      <!-- Quick Actions & Knowledge -->
      <el-col :xs="24" :lg="8">
        <!-- Quick Actions -->
        <div class="premium-card actions-card">
          <div class="card-header">
            <div class="header-left">
              <h2 class="card-title">快捷操作</h2>
              <span class="card-subtitle">Quick Actions</span>
            </div>
          </div>
          <div class="card-body">
            <div class="action-grid">
              <div class="action-item primary" @click="$router.push('/patients')">
                <el-icon class="action-icon"><UserFilled /></el-icon>
                <span class="action-label">新增患者</span>
              </div>
              <div class="action-item success" @click="$router.push('/consultations/new')">
                <el-icon class="action-icon"><EditPen /></el-icon>
                <span class="action-label">新建就诊</span>
              </div>
              <div class="action-item warning" @click="$router.push('/diagnosis')">
                <el-icon class="action-icon"><Camera /></el-icon>
                <span class="action-label">图像诊断</span>
              </div>
              <div class="action-item info" @click="$router.push('/billing')">
                <el-icon class="action-icon"><Coin /></el-icon>
                <span class="action-label">收费开单</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Knowledge Base -->
        <div class="premium-card knowledge-card">
          <div class="card-header">
            <div class="header-left">
              <h2 class="card-title">知识库</h2>
              <span class="card-subtitle">TCM Knowledge</span>
            </div>
          </div>
          <div class="card-body">
            <div class="knowledge-list">
              <div class="knowledge-item" @click="$router.push('/knowledge?tab=herbs')">
                <div class="knowledge-icon herbs">
                  <el-icon><Grape /></el-icon>
                </div>
                <div class="knowledge-info">
                  <div class="knowledge-title">中药本草</div>
                  <div class="knowledge-count">{{ knowledgeStats.herbsCount }} 味</div>
                </div>
                <el-icon class="knowledge-arrow"><ArrowRight /></el-icon>
              </div>
              <div class="knowledge-item" @click="$router.push('/knowledge?tab=formulas')">
                <div class="knowledge-icon formulas">
                  <el-icon><Memo /></el-icon>
                </div>
                <div class="knowledge-info">
                  <div class="knowledge-title">经典方剂</div>
                  <div class="knowledge-count">{{ knowledgeStats.formulasCount }} 首</div>
                </div>
                <el-icon class="knowledge-arrow"><ArrowRight /></el-icon>
              </div>
              <div class="knowledge-item" @click="$router.push('/knowledge?tab=cases')">
                <div class="knowledge-icon cases">
                  <el-icon><DocumentCopy /></el-icon>
                </div>
                <div class="knowledge-info">
                  <div class="knowledge-title">临床医案</div>
                  <div class="knowledge-count">{{ knowledgeStats.casesCount }} 例</div>
                </div>
                <el-icon class="knowledge-arrow"><ArrowRight /></el-icon>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { listConsultations } from '@/api/consultations'
import { getRevenueStats } from '@/api/billing'
import { getStockAlerts } from '@/api/inventory'
import { listPatients } from '@/api/patients'
import { listHerbs, listFormulas, listCases } from '@/api/knowledge'

const authStore = useAuthStore()

const stats = ref({
  patientCount: 0,
  todayConsultations: 0,
  monthlyConsultations: 0,
  monthlyRevenue: 0,
  todayRevenue: 0,
  inventoryAlerts: 0,
  aiDiagnosisCount: 0,
  patientGrowth: 0,
  pendingFollowups: 0
})

const recentConsultations = ref([])

const knowledgeStats = ref({
  herbsCount: 10,
  formulasCount: 12,
  casesCount: 5
})

const userName = computed(() => {
  return authStore.user?.name || authStore.user?.email?.split('@')[0] || '医生'
})

const greetingText = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '凌晨好'
  if (hour < 9) return '早上好'
  if (hour < 12) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  if (hour < 22) return '晚上好'
  return '夜深了'
})

const currentDate = computed(() => {
  const now = new Date()
  const days = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  return `${now.getMonth() + 1}月${now.getDate()}日 ${days[now.getDay()]}`
})

function formatMoney(value) {
  if (!value) return '0'
  return value.toLocaleString('zh-CN', { maximumFractionDigits: 0 })
}

function formatTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const now = new Date()
  const diff = now - d
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`

  return d.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}

async function loadDashboard() {
  try {
    const [patientsRes, consultationsRes] = await Promise.allSettled([
      listPatients({ page: 1, size: 1 }),
      listConsultations({ page: 1, size: 8 })
    ])

    if (patientsRes.status === 'fulfilled') {
      stats.value.patientCount = patientsRes.value.total || 0
    }

    if (consultationsRes.status === 'fulfilled') {
      const data = consultationsRes.value
      recentConsultations.value = data.items || data || []
      const today = new Date().toISOString().split('T')[0]
      const todayItems = (data.items || data || []).filter(
        c => c.created_at && c.created_at.startsWith(today)
      )
      stats.value.todayConsultations = todayItems.length

      const thisMonth = new Date().toISOString().substring(0, 7)
      stats.value.monthlyConsultations = (data.items || data || []).filter(
        c => c.created_at && c.created_at.startsWith(thisMonth)
      ).length
    }
  } catch (e) {
    console.error('Failed to load dashboard:', e)
  }

  try {
    const revenue = await getRevenueStats()
    stats.value.monthlyRevenue = revenue.monthly_total || 0
    stats.value.todayRevenue = revenue.today_total || 0
  } catch (e) {
    console.warn('Revenue API not available')
  }

  try {
    const alerts = await getStockAlerts()
    stats.value.inventoryAlerts = Array.isArray(alerts) ? alerts.length : 0
  } catch (e) {
    console.warn('Inventory API not available')
  }

  // Load knowledge stats
  try {
    const [herbsRes, formulasRes, casesRes] = await Promise.allSettled([
      listHerbs({ page: 1, size: 1 }),
      listFormulas({ page: 1, size: 1 }),
      listCases({ page: 1, size: 1 })
    ])

    if (herbsRes.status === 'fulfilled') {
      knowledgeStats.value.herbsCount = herbsRes.value.total || 10
    }
    if (formulasRes.status === 'fulfilled') {
      knowledgeStats.value.formulasCount = formulasRes.value.total || 12
    }
    if (casesRes.status === 'fulfilled') {
      knowledgeStats.value.casesCount = casesRes.value.total || 5
    }
  } catch (e) {
    console.warn('Knowledge stats not available')
  }
}

onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
.dashboard-premium {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0;
}

/* Hero Section */
.hero-section {
  margin-bottom: 32px;
}

.greeting-card {
  background: linear-gradient(135deg, #3C5A78 0%, #2E4760 100%);
  border-radius: 16px;
  padding: 40px;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 16px rgba(60, 90, 120, 0.15);
}

.greeting-content {
  flex: 1;
}

.greeting-title {
  font-family: 'Playfair Display', serif;
  font-size: 36px;
  font-weight: 600;
  margin: 0 0 8px 0;
  letter-spacing: -0.02em;
}

.greeting-subtitle {
  font-size: 15px;
  opacity: 0.85;
  margin: 0;
  font-weight: 400;
}

.quick-stats {
  display: flex;
  gap: 16px;
}

.stat-pill {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  padding: 16px 24px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-pill .stat-label {
  font-size: 13px;
  opacity: 0.8;
}

.stat-pill .stat-value {
  font-size: 28px;
  font-weight: 600;
  font-family: 'Playfair Display', serif;
}

.stat-pill .stat-value.alert {
  color: #FFD93D;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  gap: 20px;
  align-items: flex-start;
  border: 1px solid #E7E3DA;
  transition: all 0.3s ease;
}

.stat-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.stat-card.primary .stat-icon {
  background: rgba(60, 90, 120, 0.1);
  color: #3C5A78;
}

.stat-card.success .stat-icon {
  background: rgba(103, 194, 58, 0.1);
  color: #67C23A;
}

.stat-card.warning .stat-icon {
  background: rgba(230, 162, 60, 0.1);
  color: #E6A23C;
}

.stat-card.info .stat-icon {
  background: rgba(144, 147, 153, 0.1);
  color: #909399;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 32px;
  font-weight: 600;
  color: #1E2227;
  line-height: 1.2;
  font-family: 'Playfair Display', serif;
  margin-bottom: 4px;
}

.stat-info > .stat-label {
  font-size: 14px;
  color: #6B7077;
  margin-bottom: 8px;
  display: block;
}

.stat-trend {
  font-size: 13px;
  color: #6B7077;
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-trend.positive {
  color: #67C23A;
}

/* Premium Cards */
.content-grid {
  margin-bottom: 32px;
}

.premium-card {
  background: #FFFFFF;
  border-radius: 12px;
  border: 1px solid #E7E3DA;
  margin-bottom: 24px;
  overflow: hidden;
}

.card-header {
  padding: 24px 28px;
  border-bottom: 1px solid #E7E3DA;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  flex: 1;
}

.card-title {
  font-family: 'Playfair Display', serif;
  font-size: 20px;
  font-weight: 600;
  color: #1E2227;
  margin: 0 0 4px 0;
  letter-spacing: -0.01em;
}

.card-subtitle {
  font-size: 12px;
  color: #6B7077;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.card-body {
  padding: 0;
}

/* Consultation List */
.consultation-list {
  padding: 16px 0;
}

.consultation-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 28px;
  cursor: pointer;
  transition: background 0.2s;
}

.consultation-item:hover {
  background: #F7F5F1;
}

.consultation-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3C5A78, #2E4760);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.consultation-info {
  flex: 1;
  min-width: 0;
}

.consultation-name {
  font-weight: 500;
  font-size: 15px;
  color: #1E2227;
  margin-bottom: 6px;
}

.consultation-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #6B7077;
}

.consultation-syndrome {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.consultation-time {
  font-size: 13px;
  color: #6B7077;
  flex-shrink: 0;
}

/* Empty State */
.empty-state {
  padding: 60px 20px;
  text-align: center;
  color: #6B7077;
}

.empty-icon {
  font-size: 48px;
  opacity: 0.3;
  margin-bottom: 12px;
}

/* Actions Card */
.actions-card .card-body {
  padding: 20px 28px 24px;
}

.action-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.action-item {
  background: #F7F5F1;
  border-radius: 10px;
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.action-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.action-item.primary:hover {
  border-color: #3C5A78;
  background: rgba(60, 90, 120, 0.05);
}

.action-item.success:hover {
  border-color: #67C23A;
  background: rgba(103, 194, 58, 0.05);
}

.action-item.warning:hover {
  border-color: #E6A23C;
  background: rgba(230, 162, 60, 0.05);
}

.action-item.info:hover {
  border-color: #3C5A78;
  background: rgba(60, 90, 120, 0.05);
}

.action-icon {
  font-size: 28px;
}

.action-item.primary .action-icon {
  color: #3C5A78;
}

.action-item.success .action-icon {
  color: #67C23A;
}

.action-item.warning .action-icon {
  color: #E6A23C;
}

.action-item.info .action-icon {
  color: #3C5A78;
}

.action-label {
  font-size: 14px;
  font-weight: 500;
  color: #1E2227;
}

/* Knowledge Card */
.knowledge-card .card-body {
  padding: 16px 0;
}

.knowledge-list {
  display: flex;
  flex-direction: column;
}

.knowledge-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 28px;
  cursor: pointer;
  transition: background 0.2s;
}

.knowledge-item:hover {
  background: #F7F5F1;
}

.knowledge-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.knowledge-icon.herbs {
  background: rgba(103, 194, 58, 0.1);
  color: #67C23A;
}

.knowledge-icon.formulas {
  background: rgba(60, 90, 120, 0.1);
  color: #3C5A78;
}

.knowledge-icon.cases {
  background: rgba(230, 162, 60, 0.1);
  color: #E6A23C;
}

.knowledge-info {
  flex: 1;
}

.knowledge-title {
  font-size: 15px;
  font-weight: 500;
  color: #1E2227;
  margin-bottom: 4px;
}

.knowledge-count {
  font-size: 13px;
  color: #6B7077;
}

.knowledge-arrow {
  font-size: 16px;
  color: #6B7077;
  opacity: 0;
  transition: opacity 0.2s;
}

.knowledge-item:hover .knowledge-arrow {
  opacity: 1;
}

/* Responsive */
@media (max-width: 768px) {
  .greeting-card {
    flex-direction: column;
    align-items: flex-start;
    padding: 28px 24px;
  }

  .greeting-title {
    font-size: 28px;
  }

  .quick-stats {
    width: 100%;
    margin-top: 20px;
  }

  .stat-pill {
    flex: 1;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .action-grid {
    grid-template-columns: 1fr;
  }
}
</style>
