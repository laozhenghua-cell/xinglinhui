<template>
  <div class="page">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="title-side">
            <span>方剂库</span>
            <el-button link type="primary" size="small" @click="router.push('/kb?module=surgery')">
              在知识总库检索该专科内容
            </el-button>
          </div>
          <el-input
            v-model="q"
            placeholder="检索方名 / 功效 / 适应证 / 组成"
            prefix-icon="Search"
            clearable
            style="width: 280px"
            @keyup.enter="load"
            @clear="load"
          />
        </div>
      </template>

      <div class="filter-bar">
        <el-select v-model="method" placeholder="治法（消/托/补）" clearable style="width:150px" @change="load">
          <el-option label="消" value="消" />
          <el-option label="托" value="托" />
          <el-option label="补" value="补" />
        </el-select>
        <el-select v-model="usageType" placeholder="内治/外治" clearable style="width:150px" @change="load">
          <el-option label="内服" value="内服" />
          <el-option label="外用" value="外用" />
          <el-option label="内服外用" value="内服外用" />
        </el-select>
        <el-select v-model="domain" placeholder="学科领域" clearable style="width:150px" @change="load">
          <el-option label="疮疡" value="疮疡" />
          <el-option label="骨伤" value="骨伤" />
          <el-option label="杂病" value="杂病" />
          <el-option label="妇科" value="妇科" />
        </el-select>
      </div>

      <el-table :data="formulas" v-loading="loading" stripe>
        <el-table-column prop="name" label="方名" width="170">
          <template #default="{ row }">
            <el-button type="primary" link @click="openDetail(row)">{{ row.name }}</el-button>
          </template>
        </el-table-column>
        <el-table-column prop="method" label="治法" width="70">
          <template #default="{ row }"><el-tag v-if="row.method" size="small">{{ row.method }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="usage_type" label="用法" width="100">
          <template #default="{ row }"><el-tag v-if="row.usage_type" size="small" type="info">{{ row.usage_type }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="domain" label="领域" width="90" />
        <el-table-column prop="source" label="出处" width="200" show-overflow-tooltip />
        <el-table-column prop="function" label="功效" min-width="180" show-overflow-tooltip />
        <el-table-column prop="indication" label="适应证" min-width="200" show-overflow-tooltip />
      </el-table>
      <el-empty v-if="!loading && !formulas.length" description="暂无方剂数据" />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="current?.name" width="720px" top="5vh">
      <div v-if="current" class="formula-detail">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="方名">{{ current.name }}</el-descriptions-item>
          <el-descriptions-item label="出处">{{ current.source || '—' }}</el-descriptions-item>
          <el-descriptions-item label="治法">{{ current.method || '—' }}</el-descriptions-item>
          <el-descriptions-item label="用法">{{ current.usage_type || '—' }}</el-descriptions-item>
          <el-descriptions-item label="领域">{{ current.domain || '—' }}</el-descriptions-item>
          <el-descriptions-item label="毒性">
            <el-tag v-if="current.toxicity" type="danger" size="small">{{ current.toxicity }}</el-tag>
            <span v-else>—</span>
          </el-descriptions-item>
          <el-descriptions-item label="组成" :span="2">{{ current.composition || '—' }}</el-descriptions-item>
          <el-descriptions-item label="剂量" :span="2">{{ current.dosage || '—' }}</el-descriptions-item>
          <el-descriptions-item label="功效" :span="2">{{ current.function || '—' }}</el-descriptions-item>
          <el-descriptions-item label="适应证" :span="2">{{ current.indication || '—' }}</el-descriptions-item>
          <el-descriptions-item label="用法用量" :span="2">{{ current.usage || '—' }}</el-descriptions-item>
          <el-descriptions-item label="禁忌" :span="2">{{ current.contraindications || '—' }}</el-descriptions-item>
          <el-descriptions-item label="加减" :span="2">{{ current.modifications || '—' }}</el-descriptions-item>
          <el-descriptions-item label="制备" :span="2">{{ current.preparation || '—' }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listFormulas } from '../api'

const router = useRouter()
const formulas = ref([])
const loading = ref(false)
const q = ref('')
const method = ref('')
const usageType = ref('')
const domain = ref('')
const dialogVisible = ref(false)
const current = ref(null)

async function load() {
  loading.value = true
  try {
    const res = await listFormulas({
      q: q.value || undefined,
      method: method.value || undefined,
      usage_type: usageType.value || undefined,
      domain: domain.value || undefined
    })
    formulas.value = res || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function openDetail(row) {
  current.value = row
  dialogVisible.value = true
}

onMounted(load)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.title-side {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.formula-detail {
  max-height: 70vh;
  overflow-y: auto;
}
</style>
