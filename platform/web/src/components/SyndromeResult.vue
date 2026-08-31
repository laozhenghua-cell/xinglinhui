<template>
  <div class="syndrome-result">
    <div v-if="!result" class="empty-state">
      <el-icon :size="64" color="#6B7077"><MagicStick /></el-icon>
      <p>填写四诊信息后，点击"智能辨证"查看结果</p>
    </div>

    <div v-else class="result-content">
      <el-alert
        v-if="result.primary_syndrome.insufficient_data"
        title="四诊资料不足，以下仅为候选证型"
        description="请补充舌象、脉象及关键主症后重新辨证；当前结果不应直接作为处方依据。"
        type="warning"
        :closable="false"
        show-icon
        class="insufficient-alert"
      />
      <!-- Primary Syndrome -->
      <div class="primary-syndrome">
        <div class="syndrome-header">
          <h3 class="syndrome-title">
            <el-icon><TrophyBase /></el-icon>
            主证型
          </h3>
          <el-tag type="success" size="large" class="confidence-tag">
            符合 {{ evidenceMatched.length }} 项
          </el-tag>
        </div>

        <div class="syndrome-card">
          <div class="patient-line" v-if="patient?.name">
            <el-icon><User /></el-icon>
            <span>{{ patient.name }}</span>
            <span v-if="patient.gender" class="patient-meta">{{ patient.gender }}</span>
            <span v-if="patient.age != null" class="patient-meta">{{ patient.age }}岁</span>
          </div>

          <div class="syndrome-name">
            {{ result.primary_syndrome.syndrome_name }}
          </div>

          <div class="syndrome-meta">
            <div class="meta-item" v-if="result.primary_syndrome.tongue_pulse">
              <label>舌脉</label>
              <span v-if="typeof result.primary_syndrome.tongue_pulse === 'string'">{{ result.primary_syndrome.tongue_pulse }}</span>
              <span v-else>
                {{ result.primary_syndrome.tongue_pulse.tongue }}，
                {{ result.primary_syndrome.tongue_pulse.pulse }}
              </span>
            </div>
            <div class="meta-item" v-if="treatmentMode">
              <label>治法</label>
              <el-tag :type="treatmentMode.type" effect="dark" size="small">{{ treatmentMode.label }}</el-tag>
            </div>
          </div>

          <div class="treatment-principle">
            <h4>治则治法</h4>
            <p>{{ result.primary_syndrome.treatment_principle }}</p>
          </div>

          <!-- Recommended Formulas -->
          <div v-if="!result.primary_syndrome.insufficient_data" class="recommended-formulas clinical-section">
            <div class="section-heading">
              <div>
                <span class="section-kicker">内治</span>
                <h4>内服方（医师审核稿）</h4>
              </div>
              <el-tag type="warning" effect="plain">须审核后开具</el-tag>
            </div>
            <el-alert
              title="剂量、疗程须结合年龄、妊娠哺乳、肝肾功能、过敏史及合并用药复核。"
              type="warning"
              :closable="false"
              show-icon
              class="prescription-notice"
            />
            <div class="formula-list">
              <div
                v-for="(formula, index) in result.primary_syndrome.recommended_formulas"
                :key="index"
                class="formula-card"
                :class="{ 'priority-1': formula.priority === 1 }"
              >
                <div class="formula-header">
                  <div class="formula-title">
                    <el-icon v-if="formula.priority === 1" class="star-icon"><StarFilled /></el-icon>
                    <span class="formula-name">{{ formula.name }}</span>
                    <el-tag v-if="formula.source" size="small" type="info">{{ formula.source }}</el-tag>
                  </div>
                  <el-tag :type="formula.priority === 1 ? 'success' : 'info'" size="large">
                    匹配度 {{ (formula.match_rate * 100).toFixed(0) }}%
                  </el-tag>
                </div>

                <!-- 方剂组成 -->
                <div class="formula-composition" v-if="formula.composition">
                  <label>组成：</label>
                  <!-- 结构化组成（JSONB数组） -->
                  <div v-if="Array.isArray(formula.composition)" class="herb-chips">
                    <span
                      v-for="(herb, i) in formula.composition"
                      :key="i"
                      class="herb-chip"
                    >
                      {{ herb.name }} {{ herb.dosage }}{{ herb.unit }}
                      <span v-if="herb.note" class="herb-note">（{{ herb.note }}）</span>
                    </span>
                  </div>
                  <!-- 旧格式（字符串） -->
                  <div v-else class="composition-text">
                    {{ formula.composition }}
                  </div>
                </div>

                <!-- 功效 -->
                <div class="formula-function" v-if="formula.function">
                  <label>功效：</label>
                  <span>{{ formula.function }}</span>
                </div>

                <div class="formula-indications" v-if="formula.indications">
                  <label>主治：</label>
                  <span>{{ formula.indications }}</span>
                </div>

                <!-- 用法 -->
                <div class="formula-usage" v-if="formula.usage">
                  <label>用法：</label>
                  <span>{{ formula.usage }}</span>
                </div>

                <!-- 加减化裁 -->
                <div class="formula-modifications" v-if="formula.modifications">
                  <label>加减：</label>
                  <div class="modifications-text">{{ formula.modifications }}</div>
                </div>

                <!-- 注意事项 -->
                <div class="formula-notes" v-if="formula.notes">
                  <el-alert type="warning" :closable="false" show-icon>
                    <template #title>
                      <span style="font-size: 13px; font-weight: 500;">{{ formula.notes }}</span>
                    </template>
                  </el-alert>
                </div>

                <div class="formula-contraindications" v-if="formula.contraindications">
                  <label>禁忌：</label>
                  <span>{{ formula.contraindications }}</span>
                </div>

                <div class="formula-actions">
                  <el-button
                    size="default"
                    :type="formula.priority === 1 ? 'primary' : ''"
                    @click="selectFormula(formula)"
                    :disabled="result.primary_syndrome.insufficient_data"
                    style="width: 100%;"
                  >
                    <el-icon><Select /></el-icon>
                    选用此方
                  </el-button>
                </div>
              </div>
            </div>
          </div>
          <el-alert
            v-else
            title="当前不生成内服方或外治方"
            description="关键四诊资料尚未满足证型规则，请先补充上方所列项目并重新辨证。"
            type="warning"
            :closable="false"
            show-icon
            class="no-prescription-alert"
          />

          <!-- Modifications -->
          <div v-if="result.primary_syndrome.modifications && result.primary_syndrome.modifications.length > 0" class="modifications">
            <h4>加减化裁建议</h4>
            <div class="modification-list">
              <div
                v-for="(mod, index) in result.primary_syndrome.modifications"
                :key="index"
                class="modification-item"
              >
                <div class="modification-condition">
                  <el-icon><CircleCheck /></el-icon>
                  <span>{{ mod.condition }}</span>
                </div>
                <div class="modification-action">
                  <template v-if="mod.action.add">
                    <span class="action-label">加：</span>
                    <el-tag
                      v-for="(herb, i) in mod.action.add"
                      :key="i"
                      size="small"
                      type="success"
                      class="herb-tag"
                    >
                      + {{ herb }}
                    </el-tag>
                  </template>
                  <template v-if="mod.action.remove">
                    <span class="action-label">减：</span>
                    <el-tag
                      v-for="(herb, i) in mod.action.remove"
                      :key="i"
                      size="small"
                      type="danger"
                      class="herb-tag"
                    >
                      - {{ herb }}
                    </el-tag>
                  </template>
                  <template v-if="mod.action.increase">
                    <span class="action-label">增量：</span>
                    <el-tag
                      v-for="(herb, i) in mod.action.increase"
                      :key="i"
                      size="small"
                      type="warning"
                      class="herb-tag"
                    >
                      ↑ {{ herb }}
                    </el-tag>
                  </template>
                </div>
              </div>
            </div>
          </div>

          <!-- External Treatments ("内外兼治"思想) -->
          <div v-if="!result.primary_syndrome.insufficient_data && result.primary_syndrome.external_treatments && result.primary_syndrome.external_treatments.length > 0" class="external-treatments clinical-section">
            <div class="section-heading">
              <div>
                <span class="section-kicker">外治</span>
                <h4><el-icon><Histogram /></el-icon> 外用方（医师审核稿）</h4>
              </div>
              <el-tag size="small" type="info" class="zhou-tag">方 {{ zhouExternalCount }} 项</el-tag>
            </div>
            <div class="treatment-grid">
              <div
                v-for="(treatment, index) in result.primary_syndrome.external_treatments"
                :key="index"
                class="treatment-card"
              >
                <div class="treatment-header">
                  <div class="treatment-title">
                    <el-icon class="treatment-icon">
                      <MagicStick v-if="treatment.treatment_type === 'fumigation'" />
                      <FirstAidKit v-else-if="treatment.treatment_type === 'ointment'" />
                      <Lollipop v-else-if="treatment.treatment_type === 'suppository'" />
                      <Operation v-else />
                    </el-icon>
                    <span class="treatment-name">{{ treatment.name }}</span>
                  </div>
                  <el-tag size="small" :type="getTypeColor(treatment.treatment_type)">
                    {{ treatment.treatment_type_name }}
                  </el-tag>
                </div>

                <div class="treatment-body">
                  <div v-if="treatment.source" class="treatment-source">
                    <label>来源：</label>
                    <span>{{ treatment.source }}</span>
                  </div>

                  <div v-if="treatment.composition" class="treatment-composition">
                    <label>组成：</label>
                    <div v-if="Array.isArray(treatment.composition)" class="herb-chips compact">
                      <span v-for="(herb, herbIndex) in treatment.composition" :key="herbIndex" class="herb-chip">
                        {{ formatHerb(herb) }}
                      </span>
                    </div>
                    <span v-else>{{ treatment.composition }}</span>
                  </div>

                  <div v-if="treatment.preparation" class="treatment-preparation">
                    <label>制法：</label>
                    <span>{{ treatment.preparation }}</span>
                  </div>

                  <div class="treatment-function">
                    <label>功效：</label>
                    <span>{{ treatment.function }}</span>
                  </div>

                  <div class="treatment-usage">
                    <label>用法：</label>
                    <span>{{ treatment.usage }}</span>
                  </div>

                  <div class="treatment-frequency">
                    <label>频次：</label>
                    <span>{{ treatment.frequency }}</span>
                  </div>

                  <div v-if="treatment.duration" class="treatment-duration">
                    <label>疗程：</label>
                    <span>{{ treatment.duration }}</span>
                  </div>

                  <div v-if="treatment.indications" class="treatment-indications">
                    <label>适用：</label>
                    <span>{{ treatment.indications }}</span>
                  </div>

                  <div v-if="treatment.contraindications" class="treatment-contraindications">
                    <label>禁忌：</label>
                    <span>{{ treatment.contraindications }}</span>
                  </div>

                  <div v-if="treatment.precautions" class="treatment-precautions">
                    <label>注意事项：</label>
                    <span>{{ treatment.precautions }}</span>
                  </div>

                  <div v-if="treatment.notes" class="treatment-notes">
                    <el-alert type="info" :closable="false" :show-icon="true">
                      <template #title>
                        <span style="font-size: 12px;">{{ treatment.notes }}</span>
                      </template>
                    </el-alert>
                  </div>
                </div>

                <div class="treatment-actions">
                  <el-button size="small" type="primary" plain @click="selectTreatment(treatment)" :disabled="result.primary_syndrome.insufficient_data">
                    采用此法
                  </el-button>
                </div>
              </div>
            </div>
          </div>

          <!-- 针刺法与手术技法（可展开详细） -->
          <div
            v-if="!result.primary_syndrome.insufficient_data"
            class="procedures-section clinical-section"
          >
            <div class="section-heading">
              <div>
                <span class="section-kicker">专业操作</span>
                <h4>针刺法 · 手术技法</h4>
              </div>
            </div>
            <el-collapse>
              <el-collapse-item
                v-if="result.primary_syndrome.original_knowledge?.acupuncture?.protocols?.length"
                title="针刺法（详细）"
                name="acupuncture"
              >
                <el-alert
                  :title="result.primary_syndrome.original_knowledge.acupuncture.governance"
                  type="info"
                  :closable="false"
                  show-icon
                  style="margin-bottom: 12px"
                />
                <div
                  v-for="proto in result.primary_syndrome.original_knowledge.acupuncture.protocols"
                  :key="proto.name"
                  class="procedure-block"
                >
                  <h5 class="procedure-name">{{ proto.name }}</h5>
                  <p v-if="proto.syndrome" class="procedure-meta"><label>适用证型：</label>{{ proto.syndrome }}</p>
                  <p v-if="proto.indication" class="procedure-meta"><label>适应证：</label>{{ proto.indication }}</p>
                  <div class="table-scroll"><table class="point-table">
                    <thead><tr><th>穴位</th><th>归经</th><th>定位</th><th>操作</th></tr></thead>
                    <tbody>
                      <tr v-for="pt in proto.points" :key="pt.name">
                        <td><strong>{{ pt.name }}</strong><el-tag size="small" type="primary" effect="plain" class="role-tag">{{ pt.role }}</el-tag></td>
                        <td>{{ pt.meridian }}</td>
                        <td>{{ pt.location }}</td>
                        <td>{{ pt.method }}<span v-if="pt.depth">；{{ pt.depth }}</span></td>
                      </tr>
                    </tbody>
                  </table></div>
                  <p v-if="proto.course" class="procedure-meta"><label>疗程：</label>{{ proto.course }}</p>
                  <p class="source-line">{{ proto.source }}</p>
                </div>
              </el-collapse-item>

              <el-collapse-item
                v-if="result.primary_syndrome.original_knowledge?.surgical_techniques?.items?.length"
                title="手术技法（详细 · 院内专科）"
                name="surgical"
              >
                <el-alert
                  :title="result.primary_syndrome.original_knowledge.surgical_techniques.governance"
                  type="warning"
                  :closable="false"
                  show-icon
                  style="margin-bottom: 12px"
                />
                <div
                  v-for="tech in result.primary_syndrome.original_knowledge.surgical_techniques.items"
                  :key="tech.name"
                  class="procedure-block"
                >
                  <h5 class="procedure-name">{{ tech.name }}</h5>
                  <p class="procedure-meta"><label>适应证：</label>{{ tech.indication }}</p>
                  <ul class="procedure-points">
                    <li v-for="kp in tech.key_points" :key="kp">{{ kp }}</li>
                  </ul>
                  <p class="source-line">{{ tech.source }}</p>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </div>
      </div>

      <!-- Other Possible Syndromes -->
      <div v-if="result.syndromes.length > 1" class="other-syndromes">
        <h3 class="section-title">
          <el-icon><Grid /></el-icon>
          其他可能证型
        </h3>
        <div class="syndrome-cards">
          <div
            v-for="(syndrome, index) in result.syndromes.slice(1)"
            :key="index"
            class="other-syndrome-card"
          >
            <div class="card-header">
              <span class="syndrome-name-small">{{ syndrome.syndrome_name }}</span>
              <el-tag size="small" type="info">
                {{ (syndrome.confidence * 100).toFixed(0) }}%
              </el-tag>
            </div>
            <p class="treatment-principle-small">{{ syndrome.treatment_principle }}</p>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="result-actions">
        <el-button size="large" @click="handleReanalyze">
          <el-icon><Refresh /></el-icon>
          重新辨证
        </el-button>
        <el-button type="primary" size="large" @click="handleCreatePrescription">
          <el-icon><Document /></el-icon>
          生成处方
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  result: {
    type: Object,
    default: null
  },
  patient: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['selectFormula', 'reanalyze', 'createPrescription', 'selectTreatment'])

