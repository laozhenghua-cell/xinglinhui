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
            <el-form-item label="主诉(一句话说明最难受之处;写白话也行,系统自动识别)" required>
              <el-input v-model="complaint" type="textarea" :rows="2" maxlength="120" show-word-limit
                placeholder="如:这两天感冒了,怕冷、流清涕、有点咳嗽" />
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
            <el-row :gutter="12">
              <el-col :xs="24" :sm="8">
                <el-form-item label="何时加重(时间辨证)">
                  <el-select v-model="form.time" placeholder="无明显规律" class="w100" clearable>
                    <el-option v-for="t in timeOptions" :key="t.key" :label="t.label" :value="t.key" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item label="发病年份(五运六气)">
                  <el-input-number v-model="form.sick_year" :min="1900" :max="2100" class="w100" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item label="出生年份(运气体质,可选)">
                  <el-input-number v-model="form.birth_year" :min="1900" :max="2100" class="w100" />
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

          <!-- 白话结论 -->
          <div v-if="result.plain" class="plain-box" :class="{ 'plain-danger': result.plain.danger }">
            🌿 {{ result.plain.verdict }}
          </div>

          <!-- 病机提要(开阖枢 · 升降出入) -->
          <div v-if="result.mechanism" class="mech-box">
            <div class="mech-head">🍃 病机提要(六经开阖枢 · 脏腑升降出入)</div>
            <div v-if="result.mechanism.liujing" class="mech-line"><b>六经:</b>{{ result.mechanism.liujing }}</div>
            <div v-if="result.mechanism.zangfu" class="mech-line"><b>脏腑:</b>{{ result.mechanism.zangfu }}</div>
            <div class="mech-sum">{{ result.mechanism.summary }}</div>
          </div>

          <!-- 时间辨证 -->
          <div v-if="result.time && result.time.hint" class="time-box">
            ⏰ <b>时间辨证({{ result.time.label }}):</b>{{ result.time.hint }}
          </div>

          <!-- 脉证相参 · 真假鉴别 -->
          <div v-if="result.discern && result.discern.length" class="discern-box">
            <div class="discern-head">⚖️ 脉证相参 · 真假鉴别(舍证从脉)</div>
            <div v-for="(d, i) in result.discern" :key="i" class="discern-item">· {{ d }}</div>
          </div>

          <!-- 五运六气 -->
          <div v-if="result.wuyun" class="wuyun-box">
            <div class="wuyun-head">🌌 五运六气(发病年 · 出生年禀赋)</div>
            <div class="wuyun-year"><b>{{ result.wuyun.ganzhi }}</b>年({{ result.wuyun.year }}) · {{ result.wuyun.yun }}运{{ result.wuyun.over ? '太过' : '不及' }} · {{ result.wuyun.sitian }}司天 · {{ result.wuyun.zaiquan }}在泉</div>
            <div class="wuyun-hint">{{ result.wuyun.hint }}</div>
            <div v-if="result.wuyun.birth" class="wuyun-birth">👶 {{ result.wuyun.birth.hint }}</div>
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
                      <div v-if="(sk === 'liujing' || sk === 'zangfu') && sys.top[0].variant" class="sys-variant">
                        分型:{{ sys.top[0].variant.name }}——{{ sys.top[0].variant.treatment }}
                      </div>
                      <div v-if="sk === 'zangfu' && sys.top[0].missing && sys.top[0].missing.length" class="sys-miss">
                        📌 补录线索可坐实:{{ sys.top[0].missing.join('、') }}
                      </div>
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

            <!-- 症状反向引导 -->
            <div v-if="result.ask && result.ask.length" class="fu-strip">
              <div class="fu-head">🔍 针对您的症状,再问几个关键问题(点选后自动重辨,更精确)</div>
              <div v-for="q in result.ask" :key="q.id" class="fu-q">
                <div class="fu-qt">{{ q.q }}</div>
                <div class="fu-opts">
                  <el-tag v-for="o in q.options" :key="o.label" class="chip" type="info" @click="applyFollowup(o)">{{ o.label }}</el-tag>
                </div>
              </div>
            </div>

            <!-- 追问轨迹 -->
            <div v-if="trajectory.length" class="traj-strip">
              <div class="fu-head">🔎 追问轨迹(结论如何收敛)</div>
              <div v-for="(t, i) in trajectory" :key="i" class="traj-item">
                答「{{ t.answer }}」→ 脏腑:{{ t.zf }}<template v-if="t.lj">;六经:{{ t.lj }}</template>
              </div>
            </div>

            <!-- 鉴别追问 -->
            <div v-if="result.followup && result.followup.questions && result.followup.questions.length" class="fu-strip">
              <div class="fu-head">🔍 鉴别追问:{{ result.followup.top1 }} 与 {{ result.followup.top2 }} 接近,再答一个关键问题即可明确</div>
              <div v-for="q in result.followup.questions" :key="q.id" class="fu-q">
                <div class="fu-qt">{{ q.q }}</div>
                <div class="fu-opts">
                  <el-tag v-for="o in q.options" :key="o.label" class="chip" type="info" @click="applyFollowup(o)">{{ o.label }}</el-tag>
                </div>
              </div>
            </div>

            <!-- 开方建议(六体系主方 → 方剂库) -->
            <div v-if="result.formula_suggestions && result.formula_suggestions.length" class="prescribe-strip">
              <div class="care-head">📜 开方建议(据六体系主方)</div>
              <div class="rx-warn">⚠️ 教学参考:剂量为常用参考量,须经中医师面诊辨证后处方使用,切勿自行抓药服用</div>
              <!-- 拟方合成:主方+随症加减 → 完整处方单 -->
              <div v-if="result.prescription" class="presc-box">
                <div class="presc-head">
                  📋 拟方:<b>{{ result.prescription.name }}</b>
                  <span class="rx-src">{{ result.prescription.source }}</span>
                </div>
                <div class="presc-items">
                  <span v-for="(it, i) in result.prescription.items" :key="i" class="presc-item" :class="{ 'presc-add': it.note !== '原方' }">
                    {{ it.name }} {{ it.dosage }}<template v-if="it.note !== '原方'">({{ it.note }})</template>
                  </span>
                </div>
              </div>
              <div v-for="f in (showAllRx ? result.formula_suggestions : result.formula_suggestions.slice(0, 3))" :key="f.id" class="rx-card">
                <div class="rx-head">
                  <b class="rx-name" @click="router.push('/kb/yifang/' + f.id)">{{ f.name }}</b>
                  <el-tag size="small" type="warning">{{ f.category }}</el-tag>
                  <span class="rx-src">{{ f.source }}</span>
                </div>
                <div class="rx-line rx-contra" v-if="f.contraindications"><b>禁忌:</b>{{ f.contraindications }}</div>
                <div class="rx-comp">组成:<el-tag v-for="c in f.composition" :key="c.name" size="small" type="info" style="margin:0 3px 3px 0">{{ c.name }} {{ c.dosage || c.dose }}</el-tag></div>
                <div class="rx-ana" v-if="f.analysis && f.analysis.length">
                  <span v-for="a in f.analysis" :key="a.name" class="rx-herb">
                    <b>{{ a.name }}</b><i class="rx-role">{{ a.role }}</i>{{ a.note }}
                  </span>
                </div>
                <div class="rx-line"><b>功效:</b>{{ f.function }}</div>
                <div class="rx-line"><b>主治:</b>{{ f.indications }}</div>
                <div v-for="(en, ei) in rxMods(f.name)" :key="ei" class="rx-mod">
                  <template v-if="en.add && en.add.length">
                    ➕<el-tag v-for="a in en.add" :key="a.name" size="small" type="success" style="margin:0 3px 0 0">{{ a.name }} {{ a.dosage }}g</el-tag>
                    <span class="rx-mod-reason">{{ en.add.map(a => a.reason).join('、') }}</span>
                  </template>
                  <template v-if="en.remove && en.remove.length">➖ 去:{{ en.remove.join('、') }}</template>
                  <span class="rx-mod-src">{{ en.source }}</span>
                </div>
              </div>
              <el-button v-if="result.formula_suggestions.length > 3" link type="primary" size="small" @click="showAllRx = !showAllRx">
                {{ showAllRx ? '收起' : `展开其余 ${result.formula_suggestions.length - 3} 首` }}
              </el-button>
            </div>

            <!-- 治法门类(医方集解) -->
            <div v-if="result.menlei && result.menlei.length" class="menlei-strip">
              <div class="care-head">📚 治法门类(依《医方集解》)</div>
              <div v-for="m in result.menlei" :key="m.menlei" class="menlei-item">
                <b>{{ m.menlei }}</b>({{ m.zhifa }}):
                <el-tag v-for="f in m.formulas" :key="f.name" size="small" type="warning" class="menlei-chip" @click="router.push('/kb/yifang?q=' + encodeURIComponent(f.name))">{{ f.name }}</el-tag>
              </div>
            </div>

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
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { dxAnalyze, dxRecords, dxRecord } from '@/api/dx'
import { buildCategories } from '@/data/fourDiagnosis'

