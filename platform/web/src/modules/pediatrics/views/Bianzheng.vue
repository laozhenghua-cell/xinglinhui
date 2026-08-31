<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { findingGroups, diagnose, type DiagnosisResult } from '../engine/diagnosis'
import { syndromes } from '../data/syndromes'

const router = useRouter()

const step = ref(0)
const selected = ref<Record<string, boolean>>({})
const result = ref<DiagnosisResult | null>(null)

function toggle(key: string, v: boolean) {
  if (v) selected.value[key] = true
  else delete selected.value[key]
}

const counts = computed(() =>
  findingGroups.map((s) => s.groups.reduce((n, g) => n + g.findings.filter((f) => selected.value[f.key]).length, 0))
)

function next() {
  if (step.value < 4) {
    step.value++
    window.scrollTo({ top: 0 })
  }
}
function back() {
  if (step.value > 0) step.value--
  else window.scrollTo({ top: 0 })
}

function run() {
  if (counts.value.every((c) => c === 0)) {
    ElMessage.warning('请先在四诊各步采集证据')
    return
  }
  result.value = diagnose(selected.value)
  step.value = 5
  window.scrollTo({ top: 0 })
}

function reset() {
  selected.value = {}
  result.value = null
  step.value = 0
}

function printReport() {
  window.print()
}

const syndromeMap = computed(() => {
  const m: Record<string, (typeof syndromes)[number]> = {}
  for (const s of syndromes) m[s.id] = s
  return m
})

const dangerLevel = computed(() => {
  if (!result.value) return 'none'
  if (result.value.dangers.some((d) => d.level === '极危') || result.value.combos.length) return 'fatal'
  if (result.value.dangers.length) return 'danger'
  return 'none'
})

/** 医嘱（据言症论治生成） */
const advice = computed(() => {
  if (!result.value) return []
  const s = result.value.selected
  const list: string[] = []
  if (s['g_shenre'] || s['q_dake']) list.push('乳母戒口食素，忌肥腻荤腥（不戒则服药不效）。')
  if (s['q_duanru']) list.push('患儿因失乳致病者，必恢复乳食方能医治。')
  if (s['q_rumuyoutai'] || s['g_fashu']) list.push('乳母有胎，儿食孕乳为患——速嘱断乳。')
  if (s['g_yezhongchenqing']) list.push('乳痰吼症：戒咸味，乳母忌食腻生痰之物，必要时断乳。')
  list.push('石类药（石膏等）须煅过出尽火气，配甘草以制其毒。')
  list.push('羚羊、犀角、石膏等先煎；薄荷、木香、肉桂等后下。')
  list.push('丸散分二次服，务使药量服足；苦味药能避则避。')
  list.push('方以十二味为率，最多十四味。')
  if (s['q_tuxiebuZhi']) list.push('吐泻不止者以止泻为先——利小便、平肝木、温肠三法并用。')
  return list
})
</script>