const evidenceMatched = computed(() => {
  const evidence = props.result?.primary_syndrome?.evidence
  return [...(evidence?.matched_required || []), ...(evidence?.matched_optional || [])]
})

const evidenceMissing = computed(() => props.result?.primary_syndrome?.evidence?.missing_required || [])

const zhouExternalCount = computed(() => (
  props.result?.primary_syndrome?.external_treatments || []
).filter(treatment => treatment.source?.includes('经验方')).length)

const knowledgeStatusLabel = computed(() => {
  const status = props.result?.primary_syndrome?.original_knowledge?.source_status
  return status === 'original_explicit' ? '原著明确' : status === 'original_case' ? '原著医案' : '系统扩展'
})

const knowledgeStatusType = computed(() => {
  const status = props.result?.primary_syndrome?.original_knowledge?.source_status
  return status === 'original_explicit' ? 'success' : status === 'original_case' ? 'warning' : 'info'
})

const treatmentMode = computed(() => {
  const hasInternal = (props.result?.primary_syndrome?.recommended_formulas || []).length > 0
  const hasExternal = (props.result?.primary_syndrome?.external_treatments || []).length > 0
  if (hasInternal && hasExternal) return { label: '内外同治', type: 'success' }
  if (hasInternal) return { label: '内治', type: 'primary' }
  if (hasExternal) return { label: '外治', type: 'warning' }
  return null
})

