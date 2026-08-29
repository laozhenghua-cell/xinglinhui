<template>
  <div class="dx-page">
    <div class="dx-body">
      <!-- 输入区 -->
      <el-card class="dx-input-card" shadow="never">
        <template #header><b>四诊录入</b><span class="hint">症状可多选,也可自由输入;AI 综合报告默认开启</span></template>

        <el-form label-position="top">
          <el-form-item label="专科范围">
            <el-select v-model="form.module" placeholder="不限专科(跨专科辨证)" style="width: 260px">
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
            <el-upload :show-file-list="false" :before-upload="onPhoto" accept="image/*" :disabled="photoLoading">
              <el-button :loading="photoLoading" plain>{{ photoLoading ? '辨病中…' : '📷 拍照辨病(上传患处照片)' }}</el-button>
            </el-upload>
            <el-switch v-model="form.use_ai" active-text="AI 综合辨证报告" style="margin-left:16px" />
            <el-button type="primary" :loading="loading" style="margin-left:24px" @click="run">
              {{ loading ? '辨证中…' : '开始辨证' }}
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 结果区 -->
      <div v-if="result" class="dx-result">
        <el-card shadow="never">
          <template #header>
            <b>辨证结果</b>
            <el-tag size="small" type="success" style="margin-left:10px">知识总库匹配 · 3532 条内容</el-tag>
            <el-button text size="small" style="float:right" @click="router.push('/kb/search?q=' + encodeURIComponent(mainName))">总库检索「{{ mainName }}」</el-button>
          </template>

          <div v-if="visionResult" class="vision-block">
            <h4>📷 拍照辨病(Qwen-VL)</h4>
            <div v-for="(v, k) in visionSummary" :key="k" class="stage-line"><b>{{ k }}:</b>{{ v }}</div>
          </div>

          <el-row :gutter="16">
            <el-col :span="12">
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
            <el-col :span="12">
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
              <el-col v-for="f in list" :key="f.id" :span="8">
                <el-card shadow="hover" class="formula-card" @click="router.push('/kb/formulas/' + f.id)">
                  <b>{{ f.name }}</b><span class="src">{{ f.source }}</span>
                  <div class="fx">{{ (f.function || '').slice(0, 24) }}</div>
                  <div class="comp">{{ (f.composition || []).slice(0, 4).map(c => c.name).join('、') }}</div>
                </el-card>
              </el-col>
            </el-row>
          </div>

          <div v-if="result.systems" class="sys-block">
            <h4>🧭 辨证体系对照(八纲 · 六经 · 卫气营血 · 脏腑 · 三焦 · 经络)</h4>
            <el-row :gutter="10">
              <el-col v-for="(sys, sk) in result.systems" :key="sk" :span="8">
                <div class="sys-card">
                  <div class="sys-head">{{ sys.name }}<span class="sys-conf">{{ Math.round((sys.confidence || 0) * 100) }}%</span></div>
                  <div class="sys-main">{{ sys.summary }}</div>
                  <div v-for="t in sys.top" :key="t.key" class="sys-item">
                    <b>{{ t.name }}</b>({{ t.score }} 分)
                    <div class="sys-hits"><el-tag v-for="h in t.hits" :key="h" size="small" type="info" style="margin:0 2px 2px 0">{{ h }}</el-tag></div>
                    <div class="sys-exp">{{ t.explain }}</div>
                  </div>
                </div>
              </el-col>
            </el-row>
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
                <span v-for="(p, i) in result.consistency.pairs" :key="i" class="c-pair" :class="{ 'c-bad': p.endsWith('✗') }">{{ p }}</span>
              </div>
            </div>
          </div>

          <h4 style="margin-top:18px">关联内容</h4>
          <el-row :gutter="10">
            <el-col :span="8">
              <div class="mod-label">医案({{ (result.related.cases || []).length }})</div>
              <div v-for="c in result.related.cases" :key="c.id" class="rel-item" @click="router.push('/kb/cases/' + c.id)">{{ c.title }}</div>
            </el-col>
            <el-col :span="8">
              <div class="mod-label">要诀({{ (result.related.tips || []).length }})</div>
              <div v-for="t in result.related.tips" :key="t.id" class="rel-item" @click="router.push('/kb/tips/' + t.id)">{{ t.category }}:{{ (t.content || '').slice(0, 30) }}…</div>
            </el-col>
            <el-col :span="8">
              <div class="mod-label">引药({{ (result.related.dulong || []).length }})</div>
              <div v-for="d in result.related.dulong" :key="d.id" class="rel-item" @click="router.push('/kb/dulong/' + d.id)">{{ d.disease }} → {{ d.guide }}</div>
            </el-col>
          </el-row>

          <el-collapse v-if="result.ai" style="margin-top:18px">
            <el-collapse-item title="🤖 AI 综合辨证报告(DeepSeek)" name="ai">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="证型分析">{{ result.ai.syndrome_analysis }}</el-descriptions-item>
                <el-descriptions-item label="病种建议">{{ result.ai.disease_suggestion }}</el-descriptions-item>
                <el-descriptions-item label="方剂建议">{{ result.ai.formula_suggestion }}</el-descriptions-item>
                <el-descriptions-item label="注意事项">{{ result.ai.precautions }}</el-descriptions-item>
                <el-descriptions-item label="置信度">{{ result.ai.confidence }}</el-descriptions-item>
              </el-descriptions>
            </el-collapse-item>
          </el-collapse>
          <div v-else class="empty" style="margin-top:12px">AI 报告暂不可用,已按知识库规则匹配(可稍后重试)</div>
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

