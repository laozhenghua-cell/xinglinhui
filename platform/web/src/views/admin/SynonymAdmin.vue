<template>
  <div class="syn-page">
    <el-card shadow="never" style="margin-bottom:14px">
      <template #header>
        <b>🗂️ 口语词库管理</b>
        <span class="hint">患者白话 → 标准证候标签;新增/修改后立即生效于白话主诉解析</span>
      </template>

      <div class="add-row">
        <el-input v-model="nk" placeholder="口语词,如:脑壳疼" style="width: 220px" />
        <el-input v-model="nl" placeholder="映射标签(顿号分隔),如:头痛" style="width: 380px; margin: 0 10px" @keyup.enter="doAdd" />
        <el-button type="primary" @click="doAdd">新增 / 更新</el-button>
      </div>

      <div class="filter-row">
        <el-input v-model="q" placeholder="按关键词过滤…" clearable style="width: 260px" @keyup.enter="reload" @clear="reload" />
        <el-button @click="reload">搜索</el-button>
        <span class="hint" style="margin-left:auto">共 {{ total }} 条</span>
      </div>

      <el-table :data="items" v-loading="loading" stripe size="small" style="margin-top:10px">
        <el-table-column prop="keyword" label="口语词" min-width="180">
          <template #default="{ row }">
            <el-input v-if="editing === row.keyword" v-model="row.keyword" size="small" style="width: 160px" />
            <b v-else>{{ row.keyword }}</b>
          </template>
        </el-table-column>
        <el-table-column label="映射标签" min-width="320">
          <template #default="{ row }">
            <el-input v-if="editing === row.keyword" v-model="row.labelsText" size="small" placeholder="顿号分隔" />
            <template v-else>
              <el-tag v-for="l in row.labels" :key="l" size="small" type="success" style="margin:2px 3px 2px 0">{{ l }}</el-tag>
            </template>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <template v-if="editing === row.keyword">
              <el-button size="small" type="primary" @click="saveRow(row)">保存</el-button>
              <el-button size="small" @click="editing = ''">取消</el-button>
            </template>
            <template v-else>
              <el-button size="small" @click="startEdit(row)">编辑</el-button>
              <el-button size="small" type="danger" plain @click="doDel(row)">删除</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listSynonyms, upsertSynonym, deleteSynonym } from '@/api/admin'

const items = ref([])
const total = ref(0)
const q = ref('')
const nk = ref('')
const nl = ref('')
const editing = ref('')
const loading = ref(false)

async function reload() {
  loading.value = true
  try {
    const res = await listSynonyms(q.value)
    items.value = (res.items || []).map((x) => ({ ...x, labelsText: (x.labels || []).join('、') }))
    total.value = res.total ?? items.value.length
  } catch (e) {
    ElMessage.error('加载失败:' + (e?.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}
async function doAdd() {
  const kw = nk.value.trim()
  const labels = nl.value.split(/[、,]/).map((s) => s.trim()).filter(Boolean)
  if (!kw || !labels.length) {
    ElMessage.warning('请填写口语词与至少一个标签')
    return
  }
  await upsertSynonym(kw, labels)
  ElMessage.success(`已保存「${kw}」`)
  nk.value = ''
  nl.value = ''
  await reload()
}
function startEdit(row) {
  editing.value = row.keyword
  row.labelsText = (row.labels || []).join('、')
}
async function saveRow(row) {
  const kw = (row.keyword || '').trim()
  const labels = (row.labelsText || '').split(/[、,]/).map((s) => s.trim()).filter(Boolean)
  if (!kw || !labels.length) {
    ElMessage.warning('关键词与标签不能为空')
    return
  }
  await upsertSynonym(kw, labels)
  editing.value = ''
  ElMessage.success('已保存')
  await reload()
}
async function doDel(row) {
  await ElMessageBox.confirm(`确定删除「${row.keyword}」?`, '提示', { type: 'warning' })
  await deleteSynonym(row.keyword)
  ElMessage.success('已删除')
  await reload()
}
onMounted(reload)
</script>

<style scoped>
.syn-page { padding: 4px; }
.hint { color: #999; font-size: 12px; margin-left: 10px; }
.add-row { display: flex; align-items: center; flex-wrap: wrap; }
.filter-row { display: flex; align-items: center; gap: 8px; margin-top: 12px; }
</style>
