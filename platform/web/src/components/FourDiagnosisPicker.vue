<template>
  <div class="fdx">
    <!-- 已选摘要 -->
    <div class="fdx-summary" v-if="totalCount">
      <span>已选 {{ totalCount }} 项:</span>
      <el-tag v-for="s in allSelected.slice(0, 12)" :key="s" size="small" type="success" closable @close="removeLabel(s)" style="margin:2px 4px">{{ s }}</el-tag>
      <span v-if="allSelected.length > 12" class="more">…共 {{ allSelected.length }} 项</span>
      <el-button link type="danger" size="small" @click="clearAll">清空全部</el-button>
    </div>

    <!-- 望闻问切 -->
    <el-collapse v-model="openSections">
      <el-collapse-item v-for="(sec, si) in categories" :key="si" :name="si">
        <template #title>
          <span class="sec-title">{{ sec.section }}</span>
          <span class="sec-count">{{ countOf(sec) }} 项</span>
        </template>
        <div v-for="(g, gi) in sec.groups" :key="gi" class="fdx-group">
          <div class="group-name">{{ g.name }}</div>
          <div class="chips">
            <span v-for="it in g.items" :key="it" class="chip" :class="{ on: isOn(it) }" @click="toggle(it)">
              {{ it }}
            </span>
          </div>
        </div>
      </el-collapse-item>
    </el-collapse>

    <!-- 补充描述 -->
    <div class="fdx-detail">
      <el-input v-model="detailText" type="textarea" :rows="2" placeholder="补充描述(病史、病程、诊疗经过等,可自由输入)" />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { buildCategories, buildPediatricCategories } from '@/data/fourDiagnosis'

const props = defineProps({
  modelValue: { type: Object, default: () => ({}) },
  specialty: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])

const categories = ref([])
const openSections = ref([0, 1, 2, 3])
// 按字段分桶的选中集
const picked = ref({ tongue: [], pulse: [], local: [], systemic: [], symptoms: [] })
const detailText = ref(props.modelValue?.detail || '')

async function loadCategories() {
  const sp = props.specialty
  if (sp === 'pediatrics') {
    categories.value = await buildPediatricCategories()
    return
  }
  if (sp === 'surgery') {
    categories.value = await buildSurgeryCategories()
    return
  }
  if (sp === 'anorectal') {
    categories.value = await buildAnorectalCategories()
    return
  }
  if (sp === 'alchemy') {
    categories.value = await buildAlchemyCategories()
    return
  }
  categories.value = buildCategories(sp)
}

// 疮疡:原版辨证要点(阳证阴证鉴别 + 疮形 + 舌脉,依 13 证型与 107 病种原文归纳)
async function buildSurgeryCategories() {
  const groups = [
    { name: '疮形·颜色', field: 'local', items: ['局部红肿', '色红灼热', '色白漫肿', '色暗紫滞', '疮顶高突', '疮顶塌陷', '根盘紧束', '根脚散漫', '粟粒样脓头', '坚硬如石'] },
    { name: '疮形·脓腐', field: 'local', items: ['化脓', '波动感(应指)', '脓水稠厚', '脓水稀薄', '腐肉不脱', '新肉不生', '窦道形成', '疮面凹陷', '溃久不敛'] },
    { name: '部位', field: 'local', items: ['头面', '颈项', '背部', '胸胁', '乳房', '腹部', '脐部', '四肢', '手足', '会阴'] },
    { name: '全身(阳证阴证鉴别)', field: 'symptoms', items: ['发热', '恶寒', '口渴喜冷饮', '口渴不喜饮', '便秘', '溲赤', '神昏谵语', '神疲乏力', '畏寒肢冷', '纳呆', '恶心呕吐', '骨节酸痛'] },
    { name: '舌象', field: 'tongue', items: ['舌红', '舌绛', '舌紫暗', '舌有瘀斑', '舌淡', '苔黄', '苔黄腻', '苔白', '苔少', '苔燥'] },
    { name: '脉象', field: 'pulse', items: ['脉数', '脉滑', '脉弦', '脉洪', '脉沉', '脉细', '脉涩', '脉细数', '脉虚'] },
  ]
  return [{ section: '疮疡辨证(阳证阴证·消托补)', groups }]
}

