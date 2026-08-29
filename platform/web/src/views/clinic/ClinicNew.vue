<template>
  <div class="xl-page cn-page">
    <div class="xl-page-title">
      <h2>新建就诊</h2>
      <el-button @click="router.push('/clinic')">返回列表</el-button>
    </div>

    <!-- 第一步:患者与专科 -->
    <div class="xl-card">
      <h3>① 患者信息与专科</h3>
      <el-form label-position="top" inline>
        <el-form-item label="患者姓名" required><el-input v-model="p.patient_name" style="width:170px" /></el-form-item>
        <el-form-item label="性别">
          <el-select v-model="p.gender" style="width:100px">
            <el-option label="男" value="男" /><el-option label="女" value="女" /><el-option label="—" value="" />
          </el-select>
        </el-form-item>
        <el-form-item label="年龄"><el-input-number v-model="p.age" :min="0" :max="150" style="width:110px" /></el-form-item>
        <el-form-item label="主诉"><el-input v-model="p.chief_complaint" placeholder="如:颈后生疮三日" style="width:280px" /></el-form-item>
      </el-form>
      <div class="spec-pick">
        <div v-for="s in SPECIALTIES" :key="s.key" class="spec-opt" :class="{ on: p.specialty === s.key }" @click="p.specialty = s.key">
          <span class="so-ico">{{ s.icon }}</span><b>{{ s.name }}</b><i>{{ s.desc }}</i>
        </div>
      </div>
    </div>

    <!-- 第二步:四诊 -->
    <div class="xl-card">
      <h3>② 四诊录入</h3>
      <FourDiagnosisPicker :model-value="fourModel" :specialty="p.specialty" @update:model-value="onFour" />
      <div style="margin-top:12px">
        <el-upload :show-file-list="false" :before-upload="onPhoto" accept="image/*" :disabled="photoLoading" style="display:inline-block;margin-right:12px">
          <el-button :loading="photoLoading" plain>{{ photoLoading ? '辨病中…' : '📷 拍照辨病' }}</el-button>
        </el-upload>
        <el-switch v-model="p.four.use_ai" active-text="AI 报告" style="margin-right:16px" />
        <el-button type="primary" :loading="dxLoading" @click="runDx">🤖 AI 智能辨证</el-button>
      </div>
    </div>

    <!-- 辨证结果 -->
    <div v-if="dx" class="xl-card">
      <h3>③ 辨证结果</h3>
      <div v-if="visionResult" class="vision-note">
        <b>📷 拍照辨病:</b>
        <span v-for="(v, k) in visionSummary" :key="k">{{ k }}: {{ v }}; </span>
      </div>
      <el-row :gutter="14">
        <el-col :span="12">
          <div class="sec-title">证型</div>
          <div v-for="s in dx.syndromes" :key="s.id" class="dx-line"><b>{{ s.name }}</b><span class="score">匹配 {{ s.score }}</span>
            <div class="hits"><el-tag v-for="h in s.hits" :key="h" size="small" type="info" style="margin-right:4px">{{ h }}</el-tag></div>
          </div>
          <div class="sec-title" style="margin-top:10px">病种</div>
          <div v-for="d in dx.diseases" :key="d.id" class="dx-line"><b>{{ d.name }}</b><el-tag size="small" style="margin-left:6px">{{ MOD[d.module] }}</el-tag></div>
          <template v-if="dx.diseases && dx.diseases.length && dx.diseases[0].stages && dx.diseases[0].stages.length">
            <div class="sec-title" style="margin-top:10px">分期治法(原书规则)</div>
            <el-collapse>
              <el-collapse-item v-for="st in dx.diseases[0].stages" :key="st.stage" :title="st.stage + '期'">
                <div class="stage-line" v-if="st['内治']"><b>内治:</b>{{ st['内治'] }}</div>
                <div class="stage-line" v-if="st['外治']"><b>外治:</b>{{ st['外治'] }}</div>
                <div class="stage-line" v-if="st['护理']"><b>护理:</b>{{ st['护理'] }}</div>
                <div class="stage-line" v-if="st['注意']"><b>注意:</b>{{ st['注意'] }}</div>
              </el-collapse-item>
            </el-collapse>
          </template>
        </el-col>
        <el-col :span="12">
          <div class="sec-title">推荐方剂(点击加入处方)</div>
          <div v-for="(list, mod) in dx.formulas" :key="mod" style="margin-bottom:8px">
            <div class="mod-lab">{{ MOD[mod] }}</div>
            <el-tag v-for="f in list" :key="f.id" size="small" type="success" style="cursor:pointer;margin:0 6px 4px 0" @click="addFormula(f)">
              {{ f.name }}
            </el-tag>
          </div>
          <el-collapse v-if="dx.ai">
            <el-collapse-item title="🤖 AI 综合报告">
              <div class="ai-block"><b>证型:</b>{{ dx.ai.syndrome_analysis }}</div>
              <div class="ai-block"><b>病种:</b>{{ dx.ai.disease_suggestion }}</div>
              <div class="ai-block"><b>方剂:</b>{{ dx.ai.formula_suggestion }}</div>
              <div class="ai-block"><b>注意:</b>{{ dx.ai.precautions }}</div>
            </el-collapse-item>
          </el-collapse>
        </el-col>
      </el-row>
    </div>

    <!-- 第四步:处方 -->
    <div class="xl-card">
      <h3>④ 处方与医嘱</h3>
      <el-form label-position="top">
        <el-form-item label="处方方剂">
          <div v-if="!rx.formulas.length" class="xl-empty">点击上方"推荐方剂"加入,或手填</div>
          <el-tag v-for="(f, i) in rx.formulas" :key="i" closable type="success" style="margin:0 8px 8px 0" @close="rx.formulas.splice(i, 1)">{{ f }}</el-tag>
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label="加减化裁"><el-input v-model="rx.modification" type="textarea" :rows="2" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="外治法"><el-input v-model="rx.external" type="textarea" :rows="2" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="医嘱/调护"><el-input v-model="rx.advice" type="textarea" :rows="2" /></el-form-item>
        <el-button type="primary" size="large" :loading="saving" @click="save">💾 保存就诊</el-button>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { dxAnalyze } from '@/api/dx'