function formatHerb(herb) {
  if (typeof herb === 'string') return herb
  if (!herb || typeof herb !== 'object') return ''
  const amount = [herb.dosage, herb.unit].filter(value => value !== undefined && value !== null).join('')
  const note = herb.note ? `（${herb.note}）` : ''
  return `${herb.name || ''}${amount ? ` ${amount}` : ''}${note}`
}

function selectFormula(formula) {
  if (props.result.primary_syndrome.insufficient_data) return
  emit('selectFormula', formula)
  ElMessage.success(`已选择方剂：${formula.name}`)
}

function selectTreatment(treatment) {
  if (props.result.primary_syndrome.insufficient_data) return
  emit('selectTreatment', treatment)
  ElMessage.success(`已选择外治法：${treatment.name}`)
}

function getTypeColor(type) {
  const colorMap = {
    'fumigation': 'warning',
    'ointment': 'success',
    'suppository': 'primary',
    'injection': 'danger'
  }
  return colorMap[type] || 'info'
}

function handleReanalyze() {
  emit('reanalyze')
}

function handleCreatePrescription() {
  if (!props.result) {
    ElMessage.warning('请先完成辨证分析')
    return
  }
  if (props.result.primary_syndrome?.insufficient_data) {
    ElMessage.warning('四诊资料不足，补充资料后才能生成处方')
    return
  }
  emit('createPrescription', props.result.primary_syndrome)
}
</script>

