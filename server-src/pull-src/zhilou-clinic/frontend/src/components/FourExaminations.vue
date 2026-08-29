<template>
  <div class="four-examinations">
    <!-- Disease Type Selection -->
    <div class="exam-section disease-selector">
      <h3 class="section-title">
        <el-icon><FirstAidKit /></el-icon>
        <span>病种选择</span>
      </h3>
      <el-radio-group v-model="diseaseType" @change="handleDiseaseTypeChange">
        <el-radio-button label="痔疮">痔疮</el-radio-button>
        <el-radio-button label="肛裂">肛裂</el-radio-button>
        <el-radio-button label="肛周脓肿">肛周脓肿</el-radio-button>
        <el-radio-button label="直肠脱垂">直肠脱垂</el-radio-button>
        <el-radio-button label="肛瘘">肛瘘</el-radio-button>
        <el-radio-button label="肛门疣赘">肛门疣赘</el-radio-button>
        <el-radio-button label="肛门疖肿">肛门疖肿</el-radio-button>
        <el-radio-button label="便秘">便秘</el-radio-button>
        <el-radio-button label="肛门湿疹">肛门湿疹</el-radio-button>
      </el-radio-group>

      <!-- 证型一键填充 -->
      <div v-if="quickTemplates.length" class="quick-fill">
        <span class="quick-fill-label">证型一键填充：</span>
        <el-tag
          v-for="tpl in quickTemplates"
          :key="tpl.id"
          class="quick-fill-chip"
          :effect="lastFilledId === tpl.id ? 'dark' : 'plain'"
          type="success"
          @click="quickFill(tpl)"
        >
          {{ shortName(tpl.template_name) }}
        </el-tag>
      </div>
    </div>

    <!-- Collapse Panels for Four Examinations -->
    <el-collapse v-model="activeExams" class="exam-collapse">
      <!-- 望诊 -->
      <el-collapse-item name="inspection" class="exam-panel">
        <template #title>
          <div class="panel-title">
            <el-icon><View /></el-icon>
            <span>望诊</span>
            <el-tag v-if="inspectionCount > 0" type="success" size="small" class="count-tag">
              已填{{ inspectionCount }}项
            </el-tag>
          </div>
        </template>

        <div class="exam-content">
          <!-- 舌诊 -->
          <div class="exam-group">
            <h4 class="group-title">舌诊</h4>
            <ChipSelect v-model="symptoms.tongue_color" label="舌质" :options="['淡红','红','深红','淡白','紫暗','青紫']" />
            <ChipSelect v-model="symptoms.tongue_coating" label="舌苔" :options="['薄白','白滑','白腻','白厚','薄黄','黄','黄燥','黄腻','少苔','无苔','腻苔']" />
            <ChipSelect v-model="symptoms.tongue_shape" label="舌形" :options="['正常','胖大齿痕','瘦薄','裂纹']" />
          </div>

          <!-- 肛门局部望诊 -->
          <div class="exam-group">
            <h4 class="group-title">肛门局部</h4>
            <ChipSelect v-model="symptoms.anal_color" label="色泽" :options="['正常','鲜红','暗红','紫暗','淡白']" />
            <ChipSelect v-model="symptoms.anal_swelling" label="肿胀" :options="['无','轻度','中度','重度']" />
            <ChipSelect v-model="symptoms.secretion" label="分泌物" :options="['无','血性','脓性','粘液性']" />
          </div>
        </div>
      </el-collapse-item>

      <!-- 原著专科核对项 -->
      <el-collapse-item name="zhou-specialist" class="exam-panel">
        <template #title>
          <div class="panel-title">
            <el-icon><DocumentChecked /></el-icon>
            <span>原著专科核对</span>
            <el-tag v-if="specialistCount > 0" type="success" size="small" class="count-tag">已填{{ specialistCount }}项</el-tag>
          </div>
        </template>
        <div class="exam-content zhou-specialist-fields">
          <el-alert
            title="这些字段用于还原原文病种形态和阶段，不替代指检、肛门镜、影像或病理。"
            type="info"
            :closable="false"
            show-icon
          />
          <div v-if="diseaseType === '痔疮'" class="specialist-group">
            <ChipSelect v-model="symptoms.hemorrhoid_subtype" label="痔疮形态" :options="['血栓外痔','结缔组织外痔','静脉曲张性外痔','炎性外痔','内痔','混合痔','环状混合痔']" />
            <ChipSelect v-model="symptoms.dentate_relation" label="齿线关系" :options="['齿线上','齿线下','跨越齿线','未查']" />
            <div class="field-item"><label>肛门镜所见</label><el-input v-model="symptoms.anoscopy_finding" clearable placeholder="记录黏膜、痔体及脱出" /></div>
          </div>
          <div v-if="diseaseType === '肛周脓肿'" class="specialist-group">
            <ChipSelect v-model="symptoms.abscess_location" label="脓肿部位" :options="['骨盆直肠窝','直肠后','黏膜下','坐骨直肠窝','肛周皮下','肛门后']" />
            <ChipSelect v-model="symptoms.fluctuant" label="波动/成脓" :options="[{label:'未见波动', value:false},{label:'触及波动', value:true}]" empty-value="" />
            <div class="field-item"><label>严重感染警讯</label><el-checkbox v-model="symptoms.rapid_spread">迅速扩散</el-checkbox><el-checkbox v-model="symptoms.crepitus">捻发感</el-checkbox></div>
          </div>
          <div v-if="diseaseType === '肛裂'" class="specialist-group">
            <div class="field-item"><label>病程（天）</label><el-input-number v-model="symptoms.duration_days" :min="0" :max="9999" controls-position="right" /></div>
            <ChipSelect v-model="symptoms.fissure_location" label="裂口位置" :options="['后正中','前正中','左侧','右侧','多发']" />
            <div class="field-item"><label>陈旧性改变</label><el-checkbox v-model="symptoms.ulcer">溃疡</el-checkbox><el-checkbox v-model="symptoms.skin_tag">皮赘</el-checkbox><el-checkbox v-model="symptoms.hidden_fistula">隐瘘</el-checkbox></div>
          </div>
          <div v-if="diseaseType === '直肠脱垂'" class="specialist-group">
            <ChipSelect v-model="symptoms.prolapse_layer" label="脱垂层次" :options="['黏膜脱垂','全层脱垂']" />
            <div class="field-item"><label>脱出长度（厘米）</label><el-input-number v-model="symptoms.prolapse_length_cm" :min="0" :max="50" :precision="1" controls-position="right" /></div>
            <ChipSelect v-model="symptoms.reducibility" label="回纳情况" :options="['自行回纳','需手托回纳','不能回纳']" />
            <ChipSelect v-model="symptoms.age_group" label="年龄分组" :options="['小儿','成人','老年']" />
            <ChipSelect v-model="symptoms.mucosal_injury" label="黏膜状态" :options="['正常','充血','水肿','糜烂','溃疡','紫黑','坏死']" />
          </div>
          <div v-if="diseaseType === '肛瘘'" class="specialist-group">
            <div class="field-item"><label>外口数量</label><el-input-number v-model="symptoms.external_opening_count" :min="0" :max="20" controls-position="right" /></div>
            <div class="field-item"><label>内口</label><el-input v-model="symptoms.internal_opening" placeholder="位置/是否明确" /></div>
            <div class="field-item"><label>主管/支管/死腔</label><el-input v-model="symptoms.main_tract" placeholder="主管走向" /><el-input v-model="symptoms.branch_tract" placeholder="支管" /><el-input v-model="symptoms.dead_space" placeholder="死腔" /></div>
            <ChipSelect v-model="symptoms.wound_phase" label="创面阶段" :options="['腐肉','脓液','肉芽','收口']" />
            <div class="field-item"><label>桥形粘连/假愈合疑点</label><el-checkbox v-model="symptoms.bridge_adhesion">桥形粘连/假愈合疑点</el-checkbox></div>
            <ChipSelect v-model="symptoms.fistula_level" label="瘘管高低位" :options="['低位','高位']" />
            <ChipSelect v-model="symptoms.fistula_complexity" label="复杂程度" :options="['单纯','复杂','复发']" />
          </div>
        </div>
      </el-collapse-item>

      <!-- 闻诊 -->
      <el-collapse-item name="auscultation" class="exam-panel">
        <template #title>
          <div class="panel-title">
            <el-icon><Microphone /></el-icon>
            <span>闻诊</span>
            <el-tag v-if="auscultationCount > 0" type="success" size="small" class="count-tag">
              已填{{ auscultationCount }}项
            </el-tag>
          </div>
        </template>
        <div class="exam-content">
          <ChipSelect v-model="symptoms.odor" label="气味" :options="['无异味','腥臭','恶臭']" />
          <ChipSelect v-model="symptoms.voice" label="语声" :options="['洪亮','低微','气短懒言']" />
        </div>
      </el-collapse-item>

      <!-- 问诊 -->
      <el-collapse-item name="inquiry" class="exam-panel">
        <template #title>
          <div class="panel-title">
            <el-icon><ChatLineSquare /></el-icon>
            <span>问诊</span>
            <el-tag v-if="inquiryCount > 0" type="success" size="small" class="count-tag">
              已填{{ inquiryCount }}项
            </el-tag>
          </div>
        </template>

        <div class="exam-content">
          <!-- 主症 -->
          <div class="exam-group">
            <h4 class="group-title">主症</h4>

            <!-- 便血 -->
            <div class="compound-symptom">
              <div class="symptom-header">
                <el-checkbox v-model="symptoms.bleeding.present" @change="handleBleedingChange">
                  <strong>便血</strong>
                </el-checkbox>
              </div>
              <div v-if="symptoms.bleeding.present" class="symptom-details">
                <ChipSelect v-model="symptoms.bleeding.color" label="颜色" :options="['鲜红','暗红','晦暗','紫黑']" />
                <ChipSelect v-model="symptoms.bleeding.volume" label="量" :options="['点滴','少量','中量','大量','射血']" />
                <ChipSelect v-model="symptoms.bleeding.timing" label="时机" :options="['便前','便中','便后','不定']" />
              </div>
            </div>

            <!-- 疼痛 -->
            <div class="compound-symptom">
              <div class="symptom-header">
                <el-checkbox v-model="symptoms.pain.present" @change="handlePainChange">
                  <strong>疼痛</strong>
                </el-checkbox>
              </div>
              <div v-if="symptoms.pain.present" class="symptom-details">
                <ChipSelect v-model="symptoms.pain.degree" label="程度" :options="['轻度','中度','重度','剧烈']" />
                <ChipSelect v-model="symptoms.pain.nature" label="性质" :options="['刺痛','胀痛','灼痛','隐痛','跳痛']" />
                <ChipSelect v-model="symptoms.pain.timing" label="时机" :options="['便时','便后持续','夜间加重','持续痛']" />
              </div>
            </div>

            <!-- 脱出 -->
            <div class="compound-symptom">
              <div class="symptom-header">
                <el-checkbox v-model="symptoms.prolapse_symptom.present" @change="handleProlapseChange">
                  <strong>脱出</strong>
                </el-checkbox>
              </div>
              <div v-if="symptoms.prolapse_symptom.present" class="symptom-details">
                <ChipSelect v-model="symptoms.prolapse_symptom.degree" label="程度" :options="['I度','II度','III度','IV度']" />
              </div>
            </div>

            <!-- 肿胀 -->
            <div class="compound-symptom">
              <div class="symptom-header">
                <el-checkbox v-model="symptoms.swelling_symptom.present" @change="handleSwellingChange">
                  <strong>肿胀</strong>
                </el-checkbox>
              </div>
              <div v-if="symptoms.swelling_symptom.present" class="symptom-details">
                <ChipSelect v-model="symptoms.swelling_symptom.location" label="部位" :options="['内痔','外痔','混合痔','肛周']" />
              </div>
            </div>

            <!-- 瘙痒 -->
            <div class="compound-symptom">
              <div class="symptom-header">
                <el-checkbox v-model="symptoms.itching.present" @change="handleItchingChange">
                  <strong>瘙痒</strong>
                </el-checkbox>
              </div>
              <div v-if="symptoms.itching.present" class="symptom-details">
                <ChipSelect v-model="symptoms.itching.degree" label="程度" :options="['轻度','中度','重度']" />
              </div>
            </div>
          </div>

          <!-- 次症 -->
          <div class="exam-group">
            <h4 class="group-title">次症</h4>
            <ChipSelect v-model="symptoms.stool_condition" label="大便" :options="['正常','干结','秘结','溏泄','稀软','先干后溏','腹泻']" />
            <ChipSelect v-model="symptoms.urination" label="小便" :options="['正常','短赤','清长','频数','淋漓']" />
            <ChipSelect v-model="symptoms.thirst" label="口渴" :options="['不渴','口渴喜冷饮','口渴喜热饮','口干不欲饮']" />
            <ChipSelect v-model="symptoms.fever" label="发热" :options="['无','低热','高热','恶寒发热','潮热']" />

            <div class="checkbox-group">
              <el-checkbox v-model="symptoms.fatigue">神疲乏力</el-checkbox>
              <el-checkbox v-model="symptoms.pale_complexion">面色无华</el-checkbox>
              <el-checkbox v-model="symptoms.poor_appetite">食欲不振</el-checkbox>
              <el-checkbox v-model="symptoms.insomnia">心烦失眠</el-checkbox>
              <el-checkbox v-model="symptoms.lumbar_soreness">腰膝酸软</el-checkbox>
              <el-checkbox v-model="symptoms.bitter_mouth">口苦</el-checkbox>
              <el-checkbox v-model="symptoms.anal_distension">肛门坠胀</el-checkbox>
              <el-checkbox v-model="symptoms.anal_burning">肛门灼热</el-checkbox>
              <el-checkbox v-model="symptoms.cough">咳嗽</el-checkbox>
              <el-checkbox v-model="symptoms.shortness_of_breath">气短</el-checkbox>
              <el-checkbox v-model="symptoms.night_sweats">盗汗</el-checkbox>
            </div>
          </div>
        </div>
      </el-collapse-item>

      <!-- 切诊 -->
      <el-collapse-item name="palpation" class="exam-panel">
        <template #title>
          <div class="panel-title">
            <el-icon><Pointer /></el-icon>
            <span>切诊</span>
            <el-tag v-if="palpationCount > 0" type="success" size="small" class="count-tag">
              已填{{ palpationCount }}项
            </el-tag>
          </div>
        </template>

        <div class="exam-content">
          <!-- 脉象 -->
          <div class="exam-group">
            <h4 class="group-title">脉象（可多选）</h4>
            <div class="checkbox-group pulse-group">
              <el-checkbox v-model="symptoms.pulse_floating">浮脉</el-checkbox>
              <el-checkbox v-model="symptoms.pulse_deep">沉脉</el-checkbox>
              <el-checkbox v-model="symptoms.pulse_slow">迟脉</el-checkbox>
              <el-checkbox v-model="symptoms.pulse_rapid">数脉</el-checkbox>
              <el-checkbox v-model="symptoms.pulse_wiry">弦脉</el-checkbox>
              <el-checkbox v-model="symptoms.pulse_slippery">滑脉</el-checkbox>
              <el-checkbox v-model="symptoms.pulse_fine">细脉</el-checkbox>
              <el-checkbox v-model="symptoms.pulse_weak">弱脉</el-checkbox>
              <el-checkbox v-model="symptoms.pulse_surging">洪脉</el-checkbox>
              <el-checkbox v-model="symptoms.pulse_full">实脉</el-checkbox>
            </div>
          </div>

          <!-- 腹诊 -->
          <div class="exam-group">
            <h4 class="group-title">腹诊</h4>
            <el-radio-group v-model="symptoms.abdomen">
              <el-radio label="腹部柔软">腹部柔软</el-radio>
              <el-radio label="腹胀">腹胀</el-radio>
              <el-radio label="按之痛">按之痛</el-radio>
            </el-radio-group>
          </div>

          <!-- 肛门指诊 -->
          <div class="exam-group">
            <h4 class="group-title">肛门指诊</h4>
            <ChipSelect v-model="symptoms.sphincter" label="括约肌" :options="['正常','松弛','痉挛']" />
          </div>
        </div>
      </el-collapse-item>
    </el-collapse>

    <!-- Action Buttons -->
    <div class="exam-actions">
      <el-button @click="handleClear" size="large">
        <el-icon><RefreshLeft /></el-icon>
        清空重填
      </el-button>
      <el-button type="primary" @click="handleAnalyze" size="large" :loading="analyzing">
        <el-icon><MagicStick /></el-icon>
        智能辨证
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { analyzeSyndrome, listTemplates, getTemplate } from '@/api/diagnosis'
import ChipSelect from './ChipSelect.vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue', 'analyze', 'analyze-complete', 'disease-type-change', 'symptoms-change'])

