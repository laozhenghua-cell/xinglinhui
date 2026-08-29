<template>
  <div class="kb-detail">
    <el-page-header @back="router.back()">
      <template #content>
        <span class="detail-title">{{ meta?.icon }} {{ displayName(type, detail) || '详情' }}</span>
      </template>
    </el-page-header>

    <el-card v-loading="loading" class="detail-card">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>详情</span>
          <span>
            <el-button size="small" :type="fav ? 'warning' : 'default'" @click="onFav">{{ fav ? '★ 已收藏' : '☆ 收藏' }}</el-button>
            <el-button size="small" plain @click="noteVisible = true">📝 记笔记</el-button>
          </span>
        </div>
      </template>
      <template v-if="detail">
        <div class="detail-head">
          <el-tag v-if="detail.module" size="small" type="info">{{ MODULE_MAP[detail.module] || detail.module }}</el-tag>
          <el-tag v-if="detail.origin_id" size="small" effect="plain">源编号 {{ detail.origin_id }}</el-tag>
        </div>

        <div v-if="aliases.length" class="alias-row">
          <span class="alias-label">别名：</span>
          <el-tag v-for="(a, i) in aliases" :key="i" size="small" class="alias-tag">{{ a }}</el-tag>
        </div>

        <el-descriptions v-if="fields.length" :column="2" border size="small" class="detail-desc">
          <el-descriptions-item
            v-for="f in fields"
            :key="f.key"
            :label="f.label"
            :span="f.span || 1"
          >
            <span v-html="formatValue(detail[f.key])"></span>
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="composition.length" class="detail-section">
          <h4>组成</h4>
          <el-table :data="composition" size="small" border>
            <el-table-column label="药物" min-width="160">
              <template #default="{ row }">
                {{ typeof row === 'object' ? row.name : row }}
              </template>
            </el-table-column>
            <el-table-column label="剂量" width="140">
              <template #default="{ row }">
                {{ typeof row === 'object' ? (row.dose ?? '—') : '—' }}
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div v-if="meridians.length" class="detail-section">
          <h4>归经</h4>
          <el-tag v-for="(m, i) in meridians" :key="i" size="small" type="success" class="alias-tag">{{ m }}</el-tag>
        </div>

        <div v-if="extraEntries.length" class="detail-section">
          <h4>补充信息</h4>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item
              v-for="(e, i) in extraEntries"
              :key="i"
              :label="e.label"
              :span="e.wide ? 2 : 1"
            >
              {{ e.value }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="detail-section" v-if="linked.length || linkedLoading">
          <h4>相关内容</h4>
          <div v-loading="linkedLoading">
            <el-link
              v-for="l in linked"
              :key="`${l.type}-${l.id}`"
              type="primary"
              class="linked-item"
              @click="router.push(`/kb/${l.type}/${l.id}`)"
            >
              <el-tag size="small" class="linked-tag">{{ TYPE_MAP[l.type]?.label || l.type }}</el-tag>
              {{ displayName(l.type, l) }}
              <span class="linked-module">{{ MODULE_MAP[l.module] || '' }}</span>
            </el-link>
            <el-empty v-if="!linkedLoading && !linked.length" description="暂无相关内容" :image-size="60" />
          </div>
        </div>
      </template>
      <el-empty v-else-if="!loading" description="内容不存在或已下线" />
    </el-card>
  </div>

  <el-dialog v-model="noteVisible" title="记笔记" width="480px">
    <el-input v-model="noteText" type="textarea" :rows="5" placeholder="写下你的学习心得…" />
    <template #footer>
      <el-button @click="noteVisible = false">取消</el-button>
      <el-button type="primary" @click="saveNote">保存</el-button>
    </template>
  </el-dialog>

</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getKbItem, getKbLinked } from '@/api/kb'
import { toggleFav, addNote } from '@/api/learn'
import { ElMessage } from 'element-plus'
import { TYPE_MAP, TYPE_FIELDS, MODULE_MAP, displayName } from './config'