<style scoped>
.syndrome-result {
  max-width: 1200px;
  margin: 0 auto;
}

.empty-state {
  background: #FFFFFF;
  border: 2px dashed #E7E3DA;
  border-radius: 12px;
  padding: 64px 24px;
  text-align: center;
}

.empty-state p {
  margin-top: 16px;
  font-size: 14px;
  color: #6B7077;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.primary-syndrome {
  background: #FFFFFF;
  border: 2px solid #3C5A78;
  border-radius: 12px;
  overflow: hidden;
}

.syndrome-header { flex-wrap: wrap; gap: 8px;
  background: linear-gradient(135deg, #3C5A78 0%, #2E4760 100%);
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.syndrome-title {
  font-family: 'Playfair Display', serif;
  font-size: 20px;
  font-weight: 600;
  color: #FFFFFF;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.confidence-tag {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #FFFFFF;
  font-weight: 600;
}

.syndrome-card {
  padding: 32px 24px;
}

.patient-line {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  color: #3C5A78;
  font-weight: 500;
  margin-bottom: 12px;
  padding: 6px 12px;
  background: #F5F7FA;
  border-radius: 6px;
}
.patient-meta {
  color: #6B7077;
  font-weight: 400;
  font-size: 13px;
}

.syndrome-name {
  font-family: 'Playfair Display', serif;
  font-size: 28px;
  font-weight: 600;
  color: #1E2227;
  margin-bottom: 24px;
  text-align: center;
}

.syndrome-meta {
  display: flex;
  gap: 32px;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #E7E3DA;
}

.meta-item {
  flex: 1;
}

.meta-item label {
  display: block;
  font-size: 12px;
  color: #6B7077;
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.meta-item span {
  font-size: 14px;
  color: #1E2227;
  font-weight: 500;
}

.treatment-principle {
  background: #F7F5F1;
  border-left: 4px solid #3C5A78;
  padding: 16px 20px;
  margin-bottom: 24px;
  border-radius: 4px;
}

.treatment-principle h4 {
  font-size: 14px;
  color: #3C5A78;
  margin: 0 0 8px 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.treatment-principle p {
  font-size: 16px;
  color: #1E2227;
  margin: 0;
  line-height: 1.6;
}

.clinical-section,
.evidence-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #E7E3DA;
}

.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.section-heading h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 2px 0 0;
  font-size: 17px;
  color: #1E2227;
}

.section-kicker {
  display: block;
  font-size: 12px;
  color: #6B7077;
  font-weight: 600;
}

.evidence-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  border: 1px solid #DCE4DE;
  border-radius: 6px;
  overflow: hidden;
}

.evidence-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  min-width: 0;
  padding: 12px 14px;
  background: #F7FAF7;
  border-bottom: 1px solid #E2E8E3;
}