const diseaseType = ref('痔疮')
const activeExams = ref(['inspection', 'auscultation', 'inquiry', 'palpation'])

// 证型一键填充
const quickTemplates = ref([])
const lastFilledId = ref('')
const analyzing = ref(false)

// Symptoms data structure
const symptoms = ref({
  // 望诊
  tongue_color: '',
  tongue_coating: '',
  tongue_shape: '',
  anal_color: '',
  anal_swelling: '',
  secretion: '',

  // 闻诊
  odor: '',
  voice: '',

  // 问诊主症
  bleeding: { present: false, color: '', volume: '', timing: '' },
  pain: { present: false, degree: '', nature: '', timing: '' },
  prolapse_symptom: { present: false, degree: '' },
  swelling_symptom: { present: false, location: '' },
  itching: { present: false, degree: '' },

  // 问诊次症
  stool_condition: '',
  urination: '',
  thirst: '',
  fever: '',
  fatigue: false,
  pale_complexion: false,
  poor_appetite: false,
  insomnia: false,
  lumbar_soreness: false,
  bitter_mouth: false,
  anal_distension: false,
  anal_burning: false,
  cough: false,
  shortness_of_breath: false,
  night_sweats: false,

  // 切诊
  pulse_floating: false,
  pulse_deep: false,
  pulse_slow: false,
  pulse_rapid: false,
  pulse_wiry: false,
  pulse_slippery: false,
  pulse_fine: false,
  pulse_weak: false,
  pulse_surging: false,
  pulse_full: false,
  abdomen: '',
  sphincter: '',

  // 原著专科核对
  hemorrhoid_subtype: '',
  dentate_relation: '',
  anoscopy_finding: '',
  abscess_location: '',
  fluctuant: null,
  rapid_spread: false,
  crepitus: false,
  duration_days: null,
  fissure_location: '',
  ulcer: false,
  skin_tag: false,
  hidden_fistula: false,
  prolapse_layer: '',
  prolapse_length_cm: null,
  reducibility: '',
  mucosal_injury: '',
  age_group: '',
  external_opening_count: null,
  internal_opening: '',
  main_tract: '',
  branch_tract: '',
  dead_space: '',
  wound_phase: '',
  bridge_adhesion: false,
  fistula_level: '',
  fistula_complexity: ''
})