const route = useRoute()
const router = useRouter()
const fav = ref(false)
const noteVisible = ref(false)
const noteText = ref('')

async function onFav() {
  const res = await toggleFav({ item_type: route.params.type, item_id: route.params.id })
  fav.value = res.favorited
  ElMessage.success(res.favorited ? '已收藏' : '已取消收藏')
}
async function saveNote() {
  if (!noteText.value.trim()) { ElMessage.warning('笔记内容为空'); return }
  await addNote({ item_type: route.params.type, item_id: route.params.id, content: noteText.value.trim() })
  ElMessage.success('笔记已保存')
  noteVisible.value = false
  noteText.value = ''
}

const type = computed(() => route.params.type)
const id = computed(() => route.params.id)
const meta = computed(() => TYPE_MAP[type.value])

const detail = ref(null)
const linked = ref([])
const loading = ref(false)
const linkedLoading = ref(false)

const aliases = computed(() => {
  const a = detail.value?.aliases
  return Array.isArray(a) ? a.map((x) => (typeof x === 'object' ? x.name || JSON.stringify(x) : x)) : []
})

const composition = computed(() => {
  const c = detail.value?.composition
  return Array.isArray(c) ? c : []
})

const meridians = computed(() => {
  const m = detail.value?.meridians
  return Array.isArray(m) ? m : []
})

const fields = computed(() => {
  if (!detail.value || !meta.value) return []
  const defs = TYPE_FIELDS[type.value] || []
  return defs
    .map(([key, label]) => ({ key, label }))
    .filter((f) => {
      const v = detail.value[f.key]
      return v != null && v !== '' && f.key !== 'composition' && f.key !== 'aliases' && f.key !== 'meridians' && f.key !== 'extra'
    })
})

const extraEntries = computed(() => {
  const ex = detail.value?.extra
  if (!ex || typeof ex !== 'object' || Array.isArray(ex)) return []
  return Object.entries(ex).map(([k, v]) => ({
    label: k,
    value: v == null ? '—' : (typeof v === 'object' ? JSON.stringify(v) : String(v)),
    wide: typeof v === 'string' && v.length > 40
  }))
})

function formatValue(v) {
  if (v == null || v === '') return '—'
  if (typeof v === 'boolean') return v ? '是' : '否'
  if (Array.isArray(v)) return v.join('、')
  if (typeof v === 'object') return JSON.stringify(v)
  const s = String(v)
  return escapeHtml(s).replace(/\n/g, '<br/>')
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
}

async function load() {
  if (!meta.value || !id.value) return
  loading.value = true
  detail.value = null
  try {
    detail.value = await getKbItem(type.value, id.value)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }

  linkedLoading.value = true
  linked.value = []
  try {
    const res = await getKbLinked({ type: type.value, id: id.value })
    linked.value = res?.items || []
  } catch (e) {
    console.error(e)
  } finally {
    linkedLoading.value = false
  }
}

watch(() => [type.value, id.value], load, { immediate: true })
</script>

<style scoped>
.detail-title {
  font-size: 17px;
  font-weight: 600;
  color: #1c2b26;
}

.detail-card {
  margin-top: 16px;
}

.detail-head {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.alias-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 16px;
}

.alias-label {
  font-size: 13px;
  color: #909399;
}

.alias-tag {
  margin-right: 4px;
}

.detail-desc {
  margin-bottom: 8px;
}

.detail-section {
  margin-top: 20px;
}

.detail-section h4 {
  margin: 0 0 10px;
  font-size: 14px;
  color: #1c2b26;
  padding-left: 8px;
  border-left: 3px solid #409eff;
}

.linked-item {
  display: block;
  margin-bottom: 10px;
  font-size: 14px;
}

.linked-tag {
  margin-right: 8px;
}

.linked-module {
  margin-left: 8px;
  font-size: 12px;
  color: #b0b3b8;
}
</style>
