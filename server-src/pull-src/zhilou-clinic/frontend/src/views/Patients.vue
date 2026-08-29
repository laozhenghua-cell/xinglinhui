<template>
  <div class="patients-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>患者管理</span>
          <div class="header-actions">
            <el-input
              v-model="searchText"
              placeholder="搜索患者姓名/手机号"
              prefix-icon="Search"
              clearable
              style="width: 240px"
              @input="handleSearch"
            />
            <el-button type="primary" @click="showAddDialog">
              <el-icon><Plus /></el-icon>
              新增患者
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="patients" v-loading="loading" stripe>
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="70">
          <template #default="{ row }">
            {{ row.gender === 'male' ? '男' : row.gender === 'female' ? '女' : '未知' }}
          </template>
        </el-table-column>
        <el-table-column prop="age" label="年龄" width="70" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="doctor" label="主治医生" width="100" />
        <el-table-column prop="chief_complaint" label="主诉" show-overflow-tooltip />
        <el-table-column prop="created_at" label="建档日期" width="120">
          <template #default="{ row }">
            {{ row.created_at ? row.created_at.split('T')[0] : '' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="$router.push(`/patients/${row.id}`)">
              详情
            </el-button>
            <el-button type="warning" link @click="handleEdit(row)">
              编辑
            </el-button>
            <el-popconfirm title="确定删除该患者？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-area">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadPatients"
          @current-change="loadPatients"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="editingPatient ? '编辑患者' : '新增患者'"
      width="500px"
    >
      <el-form
        ref="patientFormRef"
        :model="patientForm"
        :rules="patientRules"
        label-width="80px"
      >
        <el-form-item label="姓名" prop="name">
          <el-input v-model="patientForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="patientForm.gender">
            <el-radio value="male">男</el-radio>
            <el-radio value="female">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="年龄" prop="age">
          <el-input-number v-model="patientForm.age" :min="0" :max="150" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="patientForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="主治医生">
          <el-input v-model="patientForm.doctor" placeholder="请输入主治医生" />
        </el-form-item>
        <el-form-item label="主诉">
          <el-input
            v-model="patientForm.chief_complaint"
            type="textarea"
            :rows="3"
            placeholder="请输入主诉"
          />
        </el-form-item>
        <el-form-item label="过敏史">
          <el-input v-model="patientForm.allergies" placeholder="请输入过敏史" />
        </el-form-item>
        <el-form-item label="既往史">
          <el-input
            v-model="patientForm.medical_history"
            type="textarea"
            :rows="2"
            placeholder="请输入既往病史"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { listPatients, createPatient, updatePatient, deletePatient } from '@/api/patients'
import { ElMessage } from 'element-plus'

const patients = ref([])
const loading = ref(false)
const saving = ref(false)
const searchText = ref('')
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const editingPatient = ref(null)
const patientFormRef = ref(null)

const patientForm = reactive({
  name: '',
  gender: 'male',
  age: null,
  phone: '',
  doctor: '',
  chief_complaint: '',
  allergies: '',
  medical_history: ''
})

const patientRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }]
}

let searchTimer = null

function handleSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    loadPatients()
  }, 300)
}

async function loadPatients() {
  loading.value = true
  try {
    const res = await listPatients({
      page: page.value,
      size: pageSize.value,
      search: searchText.value || undefined
    })
    patients.value = res.items || res || []
    total.value = res.total || patients.value.length
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function showAddDialog() {
  editingPatient.value = null
  Object.assign(patientForm, {
    name: '',
    gender: 'male',
    age: null,
    phone: '',
    doctor: '',
    chief_complaint: '',
    allergies: '',
    medical_history: ''
  })
  dialogVisible.value = true
}

function handleEdit(row) {
  editingPatient.value = row
  Object.assign(patientForm, {
    name: row.name,
    gender: row.gender,
    age: row.age,
    phone: row.phone,
    doctor: row.doctor,
    chief_complaint: row.chief_complaint,
    allergies: row.allergies,
    medical_history: row.medical_history
  })
  dialogVisible.value = true
}

async function handleSave() {
  const valid = await patientFormRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    if (editingPatient.value) {
      await updatePatient(editingPatient.value.id, patientForm)
      ElMessage.success('更新成功')
    } else {
      await createPatient(patientForm)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    loadPatients()
  } catch (e) {
    // handled by interceptor
  } finally {
    saving.value = false
  }
}

async function handleDelete(id) {
  try {
    await deletePatient(id)
    ElMessage.success('删除成功')
    loadPatients()
  } catch (e) {
    // handled by interceptor
  }
}

onMounted(() => {
  loadPatients()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.pagination-area {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .header-actions {
    flex-direction: column;
    width: 100%;
  }

  .header-actions .el-input {
    width: 100% !important;
  }
}
</style>