<template>
  <div class="page">
    <div class="h-title" style="font-size: 26px">辨证论治</div>
    <el-button type="primary" size="small" style="margin-top:10px" @click="router.push('/dx?module=pediatrics')">🧭 病种辨证(跨专科)</el-button>
    <p style="color: var(--ink-soft); font-size: 13.5px; margin-top: 6px">
      依程氏诊法四步采集证据，按八症六字立法处方。每一步均附原著依据。
    </p>

    <el-steps :active="step" finish-status="success" align-center class="steps no-print">
      <el-step title="望手纹" :description="`已选 ${counts[0] || 0} 项`" />
      <el-step title="切脉" :description="`已选 ${counts[1] || 0} 项`" />
      <el-step title="看外症" :description="`已选 ${counts[2] || 0} 项`" />
      <el-step title="问诊" :description="`已选 ${counts[3] || 0} 项`" />
      <el-step title="辨证结果" />
    </el-steps>

    <!-- 四诊采集 -->
    <div v-if="step <= 4" class="card no-print">
      <template v-for="(st, si) in findingGroups" :key="st.step">
        <div v-if="step === si">
          <div class="h-sub">{{ st.name }}</div>
          <div v-for="grp in st.groups" :key="grp.name" class="grp">
            <div class="grp-name">{{ grp.name }}</div>
            <el-checkbox-group :model-value="grp.findings.filter((f) => selected[f.key]).map((f) => f.key)" @update:model-value="(vals: unknown[]) => grp.findings.forEach((f) => toggle(f.key, (vals as string[]).includes(f.key)))">
              <el-checkbox v-for="f in grp.findings" :key="f.key" :value="f.key" class="chk">
                <span>{{ f.label }}</span>
                <span v-if="f.hint" class="hint">{{ f.hint }}</span>
              </el-checkbox>
            </el-checkbox-group>
          </div>
        </div>
      </template>
      <div class="step-actions">
        <el-button v-if="step > 0" @click="back">上一步</el-button>
        <el-button v-if="step < 4" type="primary" @click="next">下一步：{{ ['切脉', '看外症', '问诊', '开始辨证'][step] }}</el-button>
        <el-button v-if="step === 4" type="primary" @click="run">辨证论治</el-button>
      </div>
    </div>

    <!-- 结果 -->
    <div v-if="result && step === 5">
      <!-- 危候拦截 -->
      <div v-if="dangerLevel !== 'none'" class="warn-banner">
        <b v-if="dangerLevel === 'fatal'">⚠ 危候警示（原著列为死候/危候）</b>
        <b v-else>⚠ 危重征象提示</b>
        <ul style="margin: 8px 0 0; padding-left: 20px">
          <li v-for="d in result.dangers" :key="d.label">{{ d.label }}</li>
          <li v-for="c in result.combos" :key="c">{{ c }}</li>
        </ul>
        <p style="margin: 8px 0 0">
          按原著"识症趋避"：死症难治必先告明，令其多请高明；须尽自己所学而救之，
          存一片济世心。请立即告知家属，寻求中西医协同救治，切勿延误。
        </p>
      </div>

      <!-- 辨证评分 -->
      <div class="h-sec">一、辨证（八症匹配度）</div>
      <div class="card">
        <div v-for="s in result.scores" :key="s.id" class="score-row">
          <div class="score-name" :class="{ top: result.top.some((t) => t.id === s.id) }">{{ s.name }}</div>
          <el-progress :percentage="s.pct" :stroke-width="12" :color="result.top.some((t) => t.id === s.id) ? '#b03a2e' : '#c9b98f'" class="score-bar" />
          <div class="score-num">{{ s.score }} 分</div>
        </div>
        <p class="vern" style="margin-top: 10px">
          按八症总论：两症、三症同见者宜兼同参治——如疳症又病惊风，当以惊风、疳症两则一同参看。
        </p>
      </div>

      <template v-if="result.top.length">
        <div class="h-sec">二、论治</div>
        <div v-for="t in result.top" :key="t.id" class="card">
          <div class="syn-head">
            <span class="tag-syndrome">{{ syndromeMap[t.id].name }}</span>
            <span v-for="m in syndromeMap[t.id].methods" :key="m" class="tag-method">{{ m }}</span>
            <span class="match">匹配度 {{ t.pct }}%</span>
          </div>
          <p class="sy-summary">{{ syndromeMap[t.id].summary }}</p>
          <div class="h-sub">治法</div>
          <div class="original">{{ syndromeMap[t.id].zhifa.original }}</div>
          <div class="h-sub">方药（{{ syndromeMap[t.id].fangyao.name }}）</div>
          <el-table :data="syndromeMap[t.id].fangyao.herbs" size="small" border>
            <el-table-column prop="name" label="药味" width="110" />
            <el-table-column prop="dose" label="剂量" width="90" />
            <el-table-column prop="note" label="原著注" />
          </el-table>
          <p class="vern" style="margin-top: 8px">{{ syndromeMap[t.id].fangyao.usage }}</p>
          <div v-if="syndromeMap[t.id].wansan.length" class="h-sub">丸散</div>
          <p v-for="w in syndromeMap[t.id].wansan" :key="w.cond + w.powder" class="vern">
            {{ w.cond }}：{{ w.powder }}
          </p>
          <div class="h-sub">依兼症加味（原著加减法）</div>
          <el-table v-if="result.jiajianHits.filter((j) => j.syndrome === syndromeMap[t.id].name).length" :data="result.jiajianHits.filter((j) => j.syndrome === syndromeMap[t.id].name)" size="small" border>
            <el-table-column prop="cond" label="兼证" width="180" />
            <el-table-column prop="add" label="加味" />
          </el-table>
          <p v-else class="vern">未见命中加味条目的兼症；可点击"八症各论"查阅全部加减法。</p>
        </div>

        <div class="h-sec">三、医嘱</div>
        <div class="card">
          <ul class="advice">
            <li v-for="a in advice" :key="a">{{ a }}</li>
          </ul>
        </div>

        <div class="h-sec">四、辨证思路（学习卡片）</div>
        <div class="card">
          <p class="vern">为什么辨为{{ result.top.map((t) => syndromeMap[t.id].name).join('、') }}？——原著依据：</p>
          <div v-for="t in result.top" :key="'why' + t.id" class="why">
            <b>{{ syndromeMap[t.id].name }}</b>
            <div class="original" style="font-size: 13px">{{ syndromeMap[t.id].waihou.original }}</div>
            <div class="original" style="font-size: 13px">手纹：{{ syndromeMap[t.id].shouwen.original }}</div>
            <div class="original" style="font-size: 13px">脉法：{{ syndromeMap[t.id].maifa.original }}</div>
          </div>
        </div>
      </template>

      <template v-else>
        <div class="card">
          <p class="vern">
            未形成明确八症匹配。请返回补充四诊证据；或按原著"诊手纹法"：纹非沉非浮、非青非紫、
            脉亦和平、外症无病者，可先以肚泻肚痛、夜热、痢症问之，若皆非，则以脾虚受湿断之，
            投平淡补脾之药，有益无损。
          </p>
        </div>
      </template>

      <div class="no-print" style="margin: 18px 0 40px; display: flex; gap: 12px; flex-wrap: wrap">
        <el-button type="primary" @click="printReport">打印辨证论治报告</el-button>
        <el-button @click="reset">重新辨证</el-button>
        <el-button @click="step = 0">返回修改四诊</el-button>
      </div>

      <!-- 打印头部 -->
      <div class="print-head">
        <h2>程氏家传儿科秘要 · 辨证论治报告</h2>
        <p>辨证依据：清·程康圃《儿科秘要》八症六字 · 仅供参考，须执业医师复核</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.steps {
  margin: 14px 0 18px;
}
.grp {
  margin-bottom: 14px;
  padding: 10px 12px;
  background: var(--paper-light);
  border-radius: 6px;
  border: 1px solid var(--line);
}
.grp-name {
  font-family: var(--font-kai);
  font-weight: 700;
  color: var(--jade);
  margin-bottom: 8px;
  font-size: 14.5px;
}
.chk {
  margin-right: 18px;
  height: auto;
  line-height: 2.1;
}
.chk .hint {
  color: #a0845a;
  font-size: 11.5px;
  margin-left: 4px;
}
.step-actions {
  margin-top: 14px;
  display: flex;
  gap: 10px;
}
.score-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}
.score-name {
  width: 84px;
  font-family: var(--font-kai);
  font-size: 15px;
  color: var(--ink-soft);
}
.score-name.top {
  color: var(--vermilion);
  font-weight: 700;
  font-size: 16px;
}
.score-bar {
  flex: 1;
}
.score-num {
  width: 56px;
  text-align: right;
  color: var(--ink-soft);
  font-size: 12.5px;
}
.syn-head {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}
.match {
  margin-left: auto;
  font-size: 13px;
  color: var(--vermilion);
  font-weight: 600;
}
.sy-summary {
  color: var(--ink-soft);
  font-size: 13.5px;
  line-height: 1.8;
}
.advice li {
  margin: 6px 0;
  line-height: 1.8;
  font-size: 13.5px;
}
.why {
  margin: 10px 0;
}
.print-head {
  display: none;
}
@media print {
  .print-head {
    display: block;
    text-align: center;
    margin-bottom: 12px;
  }
  .print-head h2 {
    font-family: var(--font-kai);
    margin: 0;
  }
  .print-head p {
    margin: 4px 0 0;
    font-size: 12px;
  }
}
</style>