.evidence-item:nth-child(odd) {
  border-right: 1px solid #E2E8E3;
}

.evidence-item .el-icon {
  flex: 0 0 auto;
  margin-top: 3px;
  color: #427052;
}

.evidence-item div {
  display: flex;
  flex-direction: column;
  min-width: 0;
  gap: 3px;
}

.evidence-item strong {
  font-size: 13px;
  color: #2C4936;
}

.evidence-item span {
  font-size: 13px;
  line-height: 1.55;
  color: #45534A;
  overflow-wrap: anywhere;
}

.missing-evidence {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 12px 14px;
  background: #FFF8EA;
  border-left: 3px solid #B98328;
  font-size: 13px;
  line-height: 1.6;
}

.missing-evidence strong {
  color: #7B551B;
}

.missing-evidence span {
  color: #664F2C;
}

.original-knowledge {
  margin-top: 20px;
  padding: 18px;
  background: #F8FAFC;
  border: 1px solid #DCE4EE;
  border-left: 3px solid #607D9A;
}

.knowledge-basis {
  margin: 0 0 14px;
  color: #2D3D4A;
  font-size: 14px;
  line-height: 1.75;
}

.knowledge-detail-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.knowledge-detail-grid > div {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
  padding: 10px 12px;
  background: #FFFFFF;
  border: 1px solid #E1E7EE;
}