// 痔漏:原版症状字典结构化问诊(/diagnosis/symptoms)
async function buildAnorectalCategories() {
  try {
    const res = await fetch('/api/v1/diagnosis/symptoms')
    const rows = await res.json()
    const bySub = {}
    for (const r of (rows || [])) {
      const sub = r.subcategory || r.category || '全身'
      const chips = []
      const opts = r.options || {}
      if (opts && opts.type === 'select' && (opts.choices || []).length) {
        chips.push(...opts.choices)
      } else if (opts && opts.fields) {
        for (const [fn, fc] of Object.entries(opts.fields)) {
          // 复合项只取选项词(与后端症状字典映射一致);纯布尔复合字段跳过
          for (const c of (fc && fc.choices) || []) chips.push(c)
        }
      } else if (opts && opts.type === 'boolean') {
        chips.push(r.display_name || r.name)
      } else {
        chips.push(r.display_name || r.name)
      }
      if (chips.length) (bySub[sub] = bySub[sub] || []).push(...chips)
    }
    const groups = []
    for (const [sub, items] of Object.entries(bySub)) {
      let field = 'symptoms'
      if (sub.includes('舌')) field = 'tongue'
      else if (sub.includes('脉') || sub.includes('按') || sub.includes('切')) field = 'pulse'
      else if (sub.includes('局部') || sub.includes('肛门')) field = 'local'
      groups.push({ name: sub, field, items: [...new Set(items)] })
    }
    return [{ section: '痔漏辨证(原版四诊字典)', groups }]
  } catch (e) {
    return buildCategories('anorectal')
  }
}

// 丹药:原版引导式问诊(部位→疮形→脓液→全身→舌脉→特殊人群→中毒征象)
async function buildAlchemyCategories() {
  try {
    const mod = await import('@/modules/alchemy/data/assist-ontology.json')
    const steps = mod.default?.steps || mod.default || []
    const groups = []
    for (const st of steps) {
      const items = (st.options || []).map((o) => (typeof o === 'object' ? o.label : o)).filter(Boolean)
      if (!items.length) continue
      const name = st.name || st.id
      let field = 'symptoms'
      if (name.includes('舌')) field = 'tongue'
      else if (name.includes('脉')) field = 'pulse'
      else if (name.includes('部位') || name.includes('疮形') || name.includes('脓')) field = 'local'
      groups.push({ name, field, items })
    }
    return [{ section: '丹药辨证(原版引导问诊)', groups }]
  } catch (e) {
    return buildCategories('alchemy')
  }
}

onMounted(async () => {
  await loadCategories()
  // 初始化:从 modelValue 回填(逗号/顿号切分)
  const mv = props.modelValue || {}
  const init = (key) => {
    const v = mv[key] || ''
    return v ? String(v).split(/[、,，;；]/).map(s => s.trim()).filter(Boolean) : []
  }
  picked.value = {
    tongue: init('tongue'), pulse: init('pulse'), local: init('local'),
    systemic: init('systemic'), symptoms: Array.isArray(mv.symptoms) ? [...mv.symptoms] : init('symptoms'),
  }
})

watch(() => props.specialty, () => {
  clearAll()
  loadCategories()
})

const fieldOf = (item) => {
  for (const sec of categories.value) {
    for (const g of sec.groups) {
      if (g.items.includes(item)) return g.field
    }
  }
  return 'symptoms'
}
const isOn = (item) => picked.value[fieldOf(item)]?.includes(item)
function toggle(item) {
  const f = fieldOf(item)
  const arr = picked.value[f]
  const i = arr.indexOf(item)
  i >= 0 ? arr.splice(i, 1) : arr.push(item)
  emitChange()
}
function removeLabel(label) {
  const f = fieldOf(label)
  const arr = picked.value[f]
  const i = arr.indexOf(label)
  if (i >= 0) arr.splice(i, 1)
  emitChange()
}
function clearAll() {
  picked.value = { tongue: [], pulse: [], local: [], systemic: [], symptoms: [] }
  detailText.value = ''
  emitChange()
}
function emitChange() {
  emit('update:modelValue', {
    symptoms: [...picked.value.symptoms],
    tongue: picked.value.tongue.join('、'),
    pulse: picked.value.pulse.join('、'),
    local: picked.value.local.join('、'),
    systemic: picked.value.systemic.join('、'),
    detail: detailText.value,
  })
}
watch(detailText, emitChange)

const allSelected = computed(() => Object.values(picked.value).flat())
const totalCount = computed(() => allSelected.value.length)
const countOf = (sec) => sec.groups.reduce((n, g) => n + g.items.filter((i) => isOn(i)).length, 0)
</script>

<style scoped>
.fdx-summary { background: #F2F7F4; border: 1px dashed #B4D8CE; border-radius: 8px; padding: 8px 12px; margin-bottom: 10px; font-size: 12.5px; color: #55665F; }
.fdx-summary .more { color: #8A94A0; margin-left: 4px; }
.sec-title { font-weight: 700; color: var(--xl-ink); font-family: "Songti SC", serif; }
.sec-count { margin-left: 10px; font-size: 12px; color: #8A94A0; }
.fdx-group { margin-bottom: 10px; }
.group-name { font-size: 13px; color: #55665F; margin: 6px 0; font-weight: 600; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip {
  padding: 3px 10px; border: 1px solid var(--xl-line); border-radius: 999px; font-size: 12.5px;
  cursor: pointer; user-select: none; color: #3A4641; background: #fff; transition: all .12s;
}
.chip:hover { border-color: var(--xl-teal); color: var(--xl-teal); }
.chip.on { background: var(--xl-deep); border-color: var(--xl-deep); color: #fff; }
.fdx-detail { margin-top: 10px; }
</style>