// Computed counts for each examination type
const inspectionCount = computed(() => {
  let count = 0
  if (symptoms.value.tongue_color) count++
  if (symptoms.value.tongue_coating) count++
  if (symptoms.value.tongue_shape) count++
  if (symptoms.value.anal_color) count++
  if (symptoms.value.anal_swelling) count++
  if (symptoms.value.secretion) count++
  return count
})

const auscultationCount = computed(() => {
  let count = 0
  if (symptoms.value.odor) count++
  if (symptoms.value.voice) count++
  return count
})

const inquiryCount = computed(() => {
  let count = 0
  if (symptoms.value.bleeding.present) count++
  if (symptoms.value.pain.present) count++
  if (symptoms.value.prolapse_symptom.present) count++
  if (symptoms.value.swelling_symptom.present) count++
  if (symptoms.value.itching.present) count++
  if (symptoms.value.stool_condition) count++
  if (symptoms.value.urination) count++
  if (symptoms.value.thirst) count++
  if (symptoms.value.fever) count++
  if (symptoms.value.fatigue) count++
  if (symptoms.value.pale_complexion) count++
  if (symptoms.value.poor_appetite) count++
  if (symptoms.value.insomnia) count++
  if (symptoms.value.lumbar_soreness) count++
  if (symptoms.value.bitter_mouth) count++
  return count
})