const router = useRouter()

const SYS_SHORT = { bagang: '八纲', liujing: '六经', weiqiyingxue: '卫气营血', zangfu: '脏腑', sanjiao: '三焦', jingluo: '经络' }
const BAGANG_PAIRS = [['表', '里'], ['寒', '热'], ['虚', '实'], ['阴', '阳']]
const courses = ['数日', '数周', '1-3个月', '3-6个月', '半年-1年', '1年以上', '多年']
const timeOptions = [
  { key: 'morning', label: '清晨加重' },
  { key: 'forenoon', label: '上午加重' },
  { key: 'afternoon', label: '午后加重' },
  { key: 'evening', label: '傍晚加重' },
  { key: 'night', label: '夜间加重' },
  { key: 'dawn', label: '后半夜/五更' },
]

const cats = buildCategories('')
const sectionOf = name => (cats.find(c => c.section === name) || { groups: [] }).groups
const wenGroups = sectionOf('问诊')
const lookGroups = [...sectionOf('望诊'), ...sectionOf('闻诊'), ...sectionOf('切诊')]

const step = ref(1)
const complaint = ref('')
const course = ref('')
const trigger = ref('')
const customSym = ref('')
const form = reactive({ symptoms: [], tongue: '', pulse: '', local: '', systemic: '', detail: '', time: '', sick_year: new Date().getFullYear(), birth_year: null })
const loading = ref(false)
const result = ref(null)
const records = ref([])
const showAllPairs = ref(false)
const showAllRx = ref(false)
const trajectory = ref([])

