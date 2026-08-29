<template>
  <div>
    <h1 class="page-title">专业模式 · 辨证选方</h1>
    <div class="page-sub">问诊流（部位→疮形→脓液→全身症状→舌脉）+ 安全筛查 · 结果仅为学术研究参考</div>

    <!-- 知情确认 -->
    <div v-if="!gated" class="card" style="padding:20px">
      <h3 style="margin-top:0">⚕️ 专业研究模式确认</h3>
      <div style="font-size:0.9rem;line-height:1.9;color:#5c5240">
        <p>本模式面向<strong>中医外科医师、中医药研究者</strong>，用于学术研究与教学参考。</p>
        <p style="color:#b35309">丹药（轻粉、红升丹、白降丹、三仙丹等）为汞、砷剧毒化合物，属《医疗用毒性药品管理办法》毒性药品。
        本系统不提供任何处方；任何临床应用必须由执业医师在现行法规与伦理框架内独立决策，并承担全部责任。</p>
      </div>
      <el-checkbox v-model="agree">我确认自己是中医外科专业医师或研究者，使用本模块仅作学术研究参考</el-checkbox>
      <div style="margin-top:14px">
        <el-button type="danger" :disabled="!agree" @click="gated = true">开始问诊 →</el-button>
      </div>
    </div>

    <!-- 问诊流 -->
    <Questionnaire v-else-if="!result" :steps="steps" :required-ids="['special', 'poison']" @complete="onComplete" />

    <!-- 结果 -->
    <div v-else>
      <!-- 红旗 -->
      <div v-if="result.blocked" class="card" style="border:2px solid #c0392b;background:#fdf0ef">
        <h3 style="color:#c0392b;margin-top:0">🛑 红旗警示：不推荐任何方剂</h3>
        <div v-for="f in result.redFlags" :key="f.id" style="font-size:0.92rem;margin:8px 0;line-height:1.8">
          <strong>· {{ f.message }}</strong>
        </div>
        <p style="font-size:0.85rem;color:#8a2f2f">汞、砷中毒可致死。立即就医是唯一正确选择。</p>
      </div>

      <!-- 黄旗 -->
      <div v-if="result.cautious && !result.blocked" class="card" style="border:1.5px solid #d98e2b;background:#fdf6e8">
        <h3 style="color:#b35309;margin-top:0">🟡 黄旗警示</h3>
        <div v-for="f in result.yellowFlags" :key="f.id" style="font-size:0.9rem;margin:6px 0">{{ f.message }}</div>
        <p style="font-size:0.85rem;color:#8a5a1c;margin-bottom:0">以下候选方剂仅为文献研究参考；须由执业医师评估后决定。</p>
      </div>

      <!-- 证型 -->
      <template v-if="!result.blocked">
        <div class="card">
          <h3 style="margin-top:0">🧭 辨证结论</h3>
          <div v-if="result.syndromes.length">
            <div v-for="s in result.syndromes" :key="s.id" style="margin-bottom:10px">
              <strong style="color:var(--dan-red)">{{ s.name }}</strong>
              <span class="tag" style="margin-left:6px">命中 {{ s.hits.length }} 项</span>
              <div style="font-size:0.85rem;color:#6b5c42;margin-top:4px">{{ s.explain }}</div>
            </div>
          </div>
          <div v-else style="color:#9a8a6c;font-size:0.9rem">
            依据所选症状未匹配到典型证型。建议补充舌脉信息，或参照下方病证方向逐条研究。
          </div>
          <div v-if="result.syndromes.length" style="font-size:0.8rem;color:#8a7a60;margin-top:8px">
            证型已参与下方选方过滤：原书标注为阴证方者（如中九丸）在阳证热毒下自动排除并注明理由；分期（未溃/成脓/已溃）不符者同理。
          </div>
        </div>

        <!-- 候选方剂 -->
        <div class="card" v-if="result.recommendations.length">
          <h3 style="margin-top:0">🧪 候选方剂方向（按匹配度）</h3>
          <div v-for="r in result.recommendations" :key="r.id" style="border-top:1px dashed #e0d5bd;padding:12px 0">
            <strong>{{ r.title }}</strong>
            <span class="tag" style="margin-left:6px">命中 {{ r.hits.length }} 项</span>
            <div class="pill-row" style="margin:8px 0 4px">
              <span v-if="!r.kept.length" style="font-size:0.8rem;color:#9a8a6c">（此方向下的方剂均已按证/分期排除）</span>
              <template v-for="item in r.kept" :key="item.f.id">
                <div style="width:100%;margin:2px 0">
                  <a :href="'/kb/formulas?q=' + encodeURIComponent(item.f.name)" target="_blank" style="margin-left:8px;color:#1f6e8c;font-size:0.78rem">总库 ↗</a>
                  <span class="tag red" style="cursor:pointer" @click="$router.push('/alchemy/formula/' + item.f.id)">
                    {{ item.f.name }}（{{ item.f.category }}·{{ item.f.method }}）
                    <template v-for="c in item.chips" :key="c"><span class="tag" style="margin-left:4px;background:#f3ead2;color:#8a6a1c">{{ c }}</span></template>
                  </span>
                  <div v-if="item.guides && item.guides.length" style="font-size:0.78rem;color:#6b5c42;margin:4px 0 8px;background:#faf6ea;border-left:3px solid var(--dan-gold);padding:6px 10px">
                    <strong>📜 原书引药（与所选病证匹配{{ item.guides.length > 6 ? '，节选' : '' }}）：</strong>
                    <div v-for="(g, gi) in item.guides.slice(0, 6)" :key="gi">{{ g.d }} —— <span style="color:#8a6a1c">{{ g.g }}</span></div>
                    <span style="color:#9a8a6c">全部 245 条引药见 <a @click="$router.push('/alchemy/dulong')">毒龙丹引药全书 →</a></span>
                  </div>
                </div>
              </template>
            </div>
            <div v-for="ex in r.excluded" :key="ex.f.id" style="font-size:0.78rem;color:#b35309;margin:2px 0">
              ⊘ 已按{{ ex.kind }}排除：<strong>{{ ex.f.name }}</strong> —— {{ ex.reason }}
            </div>
            <div style="font-size:0.78rem;color:#8a7a60">依据：{{ r.basis }}</div>
          </div>
        </div>
        <div class="card" v-else style="color:#9a8a6c">所选症状下未匹配到候选方向（可能因红旗排除）。</div>
      </template>

      <div class="safety-banner" style="margin-top:14px">
        <strong>⚠️ 结论性质：</strong>本报告由规则引擎生成，规则依据原书主治原文与中医外科辨证常规，仅为学术研究参考，<strong>不构成诊断、处方或医疗建议</strong>。临床使用须遵循《医疗用毒性药品管理办法》与现行药典。
      </div>
      <div style="text-align:center;margin-top:16px">
        <el-button @click="reset">重新问诊</el-button>
        <el-button type="danger" plain @click="$router.push('/alchemy/safety')">查看安全与法规篇</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import Questionnaire from '../components/Questionnaire.vue'
import { runEngine } from '../utils/assistEngine.js'

const gated = ref(false)
const agree = ref(false)
const result = ref(null)

const steps = computed(() => runEngine({}).ontology)

function onComplete(answers) {
  result.value = runEngine(answers)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
function reset() {
  result.value = null
}
</script>