const palpationCount = computed(() => {
  let count = 0
  if (symptoms.value.pulse_floating) count++
  if (symptoms.value.pulse_deep) count++
  if (symptoms.value.pulse_slow) count++
  if (symptoms.value.pulse_rapid) count++
  if (symptoms.value.pulse_wiry) count++
  if (symptoms.value.pulse_slippery) count++
  if (symptoms.value.pulse_fine) count++
  if (symptoms.value.pulse_weak) count++
  if (symptoms.value.pulse_surging) count++
  if (symptoms.value.pulse_full) count++
  if (symptoms.value.abdomen) count++
  if (symptoms.value.sphincter) count++
  return count
})

const specialistCount = computed(() => Object.entries(symptoms.value).filter(([key, value]) =>
  ['hemorrhoid_subtype','dentate_relation','anoscopy_finding','abscess_location','fluctuant','duration_days','fissure_location','ulcer','skin_tag','hidden_fistula','prolapse_layer','prolapse_length_cm','reducibility','mucosal_injury','age_group','external_opening_count','internal_opening','main_tract','branch_tract','dead_space','wound_phase','bridge_adhesion','fistula_level','fistula_complexity'].includes(key) && value !== '' && value !== null && value !== undefined && value !== false
).length)

// Handle compound symptom changes
function handleBleedingChange(val) {
  if (!val) {
    symptoms.value.bleeding = { present: false, color: '', volume: '', timing: '' }
  }
}