.knowledge-detail-grid label,
.knowledge-points strong {
  color: #607D9A;
  font-size: 12px;
  font-weight: 600;
}

.knowledge-detail-grid span {
  color: #44515D;
  font-size: 13px;
  line-height: 1.6;
  overflow-wrap: anywhere;
}

.knowledge-points {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #E1E7EE;
}

.knowledge-points ul {
  margin: 6px 0 0;
  padding-left: 18px;
  color: #55636F;
  font-size: 13px;
  line-height: 1.7;
}

.knowledge-source {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  margin-top: 14px;
  color: #788692;
  font-size: 12px;
}

.clinical-assessment {
  margin-top: 16px;
  padding: 14px;
  border: 1px solid #DCE4DE;
  border-radius: 6px;
  background: #FBFCFA;
}

.assessment-heading {
  font-weight: 600;
  margin-bottom: 10px;
  color: #2E4760;
}

.assessment-block {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 8px;
  margin-top: 8px;
  line-height: 1.6;
}

.assessment-block.warning { color: #8A5A00; }
.assessment-block.danger { color: #9B2C2C; }

.differential-section,
.acupuncture-section,
.surgical-section {
  margin-top: 16px;
  padding: 14px;
  border: 1px solid #DCE4DE;
  border-radius: 6px;
  background: #FBFCFA;
}

.differential-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 10px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #E5E9E4;
  line-height: 1.6;
}
.differential-item:last-child { border-bottom: none; padding-bottom: 0; }
.differential-item.critical { background: #FDF2F2; padding: 8px; border-radius: 4px; }
.differential-item .course-note { color: #5B6B7A; font-size: 12px; }

.prescription-notice,
.no-prescription-alert {
  margin-bottom: 16px;
}

.recommended-formulas h4,
.modifications h4 {
  font-size: 15px;
  color: #1E2227;
  margin: 0 0 16px 0;
  font-weight: 600;
}

.formula-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 24px;
}

.formula-card {
  background: #F7F5F1;
  border: 1px solid #E7E3DA;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s;
}

.formula-card.priority-1 {
  background: #FFFFFF;
  border: 2px solid #3C5A78;
  box-shadow: 0 4px 16px rgba(60, 90, 120, 0.12);
}

.formula-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}

.formula-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 2px solid #E7E3DA;
}

