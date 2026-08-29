<template>
  <div class="patients">
    <el-card>
      <template #header>
        <div class="header">
          <span><el-icon><User /></el-icon> 患者管理</span>
          <div class="header-actions">
            <el-input
              v-model="searchText"
              placeholder="搜索患者姓名或电话"
              style="width: 300px; margin-right: 10px"
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="showAddDialog = true">
              <el-icon><Plus /></el-icon> 新建患者
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="patients" v-loading="loading" stripe>
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="gender" label="性别" width="80" />
        <el-table-column prop="age" label="年龄" width="80">
          <template #default="{ row }">
            {{ row.age }}岁
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="电话" width="150" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleView(row)">查看</el-button>
            <el-button size="small" type="primary" @click="createConsultation(row.id)">
              新建会诊
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next, jumper"
        @current-change="loadPatients"
        style="margin-top: 20px; text-align: center"
      />
    </el-card>

    <!-- 新建患者对话框 -->
    <el-dialog v-model="showAddDialog" title="新建患者" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="姓名" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="性别" required>
          <el-radio-group v-model="form.gender">
            <el-radio label="男" />
            <el-radio label="女" />
          </el-radio-group>
        </el-form-item>
        <el-form-item label="年龄">
          <el-input-number v-model="form.age" :min="0" :max="150" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" />
        </el-form-item>
        <el-form-item label="过敏史">
          <el-input v-model="form.allergies" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="既往病史">
          <el-input v-model="form.medical_history" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAdd" :loading="adding">确定</el-button>
      </template>
    </el-dialog>

    <!-- 患者详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="患者详情" width="600px">
      <el-descriptions :column="2" border v-if="currentPatient">
        <el-descriptions-item label="姓名">{{ currentPatient.name }}</el-descriptions-item>
        <el-descriptions-item label="性别">{{ currentPatient.gender }}</el-descriptions-item>
        <el-descriptions-item label="年龄">{{ currentPatient.age }}岁</el-descriptions-item>
        <el-descriptions-item label="电话">{{ currentPatient.phone }}</el-descriptions-item>
        <el-descriptions-item label="地址" :span="2">{{ currentPatient.address }}</el-descriptions-item>
        <el-descriptions-item label="过敏史" :span="2">{{ currentPatient.allergies }}</el-descriptions-item>
        <el-descriptions-item label="既往病史" :span="2">{{ currentPatient.medical_history }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Search, Plus } from '@element-plus/icons-vue'
import api from '../api'
import dayjs from 'dayjs'

const router = useRouter()

const patients = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchText = ref('')

const showAddDialog = ref(false)
const showDetailDialog = ref(false)
const adding = ref(false)
const currentPatient = ref(null)

const form = reactive({
  name: '',
  gender: '男',
  age: null,
  phone: '',
  address: '',
  allergies: '',
  medical_history: ''
})

const loadPatients = async () => {
  loading.value = true
  try {
    const response = await api.get('/patients', {
      params: {
        search: searchText.value,
        skip: (currentPage.value - 1) * pageSize.value,
        limit: pageSize.value
      }
    })
    patients.value = response.data
    total.value = response.data.length
  } catch (error) {
    ElMessage.error('加载患者列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadPatients()
}

const handleAdd = async () => {
  if (!form.name || !form.gender) {
    ElMessage.error('请填写必填项')
    return
  }

  adding.value = true
  try {
    const formData = new FormData()
    Object.keys(form).forEach(key => {
      if (form[key] !== null && form[key] !== '') {
        formData.append(key, form[key])
      }
    })

    await api.post('/patients', formData)
    ElMessage.success('患者创建成功')
    showAddDialog.value = false
    loadPatients()

    // 重置表单
    Object.assign(form, {
      name: '',
      gender: '男',
      age: null,
      phone: '',
      address: '',
      allergies: '',
      medical_history: ''
    })
  } catch (error) {
    ElMessage.error('创建失败')
  } finally {
    adding.value = false
  }
}

const handleView = async (patient) => {
  try {
    const response = await api.get(`/patients/${patient.id}`)
    currentPatient.value = response.data
    showDetailDialog.value = true
  } catch (error) {
    ElMessage.error('加载患者详情失败')
  }
}

const createConsultation = (patientId) => {
  router.push({ path: '/ulcers/new', query: { patient_id: patientId } })
}

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm')
}

onMounted(() => {
  loadPatients()
})
</script>

<style scoped>
.patients {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}
</style>