function handlePainChange(val) {
  if (!val) {
    symptoms.value.pain = { present: false, degree: '', nature: '', timing: '' }
  }
}

function handleProlapseChange(val) {
  if (!val) {
    symptoms.value.prolapse_symptom = { present: false, degree: '' }
  }
}

function handleSwellingChange(val) {
  if (!val) {
    symptoms.value.swelling_symptom = { present: false, location: '' }
  }
}

function handleItchingChange(val) {
  if (!val) {
    symptoms.value.itching = { present: false, degree: '' }
  }
}

function handleDiseaseTypeChange() {
  emit('disease-type-change', diseaseType.value)
  loadQuickTemplates()
}

function shortName(name) {
  return (name || '').replace('（一键辨证）', '').replace('一键辨证', '')
}

async function loadQuickTemplates() {
  quickTemplates.value = []
  lastFilledId.value = ''
  try {
    const res = await listTemplates({ disease_type: diseaseType.value, template_type: 'system' })
    quickTemplates.value = res || []
  } catch (e) {
    console.error('加载证型模板失败:', e)
  }
}

async function quickFill(tpl) {
  try {
    const res = await getTemplate(tpl.id)
    loadSymptoms(res.symptoms_data)
    lastFilledId.value = tpl.id
  } catch (e) {
    console.error('加载模板详情失败:', e)
    ElMessage.error('一键填充失败')
  }
}

