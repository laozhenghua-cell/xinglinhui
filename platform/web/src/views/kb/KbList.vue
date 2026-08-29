<template>
  <div class="kb-list">
    <el-card v-if="validType">
      <template #header>
        <div class="card-header">
          <span class="page-title">{{ meta.icon }} {{ meta.label }}列表</span>
          <el-input
            v-model="q"
            :placeholder="`检索${meta.label}…`"
            clearable
            style="width: 260px"
            @keyup.enter="reload"
            @clear="reload"
          >
            <template #append>
              <el-button @click="reload">搜索</el-button>
            </template>
          </el-input>
        </div>
      </template>

      <div class="filter-bar">
        <el-select v-model="module" placeholder="专科" clearable style="width: 150px" @change="reload">
          <el-option v-for="m in MODULES" :key="m.key" :label="m.label" :value="m.key" />
        </el-select>
        <el-input v-model="category" placeholder="分类（可选）" clearable style="width: 180px" @keyup.enter="reload" @clear="reload" />
        <el-button @click="reload">筛选</el-button>
      </div>

      <el-table :data="items" v-loading="loading" stripe>
        <el-table-column :label="nameLabel" :min-width="180">
          <template #default="{ row }">
            <el-button type="primary" link @click="openDetail(row)">
              {{ displayName(type, row) }}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column
          v-for="c in columns"
          :key="c.prop"
          :prop="c.prop"
          :label="c.label"
          :min-width="c.minWidth || 150"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <span v-if="c.kind === 'composition'">{{ formatComposition(row.composition) || '—' }}</span>
            <span v-else>{{ formatCell(c, row) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="专科" width="110">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ MODULE_MAP[row.module] || row.module || '—' }}</el-tag>
          </template>
        </el-table-column>
      </el-table>

      <div class="pager">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="size"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="load"
          @size-change="reload"
        />
      </div>
    </el-card>

    <el-empty v-else description="未知的内容类型" />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { listKbItems } from '@/api/kb'
import {
  TYPE_MAP, MODULES, MODULE_MAP,
  NAME_LABEL, LIST_COLUMNS, displayName, truncate, formatComposition
} from './config'

const route = useRoute()
const router = useRouter()

const type = computed(() => route.params.type)
const meta = computed(() => TYPE_MAP[type.value])
const validType = computed(() => !!meta.value)

const q = ref('')
const module = ref('')
const category = ref('')
const page = ref(1)
const size = ref(20)
const total = ref(0)
const items = ref([])
const loading = ref(false)

const nameLabel = computed(() => (meta.value ? NAME_LABEL[type.value] || '名称' : '名称'))
const columns = computed(() => (meta.value ? LIST_COLUMNS[type.value] || [] : []))

function formatCell(c, row) {
  const v = row[c.prop]
  if (v == null || v === '') return '—'
  if (c.kind === 'truncate') return truncate(v, 80)
  if (Array.isArray(v)) return v.join('、')
  return v
}

function openDetail(row) {
  router.push(`/kb/${type.value}/${row.id}`)
}

async function load() {
  if (!validType.value) return
  loading.value = true
  try {
    const res = await listKbItems(type.value, {
      q: q.value.trim() || undefined,
      module: module.value || undefined,
      category: category.value.trim() || undefined,
      page: page.value,
      size: size.value
    })
    items.value = res?.items || []
    total.value = Number(res?.total) || items.value.length
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function reload() {
  page.value = 1
  load()
}

// 路由 /kb/:type 切换时重置筛选（保留 ?module= 传入的专科聚焦）
watch(
  () => [type.value, route.query.module, route.query.q],
  () => {
    q.value = route.query.q || ''
    category.value = ''
    page.value = 1
    module.value = route.query.module || ''
    load()
  },
  { immediate: true }
)
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.page-title {
  font-size: 16px;
  font-weight: 600;
  color: #1c2b26;
}

.filter-bar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
