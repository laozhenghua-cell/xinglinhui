<template>
  <div class="xl-page cd-page">
    <div class="xl-page-title">
      <h2>就诊详情</h2>
      <div>
        <el-button @click="router.push('/clinic')">返回列表</el-button>
        <el-button type="primary" plain @click="router.push('/clinic/new')">再建一例</el-button>
        <el-button type="success" @click="openPdf">🖨 打印/下载处方 PDF</el-button>
      </div>
    </div>

    <template v-if="v">
      <div class="xl-card">
        <div class="pat-head">
          <span class="pat-name">{{ v.patient_name }}</span>
          <el-tag :type="TAG[v.specialty]">{{ SPEC[v.specialty] }}</el-tag>
          <span class="pat-meta">{{ v.gender || '—' }} · {{ v.age ?? '—' }} 岁 · {{ fmtTime(v.created_at) }}</span>
        </div>
        <div class="complaint"><b>主诉:</b>{{ v.chief_complaint || '—' }}</div>
      </div>

      <el-row :gutter="14">
        <el-col :span="12">
          <div class="xl-card">
            <h3>四诊</h3>
            <div class="kv" v-if="(v.four_diagnosis?.symptoms || []).length"><b>症状:</b>
              <el-tag v-for="s in v.four_diagnosis.symptoms" :key="s" size="small" type="info" style="margin:0 4px 4px 0">{{ s }}</el-tag>
            </div>
            <div class="kv"><b>舌象:</b>{{ v.four_diagnosis?.tongue || '—' }}</div>
            <div class="kv"><b>脉象:</b>{{ v.four_diagnosis?.pulse || '—' }}</div>
            <div class="kv"><b>局部:</b>{{ v.four_diagnosis?.local || '—' }}</div>
            <div class="kv"><b>全身:</b>{{ v.four_diagnosis?.systemic || '—' }}</div>
            <div class="kv" v-if="v.four_diagnosis?.detail"><b>描述:</b>{{ v.four_diagnosis.detail }}</div>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="xl-card">
            <h3>辨证</h3>
            <div v-if="!v.dx_result || (!v.dx_result.syndromes?.length && !v.dx_result.ai)" class="xl-empty">未做辨证</div>
            <div v-for="s in v.dx_result?.syndromes || []" :key="s.id" class="kv"><b>{{ s.name }}</b><span class="muted">(匹配 {{ s.score }})</span></div>
            <div v-for="d in v.dx_result?.diseases || []" :key="d.id" class="kv"><b>{{ d.name }}</b><span class="muted">({{ SPEC[d.module] || d.module }})</span></div>
            <div v-if="v.dx_result?.ai" class="ai-box">
              <div><b>证型分析:</b>{{ v.dx_result.ai.syndrome_analysis }}</div>
              <div><b>方剂建议:</b>{{ v.dx_result.ai.formula_suggestion }}</div>
              <div><b>注意事项:</b>{{ v.dx_result.ai.precautions }}</div>
            </div>
          </div>
        </el-col>
      </el-row>

      <div class="xl-card">
        <h3>处方与医嘱 <el-button link type="primary" size="small" @click="editing = !editing">{{ editing ? '完成' : '编辑' }}</el-button></h3>
        <template v-if="editing">
          <el-form label-position="top">
            <el-form-item label="方剂(逗号分隔)">
              <el-input v-model="editRx.formulasText" placeholder="如:仙方活命饮,五味消毒饮" />
            </el-form-item>
            <el-form-item label="加减化裁"><el-input v-model="editRx.modification" type="textarea" :rows="2" /></el-form-item>
            <el-form-item label="外治法"><el-input v-model="editRx.external" type="textarea" :rows="2" /></el-form-item>
            <el-form-item label="医嘱/调护"><el-input v-model="editRx.advice" type="textarea" :rows="2" /></el-form-item>
            <el-form-item label="复诊日期">
              <el-date-picker v-model="editRx.followupDate" type="date" value-format="YYYY-MM-DD" placeholder="选择复诊日期" style="width:200px" />
            </el-form-item>
            <el-form-item label="随访备注">
              <el-input v-model="editRx.followup" placeholder="如:初诊后疼痛减轻,续服三剂" />
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="editRx.followupDone">已复诊(不再提醒)</el-checkbox>
            </el-form-item>
            <el-button type="primary" @click="saveEdit">保存</el-button>
          </el-form>
        </template>
        <template v-else>
          <div class="kv" v-if="rxList.length"><b>方剂:</b>
            <el-tag v-for="f in rxList" :key="f" size="small" type="success" style="margin:0 6px 4px 0" @click="router.push('/kb/formulas?q=' + encodeURIComponent(f))">{{ f }}</el-tag>
          </div>
          <div class="kv" v-else><b>方剂:</b>—</div>
          <div class="kv"><b>加减:</b>{{ v.prescription?.modification || '—' }}</div>
          <div class="kv"><b>外治:</b>{{ v.prescription?.external || '—' }}</div>
          <div class="kv"><b>医嘱:</b>{{ v.prescription?.advice || '—' }}</div>
          <div class="kv"><b>随访:</b>{{ v.followup?.note || '—' }}<span v-if="v.followup?.followup_date" class="muted">复诊 {{ v.followup.followup_date }}</span></div>
        </template>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { clinicVisit, updateVisit, visitPdfUrl } from '@/api/clinic'