.formula-card.priority-1 .formula-header {
  border-bottom-color: #3C5A78;
}

.formula-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.star-icon {
  color: #3C5A78;
  font-size: 20px;
}

.formula-name {
  font-family: 'Playfair Display', serif;
  font-size: 20px;
  font-weight: 600;
  color: #1E2227;
}

.formula-card.priority-1 .formula-name {
  color: #3C5A78;
}

.formula-composition {
  margin-bottom: 14px;
}

.formula-composition label,
.formula-function label,
.formula-indications label,
.formula-usage label,
.formula-modifications label,
.formula-contraindications label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #3C5A78;
  margin-bottom: 8px;
}

.herb-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  line-height: 1.8;
}

.herb-chip {
  display: inline-block;
  background: #FFFFFF;
  border: 1px solid #E7E3DA;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 13px;
  color: #1E2227;
  font-weight: 500;
}

.herb-note {
  font-size: 11px;
  color: #6B7077;
  font-weight: 400;
}

.composition-text {
  font-size: 14px;
  color: #1E2227;
  line-height: 1.6;
}

.formula-function,
.formula-indications,
.formula-usage {
  margin-bottom: 14px;
}

.formula-function span,
.formula-indications span,
.formula-usage span {
  font-size: 14px;
  color: #1E2227;
  line-height: 1.6;
}

.formula-contraindications {
  margin-bottom: 14px;
  padding: 10px 12px;
  background: #FFF4F2;
  border-left: 3px solid #B8584D;
  color: #7F3029;
  font-size: 13px;
  line-height: 1.6;
}

.formula-modifications {
  margin-bottom: 14px;
}

.modifications-text {
  font-size: 13px;
  color: #1E2227;
  line-height: 1.7;
  background: #FFFFFF;
  border-left: 3px solid #3C5A78;
  padding: 10px 14px;
  border-radius: 4px;
}

.formula-notes {
  margin-bottom: 14px;
}

.formula-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #E7E3DA;
}

.modification-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.modification-item {
  background: #F7F5F1;
  border-radius: 8px;
  padding: 16px;
}

.modification-condition { flex-wrap: wrap;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-weight: 500;
  color: #1E2227;
}

.modification-action {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.action-label {
  font-size: 13px;
  color: #6B7077;
  font-weight: 500;
}

.herb-tag {
  font-size: 13px;
}

.external-treatments {
  margin-top: 24px;
}

.external-treatments > h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  color: #1E2227;
  margin: 0 0 16px 0;
  font-weight: 600;
}

.zhou-tag {
  margin-left: 8px;
  font-size: 11px;
  background: #F7F5F1;
  border: 1px solid #3C5A78;
  color: #3C5A78;
}

.treatment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.treatment-card {
  background: #F7F5F1;
  border: 1px solid #E7E3DA;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.treatment-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
  border-color: #3C5A78;
}

.treatment-header { flex-wrap: wrap; gap: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid #E7E3DA;
}

.treatment-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.treatment-icon {
  font-size: 18px;
  color: #3C5A78;
}

.treatment-name {
  font-size: 15px;
  font-weight: 600;
  color: #1E2227;
}

.treatment-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