const form = reactive({ module: '', symptoms: [], tongue: '', pulse: '', local: '', systemic: '', detail: '', use_ai: true })
const customSym = ref('')
const photoLoading = ref(false)
const visionResult = ref(null)

async function onPhoto(file) {
  photoLoading.value = true
  try {
    const fd = new FormData()
    fd.append('image', file)
    fd.append('module', form.module || 'surgery')
    fd.append('symptoms', [...form.symptoms, form.tongue, form.pulse].filter(Boolean).join(';'))
    const res = await fetch('/api/v1/dx/vision', { method: 'POST', body: fd })
    if (!res.ok) throw new Error((await res.json()).detail || '失败')
    const d = await res.json()
    visionResult.value = d.result || {}
  } catch (e) {
    ElMessage.error(e.message || '拍照辨病失败')
  } finally {
    photoLoading.value = false
  }
  return false
}
const visionSummary = computed(() => {
  const r = visionResult.value || {}
  const out = {}
  for (const k of Object.keys(r)) {
    if (typeof r[k] === 'string' && r[k]) out[k] = r[k].slice(0, 200)
  }
  return out
})
const loading = ref(false)
const result = ref(null)
const records = ref([])

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
  dxRecord(r.id).then(res => { result.value = res.result }).catch(() => {})
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
.vision-block { background: #EFF5FB; border: 1px solid #CFDFEF; border-radius: 10px; padding: 10px 14px; margin-bottom: 12px; }
.vision-block h4 { margin: 0 0 6px; color: #2F6DA0; }
.jj { font-size: 12.5px; color: #6B5C42; margin: 2px 0; padding-left: 10px; }
.sys-block { background: #F7FAF9; border: 1px solid #DCEBE4; border-radius: 10px; padding: 12px 14px; margin-top: 16px; }
.sys-block h4 { margin: 0 0 8px; color: var(--xl-deep); }
.sys-card { background: #fff; border: 1px solid var(--xl-line); border-radius: 8px; padding: 10px 12px; height: 100%; }
.sys-head { font-weight: 700; color: var(--xl-ink); display: flex; justify-content: space-between; }
.sys-conf { color: var(--xl-teal); font-size: 12px; }
.sys-main { font-family: "Songti SC", serif; font-size: 15px; color: var(--xl-cinnabar); margin: 4px 0 6px; }
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
.sys-item { font-size: 12.5px; margin: 6px 0; border-top: 1px dashed #eee; padding-top: 4px; }
.sys-hits { margin: 2px 0; }
.sys-exp { color: #8A94A0; font-size: 11.5px; }
</style>