const route = useRoute()
const router = useRouter()
const SPEC = { surgery: '外科疮疡', anorectal: '肛肠痔漏', pediatrics: '儿科', alchemy: '丹药研究' }
const TAG = { surgery: 'danger', anorectal: 'warning', pediatrics: 'success', alchemy: 'info' }
const v = ref(null)
const editing = ref(false)
const editRx = reactive({ formulasText: '', modification: '', external: '', advice: '', followup: '', followupDate: '', followupDone: false })

const rxList = computed(() => v.value?.prescription?.formulas || [])

onMounted(async () => {
  v.value = await clinicVisit(route.params.id)
  const rx = v.value.prescription || {}
  editRx.formulasText = (rx.formulas || []).join(',')
  editRx.modification = rx.modification || ''
  editRx.external = rx.external || ''
  editRx.advice = rx.advice || ''
  editRx.followup = v.value.followup?.note || ''
  editRx.followupDate = v.value.followup?.followup_date || ''
  editRx.followupDone = !!v.value.followup?.done
})
async function saveEdit() {
  const rx = {
    formulas: editRx.formulasText.split(/[,、]/).map(s => s.trim()).filter(Boolean),
    modification: editRx.modification, external: editRx.external, advice: editRx.advice,
  }
  await updateVisit(route.params.id, { prescription: rx, followup: { note: editRx.followup, followup_date: editRx.followupDate || undefined, done: editRx.followupDone } })
  v.value = await clinicVisit(route.params.id)
  editing.value = false
  ElMessage.success('已保存')
}
const fmtTime = (t) => (t ? String(t).replace('T', ' ').slice(0, 16) : '')
function openPdf() {
  window.open(visitPdfUrl(route.params.id), '_blank')
}
</script>

<style scoped>
.cd-page .xl-card { margin-bottom: 14px; }
.pat-head { flex-wrap: wrap; display: flex; align-items: center; gap: 10px; }
.pat-name { font-family: "Songti SC", serif; font-size: 20px; font-weight: 700; color: var(--xl-ink); }
.pat-meta { color: #8A94A0; font-size: 13px; }
.complaint { margin-top: 8px; }
.kv { margin: 6px 0; font-size: 13.5px; }
.kv b { color: var(--xl-ink); margin-right: 4px; }
.muted { color: #8A94A0; font-size: 12px; margin-left: 6px; }
.ai-box { background: var(--xl-mint); border-radius: 8px; padding: 10px 12px; margin-top: 8px; font-size: 13px; }
.ai-box div { margin: 4px 0; }
</style>