function handleClear() {
  symptoms.value = {
    tongue_color: '',
    tongue_coating: '',
    tongue_shape: '',
    anal_color: '',
    anal_swelling: '',
    secretion: '',
    odor: '',
    voice: '',
    bleeding: { present: false, color: '', volume: '', timing: '' },
    pain: { present: false, degree: '', nature: '', timing: '' },
    prolapse_symptom: { present: false, degree: '' },
    swelling_symptom: { present: false, location: '' },
    itching: { present: false, degree: '' },
    stool_condition: '',
    urination: '',
    thirst: '',
    fever: '',
    fatigue: false,
    pale_complexion: false,
    poor_appetite: false,
    insomnia: false,
    lumbar_soreness: false,
    bitter_mouth: false,
    anal_distension: false,
    anal_burning: false,
    cough: false,
    shortness_of_breath: false,
    night_sweats: false,
    pulse_floating: false,
    pulse_deep: false,
    pulse_slow: false,
    pulse_rapid: false,
    pulse_wiry: false,
    pulse_slippery: false,
    pulse_fine: false,
    pulse_weak: false,
    pulse_surging: false,
    pulse_full: false,
    abdomen: '',
    sphincter: ''
    ,hemorrhoid_subtype: '', dentate_relation: '', anoscopy_finding: '', abscess_location: '', fluctuant: null, rapid_spread: false, crepitus: false,
    duration_days: null, fissure_location: '', ulcer: false, skin_tag: false, hidden_fistula: false,
    prolapse_layer: '', prolapse_length_cm: null, reducibility: '', mucosal_injury: '', age_group: '',
    external_opening_count: null, internal_opening: '', main_tract: '', branch_tract: '', dead_space: '', wound_phase: '', bridge_adhesion: false,
    fistula_level: '', fistula_complexity: ''
  }
  ElMessage.success('已清空症状数据')
}

