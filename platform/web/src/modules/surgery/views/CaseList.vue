<template>
  <div class="page">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="title-side">
            <span>医案库</span>
            <el-button link type="primary" size="small" @click="router.push('/kb?module=surgery')">
              在知识总库检索该专科内容
            </el-button>
          </div>
          <el-select v-model="domain" placeholder="学科领域" clearable style="width:150px" @change="load">
            <el-option label="疮疡" value="疮疡" />
            <el-option label="骨伤" value="骨伤" />
            <el-option label="妇科" value="妇科" />
          </el-select>
        </div>
      </template>

      <el-table :data="cases" v-loading="loading" stripe>
        <el-table-column prop="id" label="编号" width="70" />
        <el-table-column prop="patient_name" label="患者" width="100">
          <template #default="{ row }">{{ row.patient_name || '—' }}</template>
        </el-table-column>
        <el-table-column label="基本信息" width="110">
          <template #default="{ row }">{{ row.gender || '' }} {{ row.age ? row.age + '岁' : '' }}</template>
        </el-table-column>
        <el-table-column prop="stage" label="阶段" width="80">
          <template #default="{ row }"><el-tag v-if="row.stage" size="small">{{ row.stage }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="chief_complaint" label="主诉" min-width="180" show-overflow-tooltip />
        <el-table-column prop="syndrome" label="证型" width="120" show-overflow-tooltip />
        <el-table-column prop="domain" label="领域" width="80" />
        <el-table-column label="疗效" width="90">
          <template #default="{ row }"><el-tag v-if="row.effect" size="small" type="success">{{ row.effect }}</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="router.push(`/surgery/cases/${row.id}`)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && !cases.length" description="暂无医案数据" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listCases } from '../api'

const router = useRouter()
const cases = ref([])
const domain = ref('')
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    cases.value = (await listCases({ domain: domain.value || undefined })) || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-side {
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>