import { createVisit } from '@/api/clinic'
import FourDiagnosisPicker from '@/components/FourDiagnosisPicker.vue'

const router = useRouter()
const MOD = { surgery: '外科疮疡', anorectal: '肛肠痔漏', pediatrics: '儿科', alchemy: '丹药研究' }
const SPECIALTIES = [
  { key: 'surgery', icon: '🩹', name: '外科疮疡', desc: '疔痈疽等' },
  { key: 'anorectal', icon: '🩺', name: '肛肠痔漏', desc: '痔瘘裂脱' },
  { key: 'pediatrics', icon: '👶', name: '儿科', desc: '八症六字' },
  { key: 'alchemy', icon: '⚗️', name: '丹药研究', desc: '外用丹药' },
]
const commonSymptoms = ['发热', '咳嗽', '红肿热痛', '疮顶脓头', '便血', '肛门坠胀', '腹泻', '便秘', '呕吐', '纳差', '口渴', '夜啼', '瘙痒', '疼痛拒按', '神疲乏力', '脓成未溃']

const p = reactive({
  patient_name: '', gender: '', age: null, specialty: 'surgery', chief_complaint: '',
  four: { symptoms: [], tongue: '', pulse: '', local: '', systemic: '', detail: '', use_ai: true },
})
const customSym = ref('')
const fourModel = computed(() => ({
  symptoms: p.four.symptoms, tongue: p.four.tongue, pulse: p.four.pulse,
  local: p.four.local, systemic: p.four.systemic, detail: p.four.detail,
}))
function onFour(v) {
  p.four.symptoms = v.symptoms || []
  p.four.tongue = v.tongue || ''
  p.four.pulse = v.pulse || ''
  p.four.local = v.local || ''
  p.four.systemic = v.systemic || ''
  p.four.detail = v.detail || ''
}
const dx = ref(null)
const dxLoading = ref(false)
const saving = ref(false)
const photoLoading = ref(false)
const visionResult = ref(null)

