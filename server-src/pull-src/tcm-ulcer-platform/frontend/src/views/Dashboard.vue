<template>
  <div class="dashboard">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>中医疮疡远程协作平台</h1>
          <div class="user-info">
            <span>{{ user?.name }} ({{ userRoleText }})</span>
            <el-button @click="handleLogout" size="small">退出</el-button>
          </div>
        </div>
      </el-header>

      <el-container>
        <el-aside width="200px">
          <el-menu :default-active="$route.path" router>
            <el-menu-item index="/dashboard">
              <el-icon><House /></el-icon>
              <span>首页</span>
            </el-menu-item>
            <el-menu-item index="/patients" v-if="user?.role === 'doctor'">
              <el-icon><User /></el-icon>
              <span>患者管理</span>
            </el-menu-item>
            <el-menu-item index="/ulcers/new" v-if="user?.role === 'doctor'">
              <el-icon><Plus /></el-icon>
              <span>新建会诊</span>
            </el-menu-item>
            <el-menu-item index="/expert/queue" v-if="user?.role === 'expert'">
              <el-icon><List /></el-icon>
              <span>会诊队列</span>
            </el-menu-item>
            <el-menu-item index="/knowledge">
              <el-icon><Reading /></el-icon>
              <span>知识库</span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <el-main>
          <div class="stats-grid" v-if="stats">
            <el-card>
              <el-statistic title="总会诊数" :value="stats.total_consultations" />
            </el-card>
            <el-card>
              <el-statistic title="本月会诊" :value="stats.monthly_consultations" />
            </el-card>
            <el-card>
              <el-statistic title="待处理" :value="stats.pending_consultations" />
            </el-card>
            <el-card>
              <el-statistic title="治愈病例" :value="stats.cured_cases" />
            </el-card>
          </div>

          <el-card style="margin-top: 20px">
            <template #header>
              <span>快捷操作</span>
            </template>
            <div class="quick-actions">
              <el-button type="primary" @click="$router.push('/ulcers/new')" v-if="user?.role === 'doctor'">
                新建疮疡会诊
              </el-button>
              <el-button type="success" @click="$router.push('/expert/queue')" v-if="user?.role === 'expert'">
                查看会诊队列
              </el-button>
              <el-button @click="$router.push('/knowledge')">浏览知识库</el-button>
            </div>
          </el-card>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { House, User, Plus, List, Reading } from '@element-plus/icons-vue'
import api from '../api'

const router = useRouter()
const authStore = useAuthStore()
const user = computed(() => authStore.user)
const stats = ref(null)

const userRoleText = computed(() => {
  return user.value?.role === 'expert' ? '专家' : '基层医生'
})

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

const loadStats = async () => {
  try {
    const response = await api.get('/analytics/overview')
    stats.value = response.data
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.dashboard {
  height: 100vh;
}

.el-header {
  background-color: #409eff;
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h1 {
  margin: 0;
  font-size: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.el-aside {
  background-color: #fff;
  border-right: 1px solid #e4e7ed;
}

.el-main {
  background-color: #f5f7fa;
  padding: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.quick-actions {
  display: flex;
  gap: 10px;
}
</style>
