<template>
  <div class="dx-page">
    <div class="dx-body">
      <!-- 输入区 -->
      <el-card class="dx-input-card" shadow="never">
        <template #header><b>四诊录入</b><span class="hint">选择专科与症状,匹配病种/证型/方剂(疮疡 · 痔漏 · 儿科 · 丹药专科库)</span></template>

        <el-form label-position="top">
          <el-form-item label="专科范围">
            <el-select v-model="form.module" placeholder="不限专科(跨专科辨证)" class="module-select">
              <el-option label="不限专科(跨专科)" value="" />
              <el-option label="外科疮疡" value="surgery" />
              <el-option label="肛肠痔漏" value="anorectal" />
              <el-option label="儿科" value="pediatrics" />
              <el-option label="丹药研究" value="alchemy" />
            </el-select>
          </el-form-item>

          <el-form-item label="四诊(按分类点选)">
            <FourDiagnosisPicker v-model="form" :specialty="form.module" />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :loading="loading" @click="run">
              {{ loading ? '辨证中…' : '开始病种辨证' }}
            </el-button>
            <span class="hint">结果由专科原版典籍规则匹配(病种分期治法 · 原著辨证 · 方剂)</span>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 结果区 -->
      <div v-if="result" class="dx-result">
        <el-card shadow="never">
          <template #header>
            <b>病种辨证结果</b>
            <el-tag size="small" type="success" style="margin-left:10px">专科知识库匹配 · 3532 条内容</el-tag>
            <span style="float:right">
              <el-button text size="small" @click="printReport">🖨️ 打印/导出报告</el-button>
              <el-button text size="small" @click="router.push('/kb/search?q=' + encodeURIComponent(mainName))">总库检索「{{ mainName }}」</el-button>
            </span>
          </template>

          <div class="med-disclaimer">⚠️ 本结果由中医典籍知识库规则引擎生成,仅供学习参考,不构成医疗建议;急危重症请立即线下就医。</div>

          <el-row :gutter="16">
            <el-col :xs="24" :sm="12">
              <h4>证型匹配 <el-tag size="small" type="purple" v-for="s in result.syndromes" :key="s.id" style="margin-left:4px">{{ MODULE_NAMES[s.module] }}</el-tag></h4>
              <div v-if="!result.syndromes.length" class="empty">未匹配到证型,请补充四诊信息</div>
              <div v-for="s in result.syndromes" :key="s.id" class="match-item">
                <b>{{ s.name }}</b>
                <span class="score" v-if="s.score !== undefined">匹配分 {{ s.score }}</span>
                <span class="score" v-else-if="s.confidence !== undefined">置信度 {{ Math.round(s.confidence * 100) }}%</span>
                <div class="hits">
                  <el-tag v-for="h in s.hits" :key="h" size="small" type="info" style="margin-right:4px">{{ h }}</el-tag>
                </div>
                <div v-if="s.original && Object.keys(s.original).some(k => s.original[k])" class="orig">
                  <div v-for="(v, k) in s.original" :key="k" v-show="v">
                    <b>{{ k }}:</b><span>{{ v }}</span>
                  </div>
                </div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12">
              <h4>病种匹配</h4>
              <div v-if="!result.diseases.length" class="empty">未匹配到病种</div>
              <div v-for="d in result.diseases" :key="d.id" class="match-item">
                <b>{{ d.name }}</b><el-tag size="small" style="margin-left:8px">{{ MODULE_NAMES[d.module] }}</el-tag><span class="score">匹配分 {{ d.score }}</span>
                <div class="hits"><el-tag v-for="h in d.hits" :key="h" size="small" type="info" style="margin-right:4px">{{ h }}</el-tag></div>
                <div v-if="d.original && (d.original['出处'] || d.original['特点'])" class="orig">
                  <span v-if="d.original['出处']" class="orig-src">出处:{{ d.original['出处'] }}</span>
                  <span v-if="d.original['特点']"> · 特点:{{ d.original['特点'] }}</span>
                  <span v-if="d.original['鉴别']"> · 鉴别:{{ d.original['鉴别'] }}</span>
                </div>
                <div v-if="d.stages && d.stages.length" class="stages">
                  <div class="stage-title">分期治法(原书规则)</div>
                  <el-tabs v-if="d.stages.length > 1" type="border-card" size="small">
                    <el-tab-pane v-for="st in d.stages" :key="st.stage" :label="st.stage">
                      <div class="stage-line" v-if="st['内治']"><b>内治:</b>{{ st['内治'] }}</div>
                      <div class="stage-line" v-if="st['外治']"><b>外治:</b>{{ st['外治'] }}</div>
                      <div class="stage-line" v-if="st['护理']"><b>护理:</b>{{ st['护理'] }}</div>
                      <div class="stage-line" v-if="st['注意']"><b>注意:</b>{{ st['注意'] }}</div>
                    </el-tab-pane>
                  </el-tabs>
                  <div v-else v-for="st in d.stages" :key="st.stage" class="stage-one">
                    <div class="stage-line" v-if="st['内治']"><b>内治:</b>{{ st['内治'] }}</div>
                    <div class="stage-line" v-if="st['外治']"><b>外治:</b>{{ st['外治'] }}</div>
                    <div class="stage-line" v-if="st['护理']"><b>护理:</b>{{ st['护理'] }}</div>
                    <div class="stage-line" v-if="st['注意']"><b>注意:</b>{{ st['注意'] }}</div>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>

          <div v-if="result.peds" class="peds-block">
            <h4>📜 原著辨证(《程氏家传儿科秘要》)</h4>
            <div v-if="result.peds.methods && result.peds.methods.length" class="peds-line">
              六字治法:<el-tag v-for="m in result.peds.methods" :key="m" size="small" type="primary" style="margin:0 4px">{{ m }}</el-tag>
            </div>
            <div v-if="result.peds.dangers && result.peds.dangers.length" class="peds-line danger">
              ⚠️ 危候警示:<el-tag v-for="d in result.peds.dangers" :key="d.label" size="small" type="danger" style="margin:0 4px">{{ d.label }}[{{ d.level }}]</el-tag>
            </div>
            <div v-if="result.peds.combos && result.peds.combos.length" class="peds-line danger">
              <span v-for="c in result.peds.combos" :key="c">⚠️ {{ c }}</span>
            </div>
            <div v-if="result.peds.jiajian && result.peds.jiajian.length" class="peds-line">
              兼症加减:
              <div v-for="(j, i) in result.peds.jiajian" :key="i" class="jj">
                【{{ j.syndrome }}】{{ j.cond }} → {{ j.add }}<span v-if="j.note">({{ j.note }})</span>
              </div>
            </div>
          </div>

          <h4 style="margin-top:18px">方剂推荐(按专科)</h4>
          <div v-if="!Object.keys(result.formulas || {}).length" class="empty">暂无匹配方剂</div>
          <div v-for="(list, mod) in result.formulas" :key="mod" style="margin-bottom:12px">
            <div class="mod-label">{{ MODULE_NAMES[mod] || mod }}</div>
            <el-row :gutter="10">
              <el-col v-for="f in list" :key="f.id" :xs="24" :sm="8">
                <el-card shadow="hover" class="formula-card" @click="router.push('/kb/formulas/' + f.id)">
                  <b>{{ f.name }}</b><span class="src">{{ f.source }}</span>
                  <div class="fx">{{ (f.function || '').slice(0, 24) }}</div>
                  <div class="comp">{{ (f.composition || []).slice(0, 4).map(c => c.name).join('、') }}</div>
                </el-card>
              </el-col>
            </el-row>
          </div>

          <h4 style="margin-top:18px">关联内容</h4>
          <el-row :gutter="10">
            <el-col :xs="24" :sm="8">
              <div class="mod-label">医案({{ (result.related.cases || []).length }})</div>
              <div v-for="c in result.related.cases" :key="c.id" class="rel-item" @click="router.push('/kb/cases/' + c.id)">{{ c.title }}</div>
            </el-col>
            <el-col :xs="24" :sm="8">
              <div class="mod-label">要诀({{ (result.related.tips || []).length }})</div>
              <div v-for="t in result.related.tips" :key="t.id" class="rel-item" @click="router.push('/kb/tips/' + t.id)">{{ t.category }}:{{ (t.content || '').slice(0, 30) }}…</div>
            </el-col>
            <el-col :xs="24" :sm="8">
              <div class="mod-label">引药({{ (result.related.dulong || []).length }})</div>
              <div v-for="d in result.related.dulong" :key="d.id" class="rel-item" @click="router.push('/kb/dulong/' + d.id)">{{ d.disease }} → {{ d.guide }}</div>
            </el-col>
          </el-row>

        </el-card>
      </div>

      <!-- 记录区 -->
      <el-card shadow="never" class="dx-records">
        <template #header><b>本设备近期辨证记录</b></template>
        <div v-if="!records.length" class="empty">暂无记录</div>
        <el-timeline v-else>
          <el-timeline-item v-for="r in records" :key="r.id" :timestamp="fmtTime(r.created_at)" placement="top">
            <a style="cursor:pointer;color:#409EFF" @click="loadRecord(r)">{{ MODULE_NAMES[r.module] || '跨专科' }} · {{ recordSummary(r) }}</a>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { dxAnalyze, dxRecords, dxRecord, dxQuick } from '@/api/dx'