const complaintText = computed(() => complaint.value.trim() || '未填写')

function rxMods(name) {
  const m = (result.value?.modifications || []).find(x => x.formula === name)
  return m ? m.entries : []
}

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

async function run(opts = {}) {
  if (!complaint.value.trim() && !form.symptoms.length && !form.tongue && !form.pulse && !form.local && !form.systemic) {
    ElMessage.warning('请先填写主诉或点选症状')
    return null
  }
  loading.value = true
  try {
    const payload = { ...form, birth_year: form.birth_year || 0 }
    // 主诉+病程+诱因并入 detail(长文本,引擎只取整句做关键词匹配,不拆词干扰)
    const parts = [`主诉:${complaint.value.trim()}`]
    if (course.value) parts.push(`病程:${course.value}`)
    if (trigger.value.trim()) parts.push(`诱因:${trigger.value.trim()}`)
    payload.detail = [payload.detail, parts.join(';')].filter(Boolean).join(';')
    const res = await dxAnalyze(payload)
    result.value = res
    showAllPairs.value = false
    showAllRx.value = false
    if (!opts.keepPos) {
      trajectory.value = []
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
    await loadRecords()
    return res
  } catch (e) {
    ElMessage.error('辨证失败:' + (e?.response?.data?.detail || e.message))
    return null
  } finally {
    loading.value = false
  }
}
function topCap(res, key) {
  const t = res?.systems?.[key]?.top?.[0]
  return t && t.score > 0 ? { name: t.name, score: t.score } : null
}
function fmtDelta(prev, now) {
  if (!prev || !now) return prev ? `${prev.name}(${prev.score}分)→信息不足` : '—'
  if (prev.name === now.name) {
    const diff = now.score - prev.score
    const lock = diff >= 2 ? ',锁定' : ''
    return `${now.name}(${prev.score}→${now.score}分${lock})`
  }
  return `${prev.name}(${prev.score}分)→${now.name}(${now.score}分)`
}
function applyFollowup(opt) {
  const prevRes = result.value
  const prevZf = topCap(prevRes, 'zangfu')
  const prevLj = topCap(prevRes, 'liujing')
  for (const r of opt.remove || []) {
    const i = form.symptoms.indexOf(r)
    if (i >= 0) form.symptoms.splice(i, 1)
  }
  for (const a of opt.add || []) {
    if (!form.symptoms.includes(a)) form.symptoms.push(a)
  }
  run({ keepPos: true }).then((res) => {
    if (!res) return
    const z2 = topCap(res, 'zangfu')
    const l2 = topCap(res, 'liujing')
    trajectory.value.push({
      answer: opt.label,
      zf: fmtDelta(prevZf, z2),
      lj: fmtDelta(prevLj, l2),
    })
  })
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
    showAllRx.value = false
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
.plain-box { background: #FFFDF4; border: 1px solid #EAD9A8; border-left: 4px solid #C9A227; border-radius: 8px; padding: 10px 14px; font-size: 14px; color: #5A4E2E; line-height: 1.7; margin-bottom: 12px; font-weight: 500; }
.plain-danger { border-color: #E8A0A0; border-left-color: #C0392B; background: #FDF0F0; color: #7A2318; }
.mech-box { background: #F4F1FA; border: 1px solid #D9CCEE; border-left: 4px solid #8A63C9; border-radius: 8px; padding: 10px 14px; margin-bottom: 12px; }
.mech-head { font-weight: 700; color: #5B3E8E; font-size: 13px; margin-bottom: 6px; }
.mech-line { font-size: 12.5px; color: #4A3E6B; margin: 2px 0; }
.mech-line b { color: #5B3E8E; margin-right: 4px; }
.mech-sum { font-family: "Songti SC", serif; font-size: 13.5px; color: #3A2E5B; margin-top: 4px; line-height: 1.7; }
.time-box { background: #F2F7F4; border: 1px solid #C9E0D2; border-left: 4px solid #4E8A68; border-radius: 8px; padding: 8px 12px; font-size: 12.5px; color: #35684C; margin-bottom: 12px; line-height: 1.7; }
.time-box b { color: #2F5E48; }
.discern-box { background: #FDF0F0; border: 1px solid #E8B4A8; border-left: 4px solid #C0392B; border-radius: 8px; padding: 10px 14px; margin-bottom: 12px; }
.discern-head { font-weight: 700; color: #A03D2C; font-size: 13px; margin-bottom: 4px; }
.discern-item { font-size: 12.5px; color: #7A2318; margin: 3px 0; }
.wuyun-box { background: #EEF3FA; border: 1px solid #B9CCE8; border-left: 4px solid #3E6BA8; border-radius: 8px; padding: 10px 14px; margin-bottom: 12px; }
.wuyun-head { font-weight: 700; color: #2F5A96; font-size: 13px; margin-bottom: 4px; }
.wuyun-year { font-size: 12.5px; color: #2F5A96; margin: 2px 0; }
.wuyun-year b { font-family: "Songti SC", serif; font-size: 14px; }
.wuyun-hint { font-size: 12.5px; color: #3E5A85; line-height: 1.7; margin-top: 2px; }
.wuyun-birth { font-size: 12.5px; color: #6B4E8E; margin-top: 4px; border-top: 1px dashed #B9CCE8; padding-top: 4px; }
.rx-warn { color: #A03D2C; background: #FCEBE8; border: 1px solid #E8B4A8; border-radius: 6px; padding: 6px 10px; font-size: 12.5px; font-weight: 600; margin-bottom: 8px; }
.presc-box { background: #fff; border: 1px solid #E8C97A; border-radius: 8px; padding: 8px 12px; margin-bottom: 8px; }
.presc-head { font-size: 13px; color: #5A4E2E; }
.presc-head b { color: #8A5A12; font-size: 15px; font-family: "Songti SC", serif; }
.presc-items { margin-top: 6px; display: flex; flex-wrap: wrap; gap: 4px 10px; }
.presc-item { font-size: 13px; color: #3E5E4F; background: #F0F8F2; border-radius: 4px; padding: 2px 7px; }
.presc-add { background: #FFF6E8; color: #7A4A12; }
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
.sys-variant { color: #2F6DA0; background: #EAF3FB; border-left: 3px solid #6AA0D8; border-radius: 4px; padding: 3px 8px; margin-top: 4px; font-size: 12px; }
.rx-mod { font-size: 12px; color: #3E7C55; margin-top: 5px; background: #F0F8F2; border-radius: 4px; padding: 3px 8px; }
.rx-mod-reason { color: #6B5C42; margin-left: 4px; }
.rx-mod-src { color: #a99a7d; margin-left: 6px; font-size: 11px; }
.sys-miss { color: #7A6A2E; background: #FBF6DE; border-left: 3px solid #D8C25A; border-radius: 4px; padding: 3px 8px; margin-top: 4px; font-size: 12px; }
.fu-strip { margin-top: 12px; padding: 10px 12px; background: #F0F6FB; border: 1px dashed #9DBFE3; border-radius: 8px; }
.fu-head { font-weight: 700; color: #2F6DA0; font-size: 13px; margin-bottom: 6px; }
.fu-q { margin: 8px 0; }
.fu-qt { font-size: 13px; color: var(--xl-ink); margin-bottom: 5px; }
.fu-opts { display: flex; flex-wrap: wrap; gap: 6px; }
.fu-opts .chip { cursor: pointer; user-select: none; }
.traj-strip { margin-top: 12px; padding: 10px 12px; background: #F4F1FA; border: 1px dashed #B9A8DD; border-radius: 8px; }
.traj-item { font-size: 12.5px; color: #4A3E6B; margin: 4px 0; }
.care-strip { margin-top: 12px; padding: 10px 12px; background: #F4FBF7; border: 1px solid #C9E8D5; border-radius: 8px; }
.menlei-strip { margin-top: 12px; padding: 10px 12px; background: #FBF6EC; border: 1px solid #E8D9BC; border-radius: 8px; }
.menlei-item { font-size: 12.5px; color: #5A4E2E; margin: 4px 0; }
.menlei-item b { color: #8A5A12; margin-right: 4px; }
.menlei-chip { cursor: pointer; margin: 0 6px 2px 0; }
.care-head { font-weight: 700; color: #2F7A50; font-size: 13px; margin-bottom: 4px; }
.care-item { font-size: 12.5px; color: #3E5E4F; margin: 3px 0; }
.prescribe-strip { margin-top: 12px; padding: 10px 12px; background: #FDF7EC; border: 1px solid #EAD9B8; border-radius: 8px; }
.rx-card { background: #fff; border: 1px solid #EFE3C8; border-radius: 8px; padding: 8px 10px; margin-top: 8px; }
.rx-head { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.rx-name { color: #8A5A12; font-size: 14px; cursor: pointer; }
.rx-name:hover { text-decoration: underline; }
.rx-src { color: #a99a7d; font-size: 12px; }
.rx-comp { margin-top: 6px; font-size: 12.5px; color: #6B5C42; }
.rx-ana { margin-top: 6px; display: flex; flex-wrap: wrap; gap: 3px 10px; background: #FBF4E4; border-radius: 6px; padding: 6px 8px; }
.rx-herb { font-size: 12px; color: #6B5C42; }
.rx-herb b { color: #7A4A12; }
.rx-role { font-style: normal; color: #B07A2E; background: #F3E4C8; border-radius: 3px; padding: 0 4px; margin: 0 4px; font-size: 11px; }
.rx-line { font-size: 12.5px; color: #5A4E38; margin-top: 4px; }
.rx-line b { color: #8A5A12; }
.rx-contra { color: #B42318; font-weight: 700; }
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
