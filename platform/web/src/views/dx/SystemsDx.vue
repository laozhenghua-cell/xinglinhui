<template>
  <div class="dx-page">
    <div class="dx-body">
      <!-- 老中医问诊流 -->
      <el-card class="dx-input-card" shadow="never">
        <template #header><b>老中医问诊</b><span class="hint">主诉 → 十问 → 望闻切,循先贤诊法</span></template>

        <el-steps :active="step" align-center finish-status="success" style="margin-bottom:18px">
          <el-step title="主诉" description="最难受之处与病程" />
          <el-step title="十问" description="寒热汗头身二便饮食" />
          <el-step title="望闻切" description="舌象 · 面色 · 脉象" />
        </el-steps>

        <!-- 第 1 步:主诉 -->
        <div v-show="step === 1">
          <el-form label-position="top">
            <el-form-item label="主诉(一句话说明最难受之处,如:胃脘胀痛反复两月,进食后加重)" required>
              <el-input v-model="complaint" type="textarea" :rows="2" maxlength="120" show-word-limit
                placeholder="哪里不舒服?持续多久了?" />
            </el-form-item>
            <el-row :gutter="12">
              <el-col :xs="24" :sm="12">
                <el-form-item label="病程">
                  <el-select v-model="course" placeholder="发病多久" class="w100">
                    <el-option v-for="c in courses" :key="c" :label="c" :value="c" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12">
                <el-form-item label="诱因(可选)">
                  <el-input v-model="trigger" placeholder="如:情志不遂 / 受凉 / 饮食不节" maxlength="40" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item>
              <el-button type="primary" :disabled="!complaint.trim()" @click="step = 2">下一步:十问</el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 第 2 步:十问 -->
        <div v-show="step === 2">
          <div class="ask-tip">如无不适可跳过——点选所苦,可多选;也可自由输入补充</div>
          <div v-for="g in wenGroups" :key="g.name" class="ask-group">
            <div class="ask-group-name">{{ g.name }}</div>
            <div class="ask-chips">
              <el-tag v-for="it in g.items" :key="it" :type="picked(g.field).includes(it) ? 'success' : 'info'"
                class="chip" @click="toggleItem(g.field, it)">{{ it }}</el-tag>
            </div>
          </div>
          <el-input v-model="customSym" placeholder="自由输入其他症状,如:胁肋胀痛、善太息(顿号分隔)" style="margin:8px 0" @keyup.enter="addCustom" />
          <div style="margin-top:12px">
            <el-button @click="step = 1">上一步</el-button>
            <el-button type="primary" @click="step = 3">下一步:望闻切</el-button>
          </div>
        </div>

        <!-- 第 3 步:望闻切 -->
        <div v-show="step === 3">
          <div class="ask-tip">舌与脉为辨证之要,请尽量点选</div>
          <div v-for="g in lookGroups" :key="g.name" class="ask-group">
            <div class="ask-group-name">{{ g.name }}</div>
            <div class="ask-chips">
              <el-tag v-for="it in g.items" :key="it" :type="picked(g.field).includes(it) ? 'success' : 'info'"
                class="chip" @click="toggleItem(g.field, it)">{{ it }}</el-tag>
            </div>
          </div>
          <div style="margin-top:14px">
            <el-button @click="step = 2">上一步</el-button>
            <el-button type="primary" :loading="loading" @click="run">{{ loading ? '辨证中…' : '开始辨证' }}</el-button>
            <span class="hint">结论由中医典籍规则引擎生成(八纲/六经/卫气营血/脏腑/三焦/经络)</span>
          </div>
        </div>
      </el-card>

      <!-- 结果区 -->
      <div v-if="result" class="dx-result">
        <el-card shadow="never">
          <template #header>
            <b>辨证论治</b>
            <span style="float:right">
              <el-button text size="small" @click="printReport">🖨️ 打印/导出报告</el-button>
            </span>
          </template>

          <!-- 危候警示(最优先) -->
          <div v-if="result.danger && result.danger.length" class="danger-strip">
            <div v-for="d in result.danger" :key="d" class="danger-item">🚨 {{ d }}</div>
          </div>

          <!-- 主诉归纳 -->
          <div class="complaint-box">
            <b>主诉:</b>{{ complaintText }}
            <span v-if="course"> · 病程:{{ course }}</span>
            <span v-if="trigger"> · 诱因:{{ trigger }}</span>
          </div>

          <div class="sys-block">
            <h4>🧭 六体系对照(八纲 · 六经 · 卫气营血 · 脏腑 · 三焦 · 经络)</h4>
            <div class="sys-summary-strip">
              <span class="ss-label">结论链</span>
              <span v-for="(sys, sk) in result.systems" :key="sk" class="ss-chip" :class="{ 'ss-empty': sys.summary === '信息不足' }">
                <b>{{ SYS_SHORT[sk] || sys.name }}</b>{{ sys.summary }}
              </span>
              <span v-if="result.consistency && result.consistency.score !== null" class="ss-cons" :class="{ 'ss-bad': result.consistency.score < 0.6 }">
                {{ result.consistency.verdict }}({{ Math.round(result.consistency.score * 100) }}%)
              </span>
            </div>
            <el-row :gutter="10">
              <el-col v-for="(sys, sk) in result.systems" :key="sk" :xs="24" :sm="12" :md="8">
                <div class="sys-card" :class="{ 'sys-empty': sys.summary === '信息不足' }">
                  <div class="sys-head">{{ sys.name }}<span class="sys-conf" v-if="sys.summary !== '信息不足'">{{ Math.round((sys.confidence || 0) * 100) }}%</span></div>
                  <div class="sys-main">{{ sys.summary }}</div>
                  <template v-if="sys.summary !== '信息不足'">
                    <div v-if="sk === 'bagang' && bagangPairs(sys).length" class="sys-pairs">
                      <span v-for="(p, i) in bagangPairs(sys)" :key="i" class="bp-chip">{{ p }}</span>
                    </div>
                    <div class="sys-top1">
                      <b>{{ sys.top[0].name }}</b>({{ sys.top[0].score }} 分)
                      <div class="sys-hits"><el-tag v-for="h in sys.top[0].hits" :key="h" size="small" type="info" style="margin:0 2px 2px 0">{{ h }}</el-tag></div>
                      <div class="sys-exp">病机:{{ sys.top[0].explain }}</div>
                      <div v-if="sys.top[0].treatment" class="sys-treat">治则:{{ sys.top[0].treatment }}</div>
                    </div>
                    <el-collapse v-if="sys.top.length > 1" class="sys-more">
                      <el-collapse-item :title="`其余候选 ${sys.top.length - 1} 个`" :name="sk">
                        <div v-for="t in sys.top.slice(1)" :key="t.key" class="sys-item">
                          <b>{{ t.name }}</b>({{ t.score }} 分)
                          <div class="sys-hits"><el-tag v-for="h in t.hits" :key="h" size="small" type="info" style="margin:0 2px 2px 0">{{ h }}</el-tag></div>
                          <div class="sys-exp">{{ t.explain }}</div>
                          <div v-if="t.treatment" class="sys-treat">治则:{{ t.treatment }}</div>
                        </div>
                      </el-collapse-item>
                    </el-collapse>
                  </template>
                </div>
              </el-col>
            </el-row>

            <!-- 调护建议 -->
            <div v-if="result.care && result.care.length" class="care-strip">
              <div class="care-head">🍵 调护医嘱</div>
              <div v-for="(c, i) in result.care" :key="i" class="care-item">{{ i + 1 }}. {{ c }}</div>
            </div>

            <div v-if="result.dynamic" class="dyn-strip">
              <div v-if="result.dynamic.liujing_merge && result.dynamic.liujing_merge.length" class="dyn-item">
                ⚡ 六经合病/并病:<b>{{ result.dynamic.liujing_merge.map(m => m.label).join(';') }}</b>
                <span class="dyn-ev">{{ result.dynamic.liujing_merge[0].evidence.join(', ') }}</span>
                <span class="dyn-note">{{ result.dynamic.liujing_merge[0].note }}</span>
              </div>
              <div v-if="result.dynamic.weiqi_merge && result.dynamic.weiqi_merge.length" class="dyn-item">
                🔥 卫气营血同病:<b>{{ result.dynamic.weiqi_merge.map(m => m.label).join(';') }}</b>
                <span class="dyn-ev">{{ result.dynamic.weiqi_merge[0].evidence.join(', ') }}</span>
              </div>
              <div v-if="result.dynamic.sanjiao_trans && result.dynamic.sanjiao_trans.stage !== '信息不足'" class="dyn-item">
                🌊 三焦传变:<b>{{ result.dynamic.sanjiao_trans.stage }}</b>
                <span class="dyn-ev">{{ result.dynamic.sanjiao_trans.hint }}</span>
              </div>
            </div>
            <div v-if="result.consistency" class="consist-strip">
              <div class="consist-head">🔗 六体系交叉印证
                <el-tag v-if="result.consistency.score !== null && result.consistency.score !== undefined" size="small"
                  :type="result.consistency.score >= 0.99 ? 'success' : result.consistency.score >= 0.6 ? 'warning' : 'danger'">
                  {{ Math.round(result.consistency.score * 100) }}%
                </el-tag>
                <span class="consist-verdict">{{ result.consistency.verdict }}</span>
              </div>
              <div class="consist-pairs">
                <span v-for="(p, i) in (showAllPairs ? result.consistency.pairs : result.consistency.pairs.slice(0, 6))" :key="i" class="c-pair" :class="{ 'c-bad': !p.ok }">{{ p.text }}</span>
                <el-button v-if="result.consistency.pairs.length > 6" link type="primary" size="small" @click="showAllPairs = !showAllPairs">
                  {{ showAllPairs ? '收起' : `展开全部 ${result.consistency.pairs.length} 对` }}
                </el-button>
              </div>
            </div>
          </div>

          <div class="med-disclaimer" style="margin-top:12px">⚠️ 本结果由中医典籍知识库规则引擎生成,仅供学习参考,不构成医疗建议;急危重症请立即线下就医。</div>
        </el-card>
      </div>

      <!-- 记录区 -->
      <el-card shadow="never" class="dx-records">
        <template #header><b>本设备近期六体系辨证记录</b></template>
        <div v-if="!records.length" class="empty">暂无记录</div>
        <el-timeline v-else>
          <el-timeline-item v-for="r in records" :key="r.id" :timestamp="fmtTime(r.created_at)" placement="top">
            <a style="cursor:pointer;color:#409EFF" @click="loadRecord(r)">{{ recordSummary(r) }}</a>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { dxAnalyze, dxRecords, dxRecord } from '@/api/dx'
