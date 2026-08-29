<template>
  <div class="xl-page">
    <div class="xl-page-title">
      <h2>门诊诊疗 · 就诊记录</h2>
      <div>
        <el-dropdown @command="doExport" style="margin-right:10px">
          <el-button><el-icon><Download /></el-icon>&nbsp;导出数据</el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="csv">CSV(Excel 可打开)</el-dropdown-item>
              <el-dropdown-item command="json">JSON</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button type="primary" @click="router.push('/clinic/new')">
          <el-icon><Plus /></el-icon>&nbsp;新建就诊
        </el-button>
      </div>
    </div>

    <div class="xl-card">
      <div class="filters">
        <el-radio-group v-model="specialty" @change="load">
          <el-radio-button value="">全部</el-radio-button>
          <el-radio-button value="surgery">外科疮疡</el-radio-button>
          <el-radio-button value="anorectal">肛肠痔漏</el-radio-button>
          <el-radio-button value="pediatrics">儿科</el-radio-button>
          <el-radio-button value="alchemy">丹药研究</el-radio-button>
        </el-radio-group>
        <el-input v-model="q" placeholder="按患者姓名检索" clearable style="width:220px" @change="load">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
      </div>

      <el-table :data="items" style="width:100%">
        <el-table-column prop="patient_name" label="患者" width="110" />
        <el-table-column label="性别/年龄" width="100">
          <template #default="{ row }">{{ row.gender || '—' }} / {{ row.age ?? '—' }}</template>
        </el-table-column>
        <el-table-column label="专科" width="100">
          <template #default="{ row }"><el-tag size="small" :type="TAG[row.specialty]">{{ SPEC[row.specialty] }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="chief_complaint" label="主诉" show-overflow-tooltip />
        <el-table-column label="辨证" show-overflow-tooltip>
          <template #default="{ row }">{{ dxNames(row) }}</template>
        </el-table-column>
        <el-table-column label="时间" width="130">
          <template #default="{ row }">{{ fmtTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="" width="70">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="router.push('/clinic/' + row.id)">详情</el-button>
          </template>
        </el-table-column>
        <template #empty><div class="xl-empty">暂无就诊记录</div></template>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Search, Download } from '@element-plus/icons-vue'
import { clinicVisits, exportVisitsUrl } from '@/api/clinic'

const router = useRouter()
const SPEC = { surgery: '外科疮疡', anorectal: '肛肠痔漏', pediatrics: '儿科', alchemy: '丹药研究' }
const TAG = { surgery: 'danger', anorectal: 'warning', pediatrics: 'success', alchemy: 'info' }
const items = ref([])
const specialty = ref('')
const q = ref('')

async function load() {
  const params = { limit: 100 }
  if (specialty.value) params.specialty = specialty.value
  if (q.value) params.q = q.value
  const res = await clinicVisits(params)
  items.value = res.items || []
}
function dxNames(row) {
  const r = row.dx_result || {}
  return ((r.syndromes || []).map(s => s.name).slice(0, 2)).join('、') || (r.ai?.disease_suggestion ? 'AI 报告' : '—')
}
const fmtTime = (t) => (t ? String(t).replace('T', ' ').slice(5, 16) : '')
onMounted(load)
function doExport(fmt) {
  window.open(exportVisitsUrl(fmt), '_blank')
}
</script>

<style scoped>
.filters { display: flex; gap: 14px; align-items: center; margin-bottom: 14px; flex-wrap: wrap; }
</style>