.treatment-body > div {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.treatment-composition .herb-chips.compact {
  margin-top: 4px;
  gap: 5px;
}

.treatment-composition .herb-chip {
  padding: 4px 8px;
  font-size: 12px;
}

.treatment-contraindications {
  padding: 9px 10px;
  background: #FFF4F2;
  border-left: 3px solid #B8584D;
}

.treatment-contraindications label,
.treatment-precautions label {
  color: #9B4037;
}

.treatment-body label {
  font-size: 12px;
  color: #6B7077;
  font-weight: 500;
}

.treatment-body span {
  font-size: 13px;
  color: #1E2227;
  line-height: 1.5;
}

.treatment-function label {
  color: #3C5A78;
}

.treatment-notes {
  margin-top: 4px;
}

.treatment-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
  border-top: 1px solid #E7E3DA;
}

.procedures-section {
  margin-top: 16px;
}

.procedure-block {
  padding: 12px 0;
  border-bottom: 1px dashed #E7E3DA;
}
.procedure-block:last-child {
  border-bottom: none;
}

.procedure-name {
  margin: 0 0 8px;
  font-size: 15px;
  color: #2E4760;
}

.procedure-meta {
  margin: 4px 0;
  font-size: 13px;
  color: #333;
  line-height: 1.6;
}
.procedure-meta label {
  color: #6B7077;
}

.table-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; }
@media (max-width: 768px) { .point-table { min-width: 420px; } }
.point-table {
  width: 100%;
  border-collapse: collapse;
  margin: 8px 0;
  font-size: 13px;
}
.point-table th,
.point-table td {
  border: 1px solid #E7E3DA;
  padding: 6px 10px;
  text-align: left;
  vertical-align: top;
  line-height: 1.6;
}
.point-table th {
  background: #F5F7FA;
  color: #5B6B7A;
  font-weight: 600;
}
.role-tag {
  margin-left: 6px;
}

.procedure-points {
  margin: 4px 0;
  padding-left: 18px;
}
.procedure-points li {
  line-height: 1.7;
  color: #333;
}

.source-line {
  margin: 6px 0 0;
  font-size: 12px;
  color: #909399;
}

.other-syndromes {
  background: #FFFFFF;
  border: 1px solid #E7E3DA;
  border-radius: 12px;
  padding: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1E2227;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.syndrome-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.other-syndrome-card {
  background: #F7F5F1;
  border: 1px solid #E7E3DA;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s;
}

.other-syndrome-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.syndrome-name-small {
  font-size: 15px;
  font-weight: 600;
  color: #1E2227;
}

.treatment-principle-small {
  font-size: 13px;
  color: #6B7077;
  margin: 0;
  line-height: 1.5;
}

.result-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  padding-top: 16px;
}

.treatment-plan {
  margin-top: 20px;
  padding: 16px;
  background: #f8fafc;
  border: 1px solid #dbe4ee;
  border-radius: 8px;
}

.plan-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-top: 14px;
}

.plan-grid section {
  padding: 12px;
  background: #fff;
  border-left: 3px solid #6b8e9e;
}

.plan-grid .risk-section {
  border-left-color: #c45656;
}

.plan-grid h4 {
  margin: 0 0 8px;
  color: #2d3d4a;
}

.plan-grid p,
.plan-grid ul {
  margin: 0;
  color: #596773;
  line-height: 1.7;
  font-size: 13px;
}

.plan-grid ul {
  padding-left: 18px;
}

.treatment-plan small {
  display: block;
  margin-top: 14px;
  color: #788692;
}

@media (max-width: 768px) {
  .syndrome-meta {
    flex-direction: column;
    gap: 16px;
  }

  .formula-card {
    padding: 16px;
  }

  .formula-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .formula-title {
    flex-wrap: wrap;
  }

  .herb-chips {
    gap: 6px;
  }

  .herb-chip {
    font-size: 12px;
    padding: 5px 10px;
  }

  .result-actions {
    flex-direction: column;
  }

  .result-actions .el-button {
    width: 100%;
  }

  .syndrome-cards {
    grid-template-columns: 1fr;
  }

  .treatment-grid {
    grid-template-columns: 1fr;
  }

  .plan-grid {
    grid-template-columns: 1fr;
  }

  .section-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .evidence-list {
    grid-template-columns: 1fr;
  }

  .evidence-item:nth-child(odd) {
    border-right: 0;
  }

  .knowledge-detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
