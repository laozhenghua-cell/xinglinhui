<template>
  <div>
    <h1 class="page-title">科普自测 · 就医指引</h1>
    <div class="page-sub">了解症状可能对应的中医外科病证 + 该不该就医、多紧急 · 不提供任何方剂</div>
    <div class="safety-banner"><strong>⚠️</strong> 本页仅为健康科普，不构成诊断；丹药剧毒，请勿自行购用任何丹药制品。</div>

    <Questionnaire v-if="!result" :steps="pubSteps" :required-ids="['poison']" @complete="onComplete" />

    <div v-else>
      <!-- 红旗 -->
      <div v-if="reds.length" class="card" style="border:2px solid #c0392b;background:#fdf0ef">
        <h3 style="color:#c0392b;margin-top:0">🛑 红旗：请立即就医</h3>
        <div v-for="(m, i) in reds" :key="i" style="font-size:0.92rem;line-height:1.8"><strong>· {{ m }}</strong></div>
        <p style="font-size:0.85rem;color:#8a2f2f;margin-bottom:0">上述情况可能危及生命，请立即前往急诊，不要自行处理。</p>
      </div>

      <!-- 黄旗 -->
      <div v-if="yellows.length" class="card" style="border:1.5px solid #d98e2b;background:#fdf6e8">
        <h3 style="color:#b35309;margin-top:0">🟡 黄旗：请尽快就医</h3>
        <div v-for="(m, i) in yellows" :key="i" style="font-size:0.9rem;margin:6px 0">{{ m }}</div>
      </div>

      <!-- 绿旗 + 病证科普 -->
      <div class="card" v-if="!reds.length">
        <h3 style="margin-top:0">🟢 绿旗：建议一般就医</h3>
        <p style="font-size:0.9rem;color:#5c5240;margin:0">
          您的情况未命中危急信号，可于近期至正规医院皮肤科或中医外科就诊，勿自行用药。
        </p>
      </div>

      <div class="card" v-if="matches.length">
        <h3 style="margin-top:0">📖 可能相关的中医外科病证（科普）</h3>
        <div v-for="k in matches" :key="k.id" style="border-top:1px dashed #e0d5bd;padding:10px 0">
          <strong style="color:var(--dan-red)">{{ k.name }}</strong>
          <div style="font-size:0.88rem;color:#6b5c42;margin-top:4px">{{ k.desc }}</div>
        </div>
        <div style="font-size:0.78rem;color:#9a8a6c;margin-top:8px">
          名词释义据张觉人《中国炼丹术与丹药》（四川人民出版社1984）及中医外科学常识整理。
        </div>
      </div>

      <div class="card">
        <h3 style="margin-top:0">🏛️ 丹丹药史话</h3>
        <p style="font-size:0.88rem;color:#5c5240;margin:0">
          中医外科丹药源出炼丹术，历史上以汞、砷化合物用于腐蚀、拔毒、提脓、生肌，对久不愈合的顽固疮疡曾有独到之功，
          但因蓄积毒性强，现代已被安全替代品大量取代，仅个别流派在严格条件下研究性应用。
          想系统了解历史与理论，可阅读<a @click="$router.push('/alchemy/chapters')">总论源流</a>与
          <a @click="$router.push('/alchemy/timeline')">炼丹时间线</a>。
        </p>
      </div>

      <div style="text-align:center;margin-top:16px">
        <el-button @click="reset">重新自测</el-button>
        <el-button type="danger" plain @click="$router.push('/alchemy/assist/professional')">专业研究入口 →</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import Questionnaire from '../components/Questionnaire.vue'
import ontology from '../data/assist-ontology.json'

const result = ref(null)
const pubStepIds = ['site', 'lesion', 'systemic', 'poison']
const pubSteps = computed(() => ontology.steps.filter((s) => pubStepIds.includes(s.id)))

const REDS = [
  { any: ['po_metallic', 'po_tremor', 'po_oliguria', 'po_rash'], msg: '出现口腔金属味、牙龈出血、震颤、少尿血尿或皮疹剥脱——可能为重金属中毒征象（若曾接触丹药/汞制品尤须警惕）。' },
  { any: ['po_high_fever'], msg: '高热不退、神志异常或呼吸困难——可能为严重感染或脓毒血症。' },
]
const YELLOWS = [
  { any: ['lesion_fistula', 'lesion_deadbone'], msg: '疮口反复流脓、经久不愈或脓中夹腐肉死骨——需排查骨髓炎、骨结核等深部感染。' },
  { any: ['lesion_scrofula', 'site_neck'], msg: '颈项部串珠状肿块——需排查淋巴结核（瘰疬）或其他颈部肿块。' },
  { any: ['sys_night_sweat', 'sys_bone_fever', 'sys_thin'], msg: '盗汗、骨蒸潮热、消瘦——需排查结核类疾病。' },
  { any: ['site_eye'], msg: '眼部症状——需至眼科就诊，切勿自行点用药物。' },
]
const KBS = [
  { id: 'kb_yong', name: '痈', match: ['lesion_swell'], desc: '红肿高突、灼热疼痛的化脓性感染，多属阳证热毒，中医外科以清热解毒、消肿溃脓为法。' },
  { id: 'kb_ju', name: '疽', match: ['lesion_flat'], desc: '漫肿平塌、疼痛不著的深部疮疡，多属阴证，起病缓而难愈，需及时就医。' },
  { id: 'kb_ding', name: '疔', match: ['lesion_boil'], desc: '根深坚硬如钉、痛剧而险的急性疮疡，面部疔疮尤须警惕走黄（败血症），应立即就医。' },
  { id: 'kb_luoli', name: '瘰疬（痰核）', match: ['lesion_scrofula', 'lesion_phlegm'], desc: '颈项部成串的慢性肿块，古籍多与结核类疾病相关，需系统检查。' },
  { id: 'kb_louguan', name: '瘘管（漏管）', match: ['lesion_fistula'], desc: '深部脓腔与体表相通的慢性窦道，反复流脓，多需外科处理。' },
  { id: 'kb_kuiyang', name: '久溃不敛', match: ['lesion_ulcer', 'stage_chronic'], desc: '疮口长期不愈合，古籍常与气血亏虚或深部病灶（死骨、异物）有关。' },
  { id: 'kb_shichuang', name: '湿疮（湿疹）', match: ['lesion_eczema'], desc: '糜烂渗水的皮肤炎症，中西医治疗手段均较成熟，应到皮肤科就诊。' },
  { id: 'kb_jiexuan', name: '疥癣', match: ['lesion_scabies'], desc: '瘙痒性皮肤病，需明确病因（疥虫、真菌等）后规范治疗。' },
]

const reds = computed(() => REDS.filter((r) => r.any.some((id) => allIds.value.includes(id))).map((r) => r.msg))
const yellows = computed(() => YELLOWS.filter((r) => r.any.some((id) => allIds.value.includes(id))).map((r) => r.msg))
const allIds = computed(() => result.value ? Object.values(result.value).flat() : [])
const matches = computed(() => KBS.filter((k) => k.match.some((id) => allIds.value.includes(id))))

function onComplete(answers) {
  result.value = answers
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
function reset() {
  result.value = null
}
</script>