async function onPhoto(file) {
  photoLoading.value = true
  try {
    const fd = new FormData()
    fd.append('image', file)
    fd.append('module', p.specialty === 'anorectal' ? 'anorectal' : 'surgery')
    fd.append('symptoms', [...p.four.symptoms, p.four.tongue, p.four.pulse].filter(Boolean).join(';'))
    const res = await fetch('/api/v1/dx/vision', { method: 'POST', body: fd })
    if (!res.ok) throw new Error((await res.json()).detail || '失败')
    const d = await res.json()
    visionResult.value = d.result || {}
    ElMessage.success('拍照辨病完成')
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
    if (typeof r[k] === 'string' && r[k]) out[k] = r[k].slice(0, 120)
  }
  return out
})
const rx = reactive({ formulas: [], modification: '', external: '', advice: '' })

function toggleSym(s) {
  const i = p.four.symptoms.indexOf(s)
  i >= 0 ? p.four.symptoms.splice(i, 1) : p.four.symptoms.push(s)
}
function addSym() {
  if (customSym.value && !p.four.symptoms.includes(customSym.value)) p.four.symptoms.push(customSym.value)
  customSym.value = ''
}
async function runDx() {
  if (!p.patient_name) { ElMessage.warning('请先填写患者姓名'); return }
  dxLoading.value = true
  try {
    dx.value = await dxAnalyze({ module: p.specialty, ...p.four })
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '辨证失败')
  } finally { dxLoading.value = false }
}
function addFormula(f) {
  if (!rx.formulas.includes(f.name)) rx.formulas.push(f.name)
}
async function save() {
  if (!p.patient_name) { ElMessage.warning('请填写患者姓名'); return }
  saving.value = true
  try {
    const v = await createVisit({
      patient_name: p.patient_name, gender: p.gender, age: p.age, specialty: p.specialty,
      chief_complaint: p.chief_complaint, four_diagnosis: p.four, dx_result: dx.value || {},
      prescription: { ...rx }, followup: {},
    })
    ElMessage.success('就诊已保存')
    router.push('/clinic/' + v.id)
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '保存失败')
  } finally { saving.value = false }
}
</script>

<style scoped>
.cn-page .xl-card { margin-bottom: 14px; }
.spec-pick { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 6px; }
.spec-opt { border: 2px solid var(--xl-line); border-radius: 12px; padding: 12px; cursor: pointer; text-align: center; transition: all .15s; }
.spec-opt.on { border-color: var(--xl-teal); background: var(--xl-mint); }
.spec-opt b { display: block; color: var(--xl-ink); margin: 4px 0 2px; }
.spec-opt i { font-style: normal; font-size: 12px; color: #8A94A0; }
.so-ico { font-size: 22px; }
.sec-title { font-weight: 600; color: var(--xl-ink); margin-bottom: 6px; }
.dx-line { padding: 6px 0; border-bottom: 1px dashed var(--xl-line); }
.score { float: right; color: var(--xl-cinnabar); font-size: 12px; }
.hits { margin-top: 3px; }
.mod-lab { font-size: 12px; color: #8A94A0; margin-bottom: 4px; }
.ai-block { margin: 6px 0; font-size: 13px; }
.hint { color: #8A94A0; font-size: 12px; margin-left: 10px; }
.stage-line { font-size: 12.5px; color: #4A5A52; margin: 3px 0; }
.stage-line b { color: var(--xl-ink); }
.vision-note { background: #EFF5FB; border: 1px solid #CFDFEF; border-radius: 8px; padding: 8px 12px; font-size: 12.5px; color: #2F6DA0; margin-bottom: 10px; }
</style>