import { buildCategories } from '@/data/fourDiagnosis'

const SYS_SHORT = { bagang: '八纲', liujing: '六经', weiqiyingxue: '卫气营血', zangfu: '脏腑', sanjiao: '三焦', jingluo: '经络' }
const BAGANG_PAIRS = [['表', '里'], ['寒', '热'], ['虚', '实'], ['阴', '阳']]
const courses = ['数日', '数周', '1-3个月', '3-6个月', '半年-1年', '1年以上', '多年']

const cats = buildCategories('')
const sectionOf = name => (cats.find(c => c.section === name) || { groups: [] }).groups
const wenGroups = sectionOf('问诊')
const lookGroups = [...sectionOf('望诊'), ...sectionOf('闻诊'), ...sectionOf('切诊')]

const step = ref(1)
const complaint = ref('')
const course = ref('')
const trigger = ref('')
const customSym = ref('')
const form = reactive({ symptoms: [], tongue: '', pulse: '', local: '', systemic: '', detail: '' })
const loading = ref(false)
const result = ref(null)
const records = ref([])
const showAllPairs = ref(false)

const complaintText = computed(() => complaint.value.trim() || '未填写')

function picked(field) {
  return field === 'symptoms' ? form.symptoms : String(form[field] || '').split('、').filter(Boolean)
}
function toggleItem(field, it) {
  if (field === 'symptoms') {
    const i = form.symptoms.indexOf(it)
    i >= 0 ? form.symptoms.splice(i, 1) : form.symptoms.push(it)
  } else {
    const arr = String(form[field] || '').split('、').filter(Boolean)
    const i = arr.indexOf(it)
    i >= 0 ? arr.splice(i, 1) : arr.push(it)
    form[field] = arr.join('、')
  }
}
function addCustom() {
  const parts = customSym.value.split(/[、,;]/).map(s => s.trim()).filter(Boolean)
  for (const p of parts) {
    if (p && !form.symptoms.includes(p)) form.symptoms.push(p)
  }
  customSym.value = ''
}
function bagangPairs(sys) {
  const byKey = {}
  for (const t of sys.top || []) byKey[t.key] = t
  return BAGANG_PAIRS.filter(([a, b]) => byKey[a] || byKey[b]).map(([a, b]) => {
    const sa = byKey[a]?.score ?? 0
    const sb = byKey[b]?.score ?? 0
    if (sa === 0 && sb === 0) return null
    const win = sa >= sb ? byKey[a].name : byKey[b].name
    return `${a}/${b}→${win}`
  }).filter(Boolean)
}
function printReport() { window.print() }