import FourDiagnosisPicker from '@/components/FourDiagnosisPicker.vue'

const router = useRouter()
const route = useRoute()

const MODULE_NAMES = { anorectal: '肛肠痔漏', surgery: '外科疮疡', pediatrics: '儿科', alchemy: '丹药研究' }
const commonSymptoms = ['发热', '咳嗽', '红肿热痛', '疮顶脓头', '便血', '肛门坠胀', '腹泻', '便秘', '呕吐', '纳差', '口渴', '舌红', '脉数', '脉浮', '瘙痒', '疼痛拒按', '神疲乏力', '夜啼']

const form = reactive({ module: '', symptoms: [], tongue: '', pulse: '', local: '', systemic: '', detail: '' })
const customSym = ref('')
const loading = ref(false)
const result = ref(null)
const records = ref([])

function printReport() { window.print() }

const mainName = computed(() => {
  const s = result.value?.syndromes?.[0]?.name
  const d = result.value?.diseases?.[0]?.name
  return s || d || ''
})

onMounted(async () => {
  if (route.query.module) form.module = String(route.query.module)
  await loadRecords()
})

function toggleSym(s) {
  const i = form.symptoms.indexOf(s)
  if (i >= 0) form.symptoms.splice(i, 1)
  else form.symptoms.push(s)
}
function addSym(s) {
  if (s && !form.symptoms.includes(s)) form.symptoms.push(s)
  customSym.value = ''
}
async function suggestSym(q, cb) {
  if (!q) return cb([])
  try {
    const res = await dxQuick(q)
    cb((res || []).map(s => ({ value: s })))
  } catch { cb([]) }
}
async function run() {
  if (!form.symptoms.length && !form.tongue && !form.pulse && !form.local && !form.systemic && !form.detail) {
    ElMessage.warning('请先录入症状或四诊信息')
    return
  }
  loading.value = true
  try {
    const res = await dxAnalyze({ ...form })
    result.value = res
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
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }).catch(() => {})
}
function recordSummary(r) {
  const rr = r.result || {}
  const names = (rr.syndromes || []).map(s => s.name).slice(0, 2)
  return names.join('、') || '辨证记录'
}
function fmtTime(t) {
  return t ? String(t).replace('T', ' ').slice(0, 16) : ''
}
</script>