async function handleAnalyze() {
  // Validate required fields
  if (!diseaseType.value) {
    ElMessage.warning('请先选择病种')
    return
  }

  const totalCount = inspectionCount.value + auscultationCount.value + inquiryCount.value + palpationCount.value
  if (totalCount < 5) {
    ElMessage.warning('请至少填写5项症状信息')
    return
  }

  analyzing.value = true
  try {
    const res = await analyzeSyndrome({
      disease_type: diseaseType.value,
      selected_symptoms: symptoms.value
    })

    emit('analyze', {
      disease_type: diseaseType.value,
      symptoms: symptoms.value,
      result: res
    })

    emit('analyze-complete', res)

    ElMessage.success('辨证分析完成')
  } catch (error) {
    ElMessage.error(error.message || '辨证分析失败')
  } finally {
    analyzing.value = false
  }
}

// Watch for external changes
watch(() => props.modelValue, (val) => {
  if (val && Object.keys(val).length > 0) {
    symptoms.value = { ...symptoms.value, ...val }
  }
}, { immediate: true, deep: true })

// Emit changes
watch(symptoms, (val) => {
  emit('update:modelValue', val)
  emit('symptoms-change', val)
}, { deep: true })

// Phase 4: Load symptoms from template
function loadSymptoms(symptomsData) {
  symptoms.value = { ...symptoms.value, ...symptomsData }
  ElMessage.success('症状模板已加载')
}

// Expose methods for parent component
defineExpose({
  loadSymptoms
})

onMounted(() => {
  emit('disease-type-change', diseaseType.value)
  loadQuickTemplates()
})

</script>

<style scoped>
.four-examinations {
  max-width: 1200px;
  margin: 0 auto;
}

.disease-selector {
  background: #FFFFFF;
  border: 1px solid #E7E3DA;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}

.quick-fill {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed #E7E3DA;
}

.quick-fill-label {
  font-size: 13px;
  color: #6B7077;
  font-weight: 500;
}

.quick-fill-chip {
  cursor: pointer;
  transition: all 0.2s;
}
.quick-fill-chip:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(60, 90, 120, 0.15);
}

.section-title {
  font-family: 'Playfair Display', serif;
  font-size: 18px;
  font-weight: 600;
  color: #1E2227;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.exam-collapse {
  border: none;
}

.exam-panel {
  background: #FFFFFF;
  border: 1px solid #E7E3DA;
  border-radius: 12px;
  margin-bottom: 16px;
  overflow: hidden;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
  color: #1E2227;
}

.count-tag {
  margin-left: auto;
}

.exam-content {
  padding: 24px;
  background: #F7F5F1;
}

.exam-group {
  margin-bottom: 24px;
}

.exam-group:last-child {
  margin-bottom: 0;
}

.group-title {
  font-size: 15px;
  font-weight: 500;
  color: #3C5A78;
  margin: 0 0 16px 0;
  padding-left: 12px;
  border-left: 3px solid #3C5A78;
}

.field-item {
  margin-bottom: 16px;
}

.field-item label {
  display: block;
  font-size: 14px;
  color: #6B7077;
  margin-bottom: 8px;
}

.field-item :deep(.el-select),
.field-item :deep(.el-input) {
  width: 100%;
}

.compound-symptom {
  background: #FFFFFF;
  border: 1px solid #E7E3DA;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
}

.symptom-header {
  margin-bottom: 12px;
}

.symptom-details {
  padding-left: 24px;
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.pulse-group {
  background: #FFFFFF;
  border: 1px solid #E7E3DA;
  border-radius: 8px;
  padding: 16px;
}

.exam-actions {
  position: sticky;
  bottom: 0;
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  padding: 12px 16px;
  background: linear-gradient(180deg, rgba(250, 249, 246, 0) 0%, #FAF9F6 30%);
  border-radius: 8px;
  z-index: 10;
}

.exam-actions .el-button {
  min-width: 140px;
}

@media (max-width: 768px) {
  .disease-selector {
    padding: 16px;
  }

  .exam-content {
    padding: 16px;
  }

  .checkbox-group {
    flex-direction: column;
    gap: 8px;
  }

  .exam-actions {
    flex-direction: column;
  }

  .exam-actions .el-button {
    width: 100%;
  }
}
</style>