onMounted(async () => {
  await loadRecords()
})

async function run() {
  if (!complaint.value.trim() && !form.symptoms.length && !form.tongue && !form.pulse && !form.local && !form.systemic) {
    ElMessage.warning('请先填写主诉或点选症状')
    return
  }
  loading.value = true
  try {
    const payload = { ...form }
    // 主诉+病程+诱因并入 detail(长文本,引擎只取整句做关键词匹配,不拆词干扰)
    const parts = [`主诉:${complaint.value.trim()}`]
    if (course.value) parts.push(`病程:${course.value}`)
    if (trigger.value.trim()) parts.push(`诱因:${trigger.value.trim()}`)
    payload.detail = [payload.detail, parts.join(';')].filter(Boolean).join(';')
    const res = await dxAnalyze(payload)
    result.value = res
    showAllPairs.value = false
    window.scrollTo({ top: 0, behavior: 'smooth' })
    await loadRecords()
  } catch (e) {
    ElMessage.error('辨证失败:' + (e?.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}
async function loadRecords() {
  try {
    const res = await dxRecords({ limit: 20 })
    records.value = res.items || []
  } catch { records.value = [] }
}
function loadRecord(r) {
  dxRecord(r.id).then(res => {
    result.value = res.result
    showAllPairs.value = false
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }).catch(() => {})
}
function recordSummary(r) {
  const rr = r.result || {}
  const s = rr.systems?.zangfu?.summary
  if (s && s !== '信息不足') return `六体系:${s}`
  const lj = rr.systems?.liujing?.summary
  if (lj && lj !== '信息不足') return `六体系:${lj}`
  const names = (rr.syndromes || []).map(x => x.name).slice(0, 2)
  return names.join('、') || '辨证记录'
}
function fmtTime(t) {
  return t ? String(t).replace('T', ' ').slice(0, 16) : ''
}
</script>

<style scoped>
.dx-page { min-height: 100vh; background: #f5f7fa; }
.dx-body { max-width: 1200px; margin: 0 auto; padding: 20px 16px; }
.dx-input-card { margin-bottom: 16px; }
.hint { color: #999; font-size: 12px; margin-left: 10px; }
.w100 { width: 100%; }
.ask-tip { color: #9a8f6a; font-size: 12.5px; background: #FBF7EC; border-left: 3px solid var(--xl-gold); padding: 4px 10px; margin-bottom: 10px; border-radius: 4px; }
.ask-group { margin-bottom: 12px; }
.ask-group-name { font-weight: 700; color: var(--xl-ink); font-size: 13px; margin-bottom: 6px; }
.ask-chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { cursor: pointer; user-select: none; }
.empty { color: #999; padding: 12px 0; }
.dx-records { margin-top: 16px; }
.danger-strip { background: #FDEEEE; border: 1px solid #E8A0A0; border-radius: 8px; padding: 8px 12px; margin-bottom: 12px; }
.danger-item { color: #B42318; font-size: 13px; font-weight: 700; margin: 3px 0; }
.complaint-box { background: #F2F7F4; border: 1px solid #D5E8DC; border-radius: 8px; padding: 8px 12px; font-size: 13px; color: #35684C; margin-bottom: 12px; }
.complaint-box b { color: var(--xl-deep); }
.med-disclaimer { background: #FFF7F0; border: 1px solid #F3D5BE; color: #9C5B2D; border-radius: 8px; padding: 6px 12px; font-size: 12.5px; }
.sys-block { background: #F7FAF9; border: 1px solid #DCEBE4; border-radius: 10px; padding: 12px 14px; margin-top: 6px; }
.sys-block h4 { margin: 0 0 8px; color: var(--xl-deep); }
.sys-summary-strip { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin-bottom: 10px; padding: 8px 10px; background: #fff; border: 1px solid var(--xl-line); border-radius: 8px; }
.ss-label { font-weight: 700; color: var(--xl-deep); font-size: 13px; margin-right: 2px; }
.ss-chip { font-size: 12.5px; background: #F2F7F4; border: 1px solid #D5E8DC; color: #35684C; border-radius: 5px; padding: 2px 7px; }
.ss-chip b { margin-right: 4px; }
.ss-empty { background: #F5F5F5; border-color: #E5E5E5; color: #9a9a9a; }
.ss-cons { font-size: 12.5px; font-weight: 700; color: #3E7C55; background: #E2F2E9; border: 1px solid #BFE0CC; border-radius: 5px; padding: 2px 8px; margin-left: auto; }
.ss-bad { color: #A05A2C; background: #F9E8D8; border-color: #E8C97A; }
.sys-card { background: #fff; border: 1px solid var(--xl-line); border-radius: 8px; padding: 10px 12px; height: 100%; margin-bottom: 10px; }
.sys-head { font-weight: 700; color: var(--xl-ink); display: flex; justify-content: space-between; }
.sys-conf { color: var(--xl-teal); font-size: 12px; }
.sys-main { font-family: "Songti SC", serif; font-size: 15px; color: var(--xl-cinnabar); margin: 4px 0 6px; }
.sys-empty .sys-main { color: #9a9a9a; font-size: 13px; }
.sys-top1 { font-size: 12.5px; margin: 6px 0 2px; border-top: 1px dashed #eee; padding-top: 4px; }
.sys-pairs { display: flex; flex-wrap: wrap; gap: 4px; margin: 2px 0 6px; }
.bp-chip { font-size: 12px; color: #4C6B58; background: #EDF5F0; border-radius: 4px; padding: 1px 6px; }
.sys-more { border-top: none; margin-top: 4px; }
.sys-more :deep(.el-collapse-item__header) { font-size: 12px; color: #7a8a80; height: 30px; line-height: 30px; background: transparent; border-bottom: none; }
.sys-more :deep(.el-collapse-item__wrap) { border-bottom: none; }
.sys-item { font-size: 12.5px; margin: 6px 0; border-top: 1px dashed #eee; padding-top: 4px; }
.sys-hits { margin: 2px 0; }
.sys-exp { color: #8A94A0; font-size: 11.5px; }
.sys-treat { color: #7A4A12; background: #FFF6E8; border-left: 3px solid #E8A84C; border-radius: 4px; padding: 3px 8px; margin-top: 4px; font-size: 12px; }
.care-strip { margin-top: 12px; padding: 10px 12px; background: #F4FBF7; border: 1px solid #C9E8D5; border-radius: 8px; }
.care-head { font-weight: 700; color: #2F7A50; font-size: 13px; margin-bottom: 4px; }
.care-item { font-size: 12.5px; color: #3E5E4F; margin: 3px 0; }
.dyn-strip { margin-top: 10px; padding: 8px 12px; background: #FFF8E6; border: 1px dashed #E8C97A; border-radius: 8px; }
.dyn-item { font-size: 13px; color: var(--xl-ink); margin: 3px 0; }
.dyn-item b { color: #9A6B00; margin: 0 4px; }
.dyn-ev { color: #8a8370; margin-left: 6px; font-size: 12px; }
.dyn-note { display: block; color: #a89c80; font-size: 12px; margin-top: 2px; }
.consist-strip { margin-top: 10px; padding: 8px 12px; background: #F2F8F4; border: 1px solid #BFE0CC; border-radius: 8px; }
.consist-head { font-size: 13px; font-weight: 700; color: var(--xl-deep); display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.consist-verdict { color: #3E7C55; font-weight: 600; }
.consist-pairs { margin-top: 6px; display: flex; flex-wrap: wrap; gap: 4px 10px; }
.c-pair { font-size: 12px; color: #4C6B58; background: #E2F2E9; border-radius: 4px; padding: 2px 6px; }
.c-bad { color: #A05A2C; background: #F9E8D8; }
@media print {
  .dx-input-card, .dx-records, .med-disclaimer { display: none !important; }
  .dx-body { max-width: 100%; padding: 0; margin: 0; }
  .dx-page { background: #fff; }
  .el-collapse-item__content { display: block !important; }
  body { background: #fff; }
}
</style>