<style scoped>
.dx-page { min-height: 100vh; background: #f5f7fa; }
.dx-topbar { display: flex; align-items: center; justify-content: space-between; padding: 12px 24px; background: #fff; border-bottom: 1px solid #e8e8e8; }
.dx-title { font-weight: 700; font-size: 17px; color: #1f2d3d; }
.dx-body { max-width: 1200px; margin: 0 auto; padding: 20px 16px; }
.dx-input-card { margin-bottom: 16px; }
.hint { color: #999; font-size: 12px; margin-left: 10px; }
.match-item { padding: 8px 10px; border-bottom: 1px dashed #eee; }
.match-item .score { float: right; color: #f56c6c; font-size: 12px; }
.hits { margin-top: 4px; }
.empty { color: #999; padding: 12px 0; }
.mod-label { font-weight: 600; color: #606266; margin: 6px 0; }
.formula-card { cursor: pointer; margin-bottom: 10px; }
.formula-card .src { color: #999; font-size: 12px; margin-left: 6px; }
.formula-card .fx { color: #67c23a; font-size: 12px; margin-top: 4px; }
.formula-card .comp { color: #909399; font-size: 12px; margin-top: 4px; }
.rel-item { cursor: pointer; padding: 5px 2px; border-bottom: 1px dashed #eee; font-size: 13px; color: #409eff; }
.dx-records { margin-top: 16px; }
.orig { margin-top: 5px; font-size: 12px; color: #6B7A72; background: #F7F4EE; border-left: 3px solid var(--xl-gold); padding: 5px 8px; border-radius: 4px; line-height: 1.7; }
.orig b { color: var(--xl-ink); }
.orig-src { color: var(--xl-gold); }
.peds-block { background: #FBF7EC; border: 1px solid #E8DDBE; border-radius: 10px; padding: 10px 14px; margin-top: 14px; }
.peds-block h4 { margin: 0 0 6px; color: var(--xl-gold); }
.peds-line { margin: 4px 0; font-size: 13px; }
.peds-line.danger { color: var(--xl-cinnabar); }
.stages { margin-top: 6px; background: #F7FBF9; border: 1px solid #DCEBE4; border-radius: 8px; padding: 8px 10px; }
.stage-title { font-size: 12px; color: var(--xl-teal); font-weight: 600; margin-bottom: 4px; }
.stage-line { font-size: 12.5px; color: #4A5A52; margin: 3px 0; }
.stage-line b { color: var(--xl-ink); }
.jj { font-size: 12.5px; color: #6B5C42; margin: 2px 0; padding-left: 10px; }
.module-select { width: 100%; max-width: 260px; }
.med-disclaimer { background: #FFF7F0; border: 1px solid #F3D5BE; color: #9C5B2D; border-radius: 8px; padding: 6px 12px; font-size: 12.5px; margin-bottom: 12px; }
@media print {
  .dx-input-card, .dx-records, .med-disclaimer { display: none !important; }
  .dx-body { max-width: 100%; padding: 0; margin: 0; }
  .dx-page { background: #fff; }
  .el-collapse-item__content { display: block !important; }
  body { background: #fff; }
}
</style>
